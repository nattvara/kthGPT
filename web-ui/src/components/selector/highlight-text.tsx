import styles from './highlight-text.less';
import { Space, Typography } from 'antd';
import { Highlight } from '@/components/lecture';

const { Paragraph } = Typography;

interface BoldedTextProps {
  text: string;
}

function BoldedText(props: BoldedTextProps) {
  const { text } = props;

  // Split the string based on the <strong> and </strong> tags
  const parts = text.split(/<strong>|<\/strong>/);

  return (
    <>
      {parts.map((str, index) => {
        // If the index is odd, it means the text was inside the <strong> tags and should be bolded
        return index % 2 === 0 ? (
          <span key={index}>{str}</span>
        ) : (
          <strong key={index}>{str}</strong>
        );
      })}
    </>
  );
}

interface HighlightProps {
  highlight: Highlight;
}

export function HighlightText(props: HighlightProps) {
  const { transcript } = props.highlight;

  if (transcript === null) {
    return <></>;
  }

  return (
    <>
      <Space direction="vertical" size="large">
        <Paragraph>
          {transcript.map((highlight) => {
            return (
              <blockquote className={styles.quote}>
                <BoldedText text={highlight}></BoldedText>
              </blockquote>
            );
          })}
        </Paragraph>
      </Space>
    </>
  );
}
