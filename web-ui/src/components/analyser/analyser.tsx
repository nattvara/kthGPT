import {
  FlagOutlined,
  ClockCircleOutlined,
  NumberOutlined,
  BulbOutlined,
} from '@ant-design/icons';
import styles from './analyser.less';
import {
  Row,
  Col,
  Space,
  Alert,
  Card,
  Result,
  Progress,
  Statistic,
  Skeleton,
  Button,
  Tag,
} from 'antd';
import { notification } from 'antd';
import { useMutation } from '@tanstack/react-query';
import { Lecture } from '@/components/lecture';
import { useEffect, useState } from 'react';
import apiClient from '@/http';
import { history } from 'umi';
import Preview from '../preview';

const UPDATE_LECTURE_INTERVAL = 1000;
const UPDATE_QUEUE_INTERVAL = 5000;

interface AnalyserProps {
  id: string
  language: string
}

const prettyLengthString = (seconds: number) => {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);

  return `${hours}h ${minutes}min`;
}

const prettyLanguageString = (slug: string) => {
  if (slug === 'en') return 'English';
  if (slug === 'sv') return 'Swedish';
  return 'Unknown';
}

const prettyTimeElapsedString = (date: Date) => {
  const currentDate = new Date();
  const elapsedTime = currentDate.getTime() - date.getTime();
  let seconds = Math.floor(elapsedTime / 1000);
  const minutes = Math.floor(seconds / 60);
  seconds = seconds % 60;

  if (minutes > 180) {
    return 'long ago...';
  }

  if (minutes > 120) {
    return 'over 2h ago';
  }

  if (minutes > 60) {
    return 'over 1h ago';
  }

  if (seconds < 5) {
    return 'Just now';
  }

  if (minutes === 0) {
    return `${seconds}s ago`;
  }

  return `${minutes}min ${seconds}s ago`;
}

export default function Analyser(props: AnalyserProps) {
  const { id, language } = props;

  const [notificationApi, contextHolder] = notification.useNotification();
  const [lecture, setLecture] = useState<Lecture | null>(null);
  const [lectures, setLectures] = useState<Lecture[]>([]);
  const [notFound, setNotFound] = useState<boolean | null>(null);

  const { mutate: fetchLecture } = useMutation(
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

  const { mutate: fetchLectures } = useMutation(
    async () => {
      return await apiClient.get(`/lectures?summary=true`);
    },
    {
      onSuccess: (res: any) => {
        const result = {
          status: res.status + '-' + res.statusText,
          headers: res.headers,
          data: res.data,
        };
        setLectures(result.data);
      },
      onError: (err: any) => {
        notificationApi['error']({
          message: 'Failed to get lectures',
          description: err.response.data.detail,
        });
      },
    }
  );

  const { isLoading: isPosting, mutate: postUrl } = useMutation(
    async () => {
      return await apiClient.post(`/url`, {
        url: `https://play.kth.se/media/${id}`,
        language,
      });
    },
    {
      onSuccess: (res: any) => {
        const result = {
          status: res.status + '-' + res.statusText,
          headers: res.headers,
          data: res.data,
        };
        notificationApi['success']({
          message: 'Restarted analysis',
          description: 'Hopefully it works this time!',
        });
      },
      onError: (err: any) => {
        notificationApi['error']({
          message: 'Failed restart analysis',
          description: err.response.data.detail,
        });
      },
    }
  );

  const goToQuestions = () => {
    history.push(`/questions/lectures/${id}/${language}`);
  };

  const restart = () => {
    postUrl();
  };

  useEffect(() => {
    fetchLecture();
    fetchLectures();
  }, [id, language]);

  useEffect(() => {
    const interval = setInterval(() => {
      fetchLecture();
    }, UPDATE_LECTURE_INTERVAL);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      fetchLectures();
    }, UPDATE_QUEUE_INTERVAL);

    return () => clearInterval(interval);
  }, []);

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
    );
  }

  if (lecture == null) {
    return <Skeleton active paragraph={{ rows: 4 }} />;
  }

  return (
    <>
      {contextHolder}
      {lecture.analysis?.state === 'ready' &&
        <>
          <Result
            status='success'
            title='Lecture has been successfully analyzed!'
            subTitle='The lecture is ready to be queried with GPT-3'
            extra={[
              <Button
                onClick={() => goToQuestions()}
                type='primary'
                key='btn'
                size='large'>
                Start asking questions
              </Button>,
            ]}
          />
          <div className={styles.divider}></div>
        </>
      }
      {lecture.analysis?.state === 'failure' &&
        <>
          <Result
            status='500'
            title='Something went wrong when analyzing the lecture!'
            subTitle='Unfortunately something must have gone wrong, click the button to try analyzing the video again. Sometimes restarting just fixes things ¯\_(ツ)_/¯'
            extra={[
              <Button
                onClick={() => restart()}
                loading={isPosting}
                type='primary'
                key='btn'
                icon={<BulbOutlined />}
                size='large'>
                Restart
              </Button>,
            ]}
          />
          <div className={styles.divider}></div>
          <div className={styles.divider}></div>
        </>
      }
      {lecture.analysis?.frozen &&
        <>
          <Result
            status='403'
            title='The analysis seems to be stuck!'
            subTitle='Click the button to restart the analysis. Sometimes restarting just fixes things ¯\_(ツ)_/¯'
            extra={[
              <Button
                onClick={() => restart()}
                loading={isPosting}
                type='primary'
                key='btn'
                icon={<BulbOutlined />}
                size='large'>
                Restart
              </Button>,
            ]}
          />
          <div className={styles.divider}></div>
          <div className={styles.divider}></div>
        </>
      }

      <Row gutter={[20, 20]}>
        <Col sm={24} md={12}>
          <Space direction='vertical' size='large'>
            {lecture.analysis?.state !== 'ready' && lecture.analysis?.state !== 'failure' &&
              <Row>
                <Col span={24}>
                  <h1 className={styles.title}>kthGPT is watching the lecture 🍿</h1>
                  <h2 className={styles.subtitle}>This can take a little while, but is only done once per lecture!</h2>
                </Col>
              </Row>
            }
            <Row gutter={[20, 20]} justify='center' align='middle'>
              <Col sm={24} md={24} lg={12}>
                <Preview lecture={lecture}></Preview>
              </Col>
              <Col sm={24} md={24} lg={12}>
                <Row justify='center' align='middle'>
                  <Progress
                    type='circle'
                    percent={lecture.analysis?.overall_progress}
                    className={styles.circle} />
                </Row>
                <Row justify='center' align='middle'>
                  <Col>
                    <h1>Lecture progress</h1>
                  </Col>
                </Row>
              </Col>
            </Row>
            {
              lecture.analysis !== null &&
              lecture.analysis?.last_message !== null &&
              lecture.analysis?.state !== 'ready' &&
              <Row gutter={[20, 10]}>
                <Col>
                  <Tag className={styles.tag} icon={<ClockCircleOutlined />} color='#108ee9'>
                    {prettyTimeElapsedString(new Date(lecture.analysis?.last_message?.timestamp!))}
                  </Tag>
                  <Alert
                    message={
                      <>
                        <Space direction='horizontal' size='small'>
                          <strong>{lecture.analysis?.last_message?.title}</strong>
                          <span>{lecture.analysis?.last_message?.body}</span>
                        </Space>
                      </>
                    }
                    type='info'
                    showIcon
                  />
                </Col>
              </Row>
            }
            <Row gutter={[20, 10]}>
              <Col span={24}>
                Downloading video
                <Progress
                  percent={lecture.analysis?.mp4_progress}
                  showInfo={lecture.analysis?.mp4_progress != 0} />

                Extracting audio
                <Progress
                  percent={lecture.analysis?.mp3_progress}
                  showInfo={lecture.analysis?.mp3_progress != 0} />

                Transcribing lecture
                <Progress
                  percent={lecture.analysis?.transcript_progress}
                  showInfo={lecture.analysis?.transcript_progress != 0} />

                Generating summary
                <Progress
                  percent={lecture.analysis?.summary_progress}
                  showInfo={lecture.analysis?.summary_progress != 0} />
              </Col>
            </Row>

            <Space direction='vertical' size='small'>
              <Row gutter={[20, 10]}>
                {lecture.length !== 0 &&
                  <Col>
                    <Card size='small'>
                      <Statistic
                        title='Length'
                        value={prettyLengthString(lecture.length!)}
                        prefix={<ClockCircleOutlined />}
                      />
                    </Card>
                  </Col>
                }
                {lecture.words !== 0 &&
                  <Col>
                    <Card size='small'>
                      <Statistic
                        title='Number of words'
                        value={lecture.words!}
                        suffix='words'
                        prefix={<NumberOutlined />}
                      />
                    </Card>
                  </Col>
                }
                <Col>
                  <Card size='small'>
                    <Statistic
                      title='Language'
                      value={prettyLanguageString(lecture.language!)}
                      prefix={<FlagOutlined />}
                    />
                  </Card>
                </Col>
              </Row>
            </Space>
          </Space>
        </Col>

        <Col sm={24} md={12}>
          <Card title='Current Queue' className={styles.queue_container}>
            <div className={styles.queue}>
              {lectures.map(lecture =>
                <div style={{width: '95%'}} key={lecture.public_id}>
                  <span>{lecture.content_link}</span>
                  <Progress
                    percent={lecture.overall_progress!}
                    className={styles.previous_lecture}
                    strokeColor='#aaa' />
                </div>
              )}
            </div>
          </Card>
        </Col>
      </Row>

      <div className={styles.divider}></div>
      <div className={styles.divider}></div>
      <div className={styles.divider}></div>
    </>
  );
}
