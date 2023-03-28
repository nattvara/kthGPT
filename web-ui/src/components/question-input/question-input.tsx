import { SendOutlined } from '@ant-design/icons';
import styles from './question-input.less';
import { Row, Col, Button, Space, Input } from 'antd';
import { useEffect, useState } from 'react';

const { TextArea } = Input;

export interface Example {
  titleEn: string;
  titleSv: string;
  queryStringEn: string;
  queryStringSv: string;
}

interface QuestionInputProps {
  language: string;
  placeholder: string;
  isAsking: boolean;
  huge: boolean;
  examples: Example[];
  onAsk: (queryString: string) => void;
  defaultQueryString?: string;
  extraButtons?: JSX.Element[];
  disabled: boolean;
}

export default function QuestionInput(props: QuestionInputProps) {
  const {
    placeholder,
    onAsk,
    isAsking,
    examples,
    language,
    extraButtons,
    huge,
    defaultQueryString,
    disabled,
  } = props;
  const [queryString, setQueryString] = useState('');

  useEffect(() => {
    if (defaultQueryString) setQueryString(defaultQueryString);
  }, [defaultQueryString, setQueryString]);

  return (
    <>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <Row>
          <Col span={24}>
            <TextArea
              className={`${huge ? styles.hugeInput : styles.normalInput} ${
                disabled ? styles.disabled : ''
              }`}
              value={queryString}
              onChange={(e) => {
                let val = e.target.value;
                val = val.replaceAll('\n', '');
                setQueryString(val);
              }}
              onPressEnter={() => onAsk(queryString)}
              placeholder={placeholder}
              autoSize={true}
            />
          </Col>
        </Row>
        <Row gutter={[10, 10]}>
          <Col>
            <Button
              onClick={() => onAsk(queryString)}
              loading={isAsking}
              disabled={disabled}
              type="primary"
              size="large"
            >
              <SendOutlined /> Ask
            </Button>
          </Col>
          {extraButtons &&
            extraButtons.map((button, index) => {
              return <Col key={index}>{button}</Col>;
            })}
        </Row>
        <Row gutter={[10, 10]}>
          <Col>
            <Button type="text" size="small" style={{ pointerEvents: 'none' }}>
              Some examples
            </Button>
          </Col>
          {examples &&
            examples.map((example) => (
              <Col key={example.titleEn}>
                <Button
                  type="dashed"
                  size="small"
                  onClick={() => {
                    if (language === 'en') {
                      setQueryString(example.queryStringEn);
                    } else if (language === 'sv') {
                      setQueryString(example.queryStringSv);
                    }
                  }}
                >
                  {language === 'en' && example.titleEn}
                  {language === 'sv' && example.titleSv}
                </Button>
              </Col>
            ))}
        </Row>
      </Space>
    </>
  );
}
