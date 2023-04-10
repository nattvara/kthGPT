import styles from './text-math.less';
import 'katex/dist/katex.min.css';
import { InlineMath } from 'react-katex';

interface LatexProps {
  code: string;
}

function Latex(props: LatexProps) {
  const { code } = props;

  return (
    <span className={styles.math}>
      <InlineMath math={code} />
    </span>
  );
}

interface TextMathProps {
  text: string;
}

export function TextMath(props: TextMathProps) {
  const { text } = props;

  const parts = text.split('$');
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
