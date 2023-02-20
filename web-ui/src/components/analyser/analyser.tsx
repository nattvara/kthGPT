import {
  BulbOutlined,
  LoadingOutlined,
  GithubFilled,
} from '@ant-design/icons';
import styles from './analyser.less';
import {
  Row,
  Col,
  Space,
  Card,
  Result,
  Progress,
  Skeleton,
  Button,
  Typography,
} from 'antd';
import { notification } from 'antd';
import { useMutation } from '@tanstack/react-query';
import { Lecture } from '@/components/lecture';
import { useEffect, useState } from 'react';
import apiClient from '@/http';
import { history } from 'umi';
import Preview from '../preview';
import LectureProgress from './lecture-progress';

const { Paragraph } = Typography;

const UPDATE_LECTURE_INTERVAL = 1000;
const UPDATE_QUEUE_INTERVAL = 5000;

interface AnalyserProps {
  id: string
  language: string
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
      return await apiClient.post(`/url/${lecture!.source}`, {
        url: lecture!.content_link,
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

  const openGithubIssues = () => {
    window.open('https://github.com/nattvara/kthGPT/issues', '_blank');
  }

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

  if (lecture.approved === null) {
    return <>
      <Result
        icon={<LoadingOutlined />}
        title='Waiting for the video to be approved'
        subTitle={
          <>
            <Row justify='center'>
              <Col xs={24} sm={12}>
                <Paragraph>
                  Since kthGPT has limited capacity only relevant videos are allowed. kthGPT is currently trying to figure out if the video is relevant. Relevant videos are educational videos, such as recorded lectures, tutorials about math, programming etc.
                </Paragraph>
                <Paragraph>
                  kthGPT will also not watch videos longer than 4 hours.
                </Paragraph>
                <Paragraph>
                  <strong>This can take a few minutes.</strong>
                </Paragraph>
              </Col>
            </Row>
          </>
        }
      />
      <div className={styles.divider}></div>
      <div className={styles.divider}></div>
    </>
  }

  if (lecture.approved === false) {
    return <>
      <Result
        status='error'
        title='The video was denied by kthGPT'
        subTitle={
          <>
            <Row justify='center'>
              <Col xs={24} sm={12} style={{textAlign: 'left'}}>
                <Paragraph>
                  <strong>Since kthGPT has limited capacity only relevant videos are allowed. </strong>
                  kthGPT is using AI to determine which videos are relevant. And this video was denied.
                  There is a few reasons why this could have happened. However, most likely this is because the video was off-topic.
                </Paragraph>
                <Paragraph>
                  Youtube videos should be about a topic that is relevant for a course at KTH, which is the purpose of kthGPT.
                </Paragraph>
                <Paragraph>
                  <strong>If you feel this video should be admitted </strong> please feel free to open an issue on github.
                </Paragraph>
              </Col>
            </Row>
          </>
        }
        extra={[
          <Button
            onClick={() => openGithubIssues()}
            loading={isPosting}
            type='primary'
            key='btn'
            icon={<GithubFilled />}
            size='large'>
            Open an issue
          </Button>
        ]}
      />
      <div className={styles.divider}></div>
      <div className={styles.divider}></div>
    </>
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
            <Row gutter={[20, 20]} justify='start' align='middle'>
              <Col sm={24} md={24} lg={12}>
                <Preview lecture={lecture}></Preview>
              </Col>
            </Row>

            <Row>
              <LectureProgress lecture={lecture} />
            </Row>
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
