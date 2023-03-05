import { SendOutlined, CloseOutlined, ReloadOutlined } from '@ant-design/icons';
import styles from './questions.less';
import { Row, Col, Space, Button, Skeleton, Result } from 'antd';
import { notification } from 'antd';
import { useMutation } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import apiClient, { ServerErrorResponse, ServerResponse } from '@/http';
import { history } from 'umi';
import TextArea from 'antd/es/input/TextArea';
import Preview from '../preview';
import { Lecture } from '@/components/lecture';
import {
  EVENT_ASKED_QUESTION,
  EVENT_ASKED_QUESTION_NO_CACHE,
  emitEvent,
  ACTION_NONE,
  CATEGORY_QUESTIONS,
} from '@/matomo';
import CourseSelector from '../analyser/course-selector';

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

const randomInt = (min: number, max: number) => {
  return Math.floor(Math.random() * (max - min + 1)) + min;
};

interface LectureResponse extends ServerResponse {
  data: Lecture;
}

interface QueryResponse extends ServerResponse {
  data: {
    response: string;
    cached: boolean;
  };
}

interface QuestionsProps {
  id: string;
  language: string;
}

export default function Questions(props: QuestionsProps) {
  const { id, language } = props;
  const [queryString, setQueryString] = useState('');

  const [notificationApi, contextHolder] = notification.useNotification();
  const [lecture, setLecture] = useState<Lecture | null>(null);
  const [response, setResponse] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [notFound, setNotFound] = useState<boolean | null>(null);
  const [overrideCache, setOverrideCache] = useState<boolean>(false);
  const [wasCached, setWasCached] = useState<boolean>(false);

  const { mutate: fetchLecture } = useMutation(
    async () => {
      return await apiClient.get(`/lectures/${id}/${language}`);
    },
    {
      onSuccess: (res: LectureResponse) => {
        const result = {
          status: res.status + '-' + res.statusText,
          headers: res.headers,
          data: res.data,
        };
        setLecture(result.data);
        setNotFound(false);
      },
      onError: (err: ServerErrorResponse) => {
        notificationApi['error']({
          message: 'Failed to get the lecture',
          description: err.response.data.detail,
        });
        if (err.response.status === 404) {
          setNotFound(true);
        }
      },
    }
  );

  const { isLoading: isMakingQuery, mutate: makeQuery } = useMutation(
    async () => {
      setResponse('');
      return await apiClient.post(
        '/query',
        {
          lecture_id: id,
          language: language,
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
        if (err.response.status === 404) {
          setNotFound(true);
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

  useEffect(() => {
    fetchLecture();
  }, [id, language, fetchLecture]);

  useEffect(() => {
    if (lecture === null) return;

    if (lecture.title) {
      document.title = `kthGPT - ${lecture.title}`;
    }
  }, [lecture]);

  const askQuestion = () => {
    if (isMakingQuery) return;

    makeQuery();

    emitEvent(CATEGORY_QUESTIONS, EVENT_ASKED_QUESTION, ACTION_NONE);
  };

  const askQuestionWithoutCache = async () => {
    if (isMakingQuery) return;

    await setOverrideCache(true);
    askQuestion();

    emitEvent(CATEGORY_QUESTIONS, EVENT_ASKED_QUESTION_NO_CACHE, ACTION_NONE);
  };

  if (notFound === true) {
    return (
      <>
        <Result
          status="404"
          title="Could not find lecture"
          extra={[
            <Button
              onClick={() => history.push('/')}
              type="primary"
              key="btn"
              size="large"
            >
              Add a lecture here
            </Button>,
          ]}
        />
      </>
    );
  }

  if (lecture == null) {
    return <Skeleton active paragraph={{ rows: 4 }} />;
  }

  let placeholder = '';
  if (lecture.language === 'en') {
    placeholder = 'Enter a question about the lecture...';
  } else if (lecture.language === 'sv') {
    placeholder = 'Skriv en fråga om föreläsningen...';
  }

  let smLeft;
  let smRight;
  let mdLeft;
  let mdRight;
  let lgLeft;
  let lgRight;
  if (lecture.courses_can_change) {
    smLeft = 24;
    smRight = 24;
    mdLeft = 12;
    mdRight = 12;
    lgLeft = 12;
    lgRight = 12;
  } else {
    smLeft = 24;
    smRight = 24;
    mdLeft = 16;
    mdRight = 8;
    lgLeft = 17;
    lgRight = 7;
  }

  return (
    <>
      {contextHolder}
      <Row>
        <Col sm={smLeft} md={mdLeft} lg={lgLeft}>
          <Space direction="vertical" size="large" style={{ width: '100%' }}>
            <Row>
              <Col span={24}>
                <TextArea
                  className={styles.hugeInput}
                  value={queryString}
                  onChange={(e) => {
                    let val = e.target.value;
                    val = val.replaceAll('\n', '');
                    setQueryString(val);
                  }}
                  onPressEnter={() => askQuestion()}
                  placeholder={placeholder}
                  autoSize={true}
                />
              </Col>
            </Row>
            <Row gutter={[10, 10]}>
              <Col>
                <Button
                  onClick={() => askQuestion()}
                  loading={isMakingQuery}
                  type="primary"
                  size="large"
                >
                  <SendOutlined /> Ask
                </Button>
              </Col>
              <Col>
                <Button
                  type="default"
                  size="large"
                  onClick={() => history.push('/')}
                >
                  <CloseOutlined /> Another lecture
                </Button>
              </Col>

              <Col>
                <Button
                  type="text"
                  size="small"
                  style={{ pointerEvents: 'none' }}
                >
                  Some examples
                </Button>
              </Col>
              {examples.map((example) => (
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
                    {lecture.language === 'en' && example.titleEn}
                    {lecture.language === 'sv' && example.titleSv}
                  </Button>
                </Col>
              ))}
            </Row>
          </Space>
          <Row>
            <Col span={24}>
              {error !== '' && (
                <>
                  <Result
                    status="500"
                    title="Sorry, something went wrong."
                    subTitle={error}
                    extra={
                      <Button
                        onClick={() => askQuestion()}
                        loading={isMakingQuery}
                        type="primary"
                        size="large"
                      >
                        <ReloadOutlined /> Try Again
                      </Button>
                    }
                  />
                </>
              )}
              {isMakingQuery && (
                <>
                  <Skeleton active paragraph={{ rows: randomInt(1, 8) }} />
                  <Skeleton active paragraph={{ rows: randomInt(6, 10) }} />
                  <Skeleton active paragraph={{ rows: randomInt(1, 4) }} />
                  <Skeleton active paragraph={{ rows: randomInt(2, 8) }} />
                </>
              )}
              {!isMakingQuery && response !== '' && (
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
                        This response was cached. Click here to override the
                        cache
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
              )}
            </Col>
          </Row>
          <Row>
            <div className={styles.divider}></div>
            <div className={styles.divider}></div>
            <div className={styles.divider}></div>
          </Row>
        </Col>
        <Col sm={smRight} md={mdRight} lg={lgRight}>
          <div className={styles.preview_container}>
            {lecture.courses_can_change && (
              <Row>
                <CourseSelector
                  lecture={lecture}
                  onLectureUpdated={(lecture) => setLecture(lecture)}
                />
              </Row>
            )}
            <Row>
              <Preview lecture={lecture}></Preview>
            </Row>
          </div>
        </Col>
      </Row>
    </>
  );
}
