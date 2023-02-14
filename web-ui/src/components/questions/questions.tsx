import {
  SendOutlined,
  CloseOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import styles from './questions.less';
import {
  Row,
  Col,
  Space,
  Button,
  Skeleton,
  Result,
} from 'antd';
import { notification } from 'antd';
import { useMutation } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import apiClient from '@/http';
import { history } from 'umi';
import TextArea from 'antd/es/input/TextArea';
import Preview from '../preview';
import { Lecture } from '@/components/lecture';

interface QuestionsProps {
  id: string
  language: string
}

const examples = [
  {
    title: 'Summarize the lecture for me',
    queryString: 'Summarize the lecture for me into 10 bullets',
  },
  {
    title: 'Tell me the core concepts covered in the lecture',
    queryString: 'Tell me the core concepts covered in the lecture and give some explanations for each',
  },
  {
    title: 'At which point in the lecture is X covered?',
    queryString: 'At which point in the lecture is X covered?',
  },
  {
    title: 'Tell me a joke about this lecture',
    queryString: 'Tell me a joke about the contents covered in this lecture',
  },
];

const randomInt = (min: number, max: number) => {
  return Math.floor(Math.random() * (max - min + 1)) + min;
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

  const { isLoading: isLoadingLecture, mutate: fetchLecture } = useMutation(
    async () => {
      return await apiClient.get(`/lectures/${id}/${language}`);
    },
    {
      onSuccess: (res: any) => {
        const result = {
          status: res.status + '-' + res.statusText,
          headers: res.headers,
          data: res.data,
        };
        setLecture(result.data);
        setNotFound(false);
      },
      onError: (err: any) => {
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
      return await apiClient.post('/query', {
        lecture_id: id,
        language: language,
        query_string: queryString,
        override_cache: overrideCache,
      });
    },
    {
      onSuccess: (res: any) => {
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
      onError: (err: any) => {
        if (err.response.status === 404) {
          setNotFound(true);
        }
        const data = err.response.data;
        if (data.detail) {
          setError(data.detail);
        } else {
          setError('Something went wrong when communicating with openAI.')
        }
      },
    }
  );

  useEffect(() => {
    fetchLecture();
  }, [id, language]);

  const askQuestion = () => {
    makeQuery();
  };

  const askQuestionWithoutCache = async () => {
    await setOverrideCache(true);
    askQuestion();
  };

  if (notFound === true) {
    return (
      <>
        <Result
          status='404'
          title='Could not find lecture'
          extra={[
            <Button
              onClick={() => history.push('/')}
              type='primary'
              key='btn'
              size='large'>
              Add a lecture here
            </Button>,
          ]}
        />
      </>
    )
  }

  if (lecture == null) {
    return <Skeleton active paragraph={{ rows: 4 }} />;
  }

  return (
    <>
      {contextHolder}
      <Row>
        <Col sm={24} md={15} lg={18}>
          <Space direction='vertical' size='large' style={{width: '100%'}}>
            <Row>
              <Col span={24}>
                <TextArea
                  className={styles.hugeInput}
                  value={queryString}
                  onChange={e => setQueryString(e.target.value)}
                  onPressEnter={() => {}}
                  placeholder='Enter a question...'
                  autoSize={true} />
              </Col>
            </Row>
            <Row gutter={[10, 10]}>
              <Col>
                <Button
                  onClick={() => askQuestion()}
                  loading={isMakingQuery}
                  type='primary'
                  size='large'
                >
                  <SendOutlined /> Ask
                </Button>
              </Col>
              <Col>
                <Button type='default' size='large' onClick={() => history.push('/')}>
                  <CloseOutlined /> Analyse a new lecture
                </Button>
              </Col>

              <Col>
                <Button type='text' size='small' style={{pointerEvents: 'none'}}>
                  Some examples
                </Button>
              </Col>
              {examples.map(example =>
                <Col key={example.title}>
                  <Button
                    type='dashed'
                    size='small'
                    onClick={() => setQueryString(example.queryString)}
                  >
                    {example.title}
                  </Button>
                </Col>
              )}
            </Row>
          </Space>
        </Col>
        <Col sm={24} md={9} lg={6}>
          <div className={styles.preview_container}>
            <Preview lecture={lecture}></Preview>
          </div>
        </Col>
      </Row>
      <Row>
        <Col sm={24} md={15} lg={18}>
          {error !== '' &&
            <>
              <Result
                status='500'
                title='Sorry, something went wrong.'
                subTitle={error}
                extra={
                  <Button
                    onClick={() => askQuestion()}
                    loading={isMakingQuery}
                    type='primary'
                    size='large'
                  >
                    <ReloadOutlined /> Try Again
                  </Button>
                }
              />
            </>
          }
          {isMakingQuery &&
            <>
              <Skeleton active paragraph={{ rows: randomInt(1, 8) }} />
              <Skeleton active paragraph={{ rows: randomInt(6, 10) }} />
              <Skeleton active paragraph={{ rows: randomInt(1, 4) }} />
              <Skeleton active paragraph={{ rows: randomInt(2, 8) }} />
            </>
          }
          {!isMakingQuery && response !== '' &&
            <>
              <pre className={styles.response}>
                {response}
              </pre>

              <div className={styles.divider}></div>

              {wasCached &&
                <Row justify='end' align='middle'>
                  <Button type='text' size='small' style={{pointerEvents: 'none'}}>
                    This response was cached. Click here to override the cache
                  </Button>
                  <Button
                    onClick={() => askQuestionWithoutCache()}
                    loading={isMakingQuery}
                    type='dashed'
                    size='small'
                    icon={<ReloadOutlined />}
                  >
                    New Response
                  </Button>
                </Row>
              }
            </>
          }
        </Col>
      </Row>
      <Row>
        <div className={styles.divider}></div>
        <div className={styles.divider}></div>
        <div className={styles.divider}></div>
      </Row>
    </>
  );
}
