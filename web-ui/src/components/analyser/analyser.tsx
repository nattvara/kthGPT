import {
  FlagOutlined,
  ClockCircleOutlined,
  NumberOutlined,
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
const GITHUB_URL = 'https://github.com/nattvara/kthGPT';

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

  const goToQuestions = () => {
    history.push(`/questions/lectures/${id}/${language}`);
  };

  const goToGithub = () => {
    window.open(GITHUB_URL, '_blank')
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
      {lecture.state === 'ready' &&
        <>
          <Result
            status='success'
            title='Lecture has been successfully analyzed!'
            subTitle='The lecture is ready to be quired with GPT-3'
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
      {lecture.state === 'failure' &&
        <>
          <Result
            status='500'
            title='Something went wrong when analyzing lecture!'
            subTitle='Unfortunately something must have gone wrong, please contact the maintainer for help.'
            extra={[
              <Button
                onClick={() => goToGithub()}
                danger
                type='primary'
                key='btn'
                size='large'>
                Contact
              </Button>,
            ]}
          />
        </>
      }

      <Row gutter={[20, 20]}>
        <Col sm={24} md={12}>
          <Space direction='vertical' size='large'>
            <Row gutter={[20, 20]} justify='center' align='middle'>
              <Col sm={24} md={24} lg={12}>
                <Preview lecture={lecture}></Preview>
              </Col>
              <Col sm={24} md={24} lg={12}>
                <Progress
                  type='circle'
                  percent={lecture.overall_progress}
                  className={styles.circle} />
              </Col>
            </Row>

            <Row gutter={[20, 10]}>
              <Col span={24}>
                Downloading video
                <Progress
                  percent={lecture.mp4_progress}
                  showInfo={lecture.mp4_progress != 0} />

                Extracting audio
                <Progress
                  percent={lecture.mp3_progress}
                  showInfo={lecture.mp3_progress != 0} />

                Transcribing lecture
                <Progress
                  percent={lecture.transcript_progress}
                  showInfo={lecture.transcript_progress != 0} />

                Generating summary
                <Progress
                  percent={lecture.summary_progress}
                  showInfo={lecture.summary_progress != 0} />
              </Col>
            </Row>

            <Space direction='vertical' size='small'>
              {lecture.state == 'waiting' &&
                <Row gutter={[20, 20]}>
                  <Col span={24}>
                    <Alert
                      message='Lectures before in queue'
                      description='There are other lectures being analyzed before this lecture'
                      type='warning'
                      showIcon
                      />
                  </Col>
                </Row>
              }

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
                    percent={lecture.overall_progress}
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
