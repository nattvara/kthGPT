import styles from './text-math.less';
import 'katex/dist/katex.min.css';
import { InlineMath, BlockMath } from 'react-katex';

function isInline(code: string) {
  const pattern = /\$[^\$]*\$/;
  return pattern.test(code);
}

interface LatexProps {
  code: string;
}

function Latex(props: LatexProps) {
  const { code } = props;

  if (isInline(code)) {
    return (
      <span className={styles.math}>
        <InlineMath math={code.replaceAll('$', '')} />
      </span>
    );
  }

  // replace \[ with \begin{equation}
  let replaced = code.replaceAll('\\[', '\\begin{equation}');
  replaced = replaced.replaceAll('\\]', '\\end{equation}');

  return (
    <span className={`${styles.math} ${styles.block_math}`}>
      <BlockMath math={replaced} />
    </span>
  );
}

interface TextMathProps {
  text: string;
}

export function TextMath(props: TextMathProps) {
  const { text } = props;

  // this regex captures
  // $ signs        -> $singleline_content$
  // \begin blocks  -> \begin{same_tag}multiline_content\end{same_tag}
  // \[ equations   -> \[multiline_content\]
  const regex =
    /\$(.+?)\$|\\begin\{((\s|\S)*?)\}((\s|\S)*?)\\end\{\2\}|\\\[((\s|\S)*?)\\\]/gm;
  const parts = [];
  let lastIndex = 0;
  let match;

  while ((match = regex.exec(text)) !== null) {
    parts.push(text.slice(lastIndex, match.index));
    parts.push(match[0]);
    lastIndex = regex.lastIndex;
  }
  parts.push(text.slice(lastIndex));

  const content = parts.map((part, index) => {
    if (index % 2 === 0) {
      const lines = part.split('\n');
      return lines.map((line, lineIndex) => (
        <span key={`part-${index}-line-${lineIndex}`}>
          <span>{line}</span>
          {lineIndex < lines.length - 1 && <br />}
        </span>
      ));
    } else {
      return <Latex key={index} code={part} />;
    }
  });

  return <div>{content}</div>;
}
