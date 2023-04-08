import { ReloadOutlined } from '@ant-design/icons';
import styles from './lecture-question.less';
import { Row, Col, Button, Skeleton, Result } from 'antd';
import { useMutation } from '@tanstack/react-query';
import { useState } from 'react';
import apiClient, { ServerErrorResponse, ServerResponse } from '@/http';
import { Lecture } from '@/types/lecture';
import {
  emitEvent,
  EVENT_ASKED_QUESTION,
  EVENT_ASKED_QUESTION_NO_CACHE,
  ACTION_NONE,
  CATEGORY_QUESTIONS,
  EVENT_RECEIVED_QUESTION_ANSWER,
  EVENT_ERROR_RESPONSE,
} from '@/matomo';
import QuestionInput from '@/components/input/question-input/question-input';
import LectureTranscript from '../lecture-transcript-modal/lecture-transcript-modal';
import { SearchResultLoading } from '@/components/searching/search-result-loading/search-result-loading';

const examples = [
  {
    titleEn: 'Summarize the lecture for me',
    titleSv: 'Sammanfatta föreläsningen för mig',
    queryStringEn: 'Summarize the lecture for me into 10 bullets',
    queryStringSv: 'Sammanfatta denna föreläsning i 10 punkter',
  },
  {
    titleEn: 'Tell me the core concepts covered in the lecture',
    titleSv: 'Berätta om kärnbegreppen i föreläsningen',
    queryStringEn:
      'Tell me the core concepts covered in the lecture and give some explanations for each',
    queryStringSv:
      'Förklara kärnbegreppen i denna föreläsning, med några användbara exempel',
  },
  {
    titleEn: `I didn't go to the lecture, what have i missed?`,
    titleSv: 'Jag gick inte på föreläsningen, vad har jag missat?',
    queryStringEn: `If i didn't attend this lecture what would I have to read-up on?`,
    queryStringSv:
      'Om jag inte deltog på den här föreläsningen, vad skulle jag behöva läsa på om?',
  },
  {
    titleEn: 'At which point in the lecture is X covered?',
    titleSv: 'När i föreläsningen berättar föreläsaren om X?',
    queryStringEn: 'At which point in the lecture is X covered?',
    queryStringSv: 'När i föreläsningen berättar föreläsaren om X?',
  },
  {
    titleEn: 'Where in the course literature can I read more about this?',
    titleSv: 'Var i kursboken kan jag läsa mer om detta?',
    queryStringEn:
      'Where in the course book "X" can i read more about the topics from this lecture?',
    queryStringSv:
      'Var i kursboken "X" kan jag läsa mer om innehållet från denna föreläsning?',
  },
  {
    titleEn: 'Tell me a joke about this lecture',
    titleSv: 'Berätta ett skämt om den här föreläsningen',
    queryStringEn: 'Tell me a joke about the contents covered in this lecture',
    queryStringSv: 'Berätta ett skämt om innehållet i den här föreläsningen',
  },
];

interface QueryResponse extends ServerResponse {
  data: {
    response: string;
    cached: boolean;
  };
}

interface LectureQuestionProps {
  lecture: Lecture;
}

export default function LectureQuestion(props: LectureQuestionProps) {
  const { lecture } = props;

  const [queryString, setQueryString] = useState('');
  const [response, setResponse] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [overrideCache, setOverrideCache] = useState<boolean>(false);
  const [wasCached, setWasCached] = useState<boolean>(false);

  const { isLoading: isMakingQuery, mutate: makeQuery } = useMutation(
    async () => {
      setResponse('');
      return await apiClient.post(
        '/query/lecture',
        {
          lecture_id: lecture.public_id,
          language: lecture.language,
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
        emitEvent(
          CATEGORY_QUESTIONS,
          EVENT_RECEIVED_QUESTION_ANSWER,
          ACTION_NONE
        );
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
        emitEvent(CATEGORY_QUESTIONS, EVENT_ERROR_RESPONSE, 'makeQuery');
      },
    }
  );

  const askQuestion = async (q: string) => {
    await setQueryString(q);
    if (isMakingQuery) return;

    makeQuery();

    emitEvent(CATEGORY_QUESTIONS, EVENT_ASKED_QUESTION, queryString);
  };

  const askQuestionWithoutCache = async () => {
    if (isMakingQuery) return;

    await setOverrideCache(true);
    askQuestion(queryString);

    emitEvent(CATEGORY_QUESTIONS, EVENT_ASKED_QUESTION_NO_CACHE, queryString);
  };

  let placeholder = '';
  if (lecture.language === 'en') {
    placeholder = 'Enter a question about the lecture...';
  } else if (lecture.language === 'sv') {
    placeholder = 'Skriv en fråga om föreläsningen...';
  }

  return (
    <>
      <QuestionInput
        language={lecture.language}
        placeholder={placeholder}
        isAsking={isMakingQuery}
        examples={examples}
        huge={true}
        disabled={false}
        onAsk={(queryString: string) => askQuestion(queryString)}
        extraButtons={[<LectureTranscript lecture={lecture} />]}
      />

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

      {isMakingQuery && (
        <Row>
          <Col span={24}>
            <SearchResultLoading size={4} min={1} max={10} />
          </Col>
        </Row>
      )}

      {!isMakingQuery && response !== '' && (
        <Row>
          <Col span={24}>
            <>
              <Row gutter={[20, 20]}>
                <Col span={24}>
                  <pre className={styles.response}>{response}</pre>
                </Col>
              </Row>

              <div className={styles.divider}></div>

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
    </>
  );
}
