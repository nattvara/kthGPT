import { Button, Col, Result, Row } from 'antd';
import styles from './image-question.less';
import { Image } from '@/types/search';
import InputQuestion from '@/components/input/input-question/input-question';
import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import apiClient, { ServerErrorResponse, ServerResponse } from '@/http';
import { ReloadOutlined } from '@ant-design/icons';
import { SearchResultLoading } from '@/components/search/search-result-loading/search-result-loading';
import { TextMath } from '@/components/text/text-math/text-math';

interface QueryResponse extends ServerResponse {
  data: {
    response: string;
    cached: boolean;
  };
}

interface ImageQuestionProps {
  image: Image;
}

export default function ImageQuestion(props: ImageQuestionProps) {
  const { image } = props;

  const [queryString, setQueryString] = useState('');
  const [response, setResponse] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [overrideCache, setOverrideCache] = useState<boolean>(false);
  const [wasCached, setWasCached] = useState<boolean>(false);

  const { isLoading: isMakingQuery, mutate: makeQuery } = useMutation(
    async () => {
      setResponse('');
      return await apiClient.post(
        '/query/image',
        {
          image_id: image.id,
          query_string: queryString,
          override_cache: overrideCache,
        },
        {
          timeout: 1000 * 40, // 40s timeout
        }
      );
    },
    {
      onSuccess: (res: QueryResponse) => {
        const result = {
          status: res.status + '-' + res.statusText,
          headers: res.headers,
          data: res.data,
        };
        setError('');
        setResponse(result.data.response);
        setWasCached(result.data.cached);
        setOverrideCache(false);
      },
      onError: (err: ServerErrorResponse) => {
        if (err.code === 'ECONNABORTED') {
          setError('OpenAI took to long to response, try asking again!');
        }
        const data = err.response.data;
        if (data.detail) {
          setError(data.detail);
        } else {
          setError('Something went wrong when communicating with OpenAI.');
        }
      },
    }
  );

  const askQuestion = async (q: string) => {
    await setQueryString(q);
    if (isMakingQuery) return;

    makeQuery();
  };

  const askQuestionWithoutCache = async () => {
    if (isMakingQuery) return;

    await setOverrideCache(true);
    askQuestion(queryString);
  };

  return (
    <div className={styles.container}>
      <Row>
        <InputQuestion
          language={'en'}
          placeholder={'Enter a question about this assignment...'}
          disabled={!image.can_ask_question}
          isAsking={isMakingQuery}
          examples={[
            {
              titleEn: 'Explain this assignment',
              titleSv: '',
              queryStringEn: 'Explain this assignment, what is it testing?',
              queryStringSv: '',
            },
            {
              titleEn: 'High-level how-to',
              titleSv: '',
              queryStringEn: 'How do I solve this assignment?',
              queryStringSv: '',
            },
            {
              titleEn: 'Detailed step-by-step instructions',
              titleSv: '',
              queryStringEn:
                'Give me detailed step-by-step instructions of how to solve this assignment',
              queryStringSv: '',
            },
            {
              titleEn: 'Explain this solution',
              titleSv: '',
              queryStringEn:
                'Consider this solution to an assignment, explain how the solution works in detail. Include step by step instructions',
              queryStringSv: '',
            },
            {
              titleEn: 'How do I solve assignment b?',
              titleSv: '',
              queryStringEn:
                'How do I solve assignment b? Give me theory and step-by-step instructions',
              queryStringSv: '',
            },
            {
              titleEn: 'What does "X" mean?',
              titleSv: '',
              queryStringEn:
                'Explain what "X" mean in the [End/Beginning/Middle] of the assignment?',
              queryStringSv: '',
            },
          ]}
          huge={false}
          onAsk={(queryString: string) => askQuestion(queryString)}
        />
      </Row>

      {error !== '' && (
        <Row>
          <Col span={24}>
            <>
              <Result
                status="500"
                title="Sorry, something went wrong."
                subTitle={error}
                extra={
                  <Button
                    onClick={() => askQuestion(queryString)}
                    loading={isMakingQuery}
                    type="primary"
                    size="large"
                  >
                    <ReloadOutlined /> Try Again
                  </Button>
                }
              />
            </>
          </Col>
        </Row>
      )}

      {isMakingQuery && <SearchResultLoading size={4} min={2} max={3} />}

      {!isMakingQuery && response !== '' && (
        <Row>
          <Col span={24}>
            <>
              <Row gutter={[20, 20]}>
                <Col span={24}>
                  <div className={styles.response}>
                    <TextMath text={response} />
                  </div>
                </Col>
              </Row>

              {wasCached && (
                <Row justify="end" align="middle" gutter={[10, 10]}>
                  <Button
                    type="text"
                    size="small"
                    style={{ pointerEvents: 'none' }}
                  >
                    This response was cached. Click here to override the cache
                  </Button>
                  <Button
                    onClick={() => askQuestionWithoutCache()}
                    loading={isMakingQuery}
                    type="dashed"
                    size="small"
                    icon={<ReloadOutlined />}
                  >
                    New Response
                  </Button>
                </Row>
              )}
            </>
          </Col>
        </Row>
      )}
    </div>
  );
}
