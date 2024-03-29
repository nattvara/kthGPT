import styles from './watch.less';
import PageFrame from '@/components/page/page-frame/page-frame';
import { emitEvent, registerPageLoad } from '@/matomo';
import { Lecture } from '@/types/lecture';
import { useMutation } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import { useParams } from 'umi';
import apiClient, { ServerErrorResponse, ServerResponse } from '@/http';
import { Button, Col, Result, Row, Skeleton, Space, notification } from 'antd';
import { history } from 'umi';
import LectureWatchResult from '@/components/lecture/lecture-watch-result/lecture-watch-result';
import LecturePreview from '@/components/lecture/lecture-preview/lecture-preview';
import CourseTagger from '@/components/course/course-tagger/course-tagger';
import LectureQueueSummary from '@/components/lecture/lecture-queue-summary/lecture-queue-summary';
import LectureProgress from '@/components/lecture/lecture-progress/lecture-progress';
import {
  ACTION_NONE,
  CATEGORY_PAGE_WATCH,
  EVENT_ERROR_RESPONSE,
  EVENT_RESTART,
} from '@/matomo/events';

const UPDATE_LECTURE_INTERVAL = 1000;

interface LectureResponse extends ServerResponse {
  data: Lecture;
}

interface UrlResponse extends ServerResponse {
  data: {
    uri: string;
    language: string;
  };
}

export default function WatchPage() {
  const { id, language } = useParams();

  const [lecture, setLecture] = useState<Lecture | null>(null);
  const [notFound, setNotFound] = useState<boolean | null>(null);
  const [notificationApi, contextHolder] = notification.useNotification();

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
        if (err.response.status === 404) {
          setNotFound(true);
        }
        emitEvent(CATEGORY_PAGE_WATCH, EVENT_ERROR_RESPONSE, 'fetchLecture');
      },
    }
  );

  const { isLoading: isRestarting, mutate: restart } = useMutation(
    async () => {
      if (lecture === null) {
        throw new Error('lecture was null');
      }

      let contentLink = '';
      if (lecture.content_link !== null) {
        contentLink = lecture.content_link;
      }

      return await apiClient.post(`/url/${lecture.source}`, {
        url: contentLink,
        language,
      });
    },
    {
      onSuccess: (res: UrlResponse) => {
        const result = {
          status: res.status + '-' + res.statusText,
          headers: res.headers,
          data: res.data,
        };
        console.log(result);
        notificationApi['success']({
          message: 'Restarted analysis',
          description: 'Hopefully it works this time!',
        });
        emitEvent(
          CATEGORY_PAGE_WATCH,
          EVENT_RESTART,
          lecture === null ? ACTION_NONE : lecture.public_id
        );
      },
      onError: (err: ServerErrorResponse) => {
        notificationApi['error']({
          message: 'Failed restart analysis',
          description: err.response.data.detail,
        });
        emitEvent(CATEGORY_PAGE_WATCH, EVENT_ERROR_RESPONSE, 'restart');
      },
    }
  );

  const breadcrumbs = [
    {
      title: 'Lectures',
    },
  ];
  if (lecture === null) {
    breadcrumbs.push({
      title: 'Unknown lecture',
    });
  } else {
    breadcrumbs.push({
      title: lecture.title !== null ? lecture.title : 'Unknown lecture',
    });
  }
  breadcrumbs.push({
    title: 'Watch Lecture',
  });

  useEffect(() => {
    registerPageLoad();
    fetchLecture();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    const interval = setInterval(() => {
      fetchLecture();
    }, UPDATE_LECTURE_INTERVAL);

    return () => clearInterval(interval);
  }, [fetchLecture]);

  useEffect(() => {
    if (lecture && lecture.title) {
      document.title = `OpenUni.AI | ${lecture.title}`;
    }
  }, [lecture]);

  if (id === undefined) {
    return <></>;
  }

  if (language === undefined) {
    return <></>;
  }

  // Not found
  if (notFound) {
    return (
      <>
        <PageFrame showBack={true} breadcrumbs={breadcrumbs}>
          <Result
            status="404"
            title="Could not find lecture"
            extra={[
              <Button
                onClick={() => history.push('/add')}
                type="primary"
                key="btn"
                size="large"
              >
                Add a lecture here
              </Button>,
            ]}
          />
        </PageFrame>
      </>
    );
  }

  // Loading
  if (lecture === null) {
    return (
      <>
        <PageFrame showBack={true} breadcrumbs={breadcrumbs}>
          <Skeleton active paragraph={{ rows: 4 }} />
        </PageFrame>
      </>
    );
  }

  if (lecture.approved !== true) {
    return (
      <>
        <PageFrame showBack={true} breadcrumbs={breadcrumbs}>
          <Row>
            <Col span={24}>
              <LectureWatchResult
                lecture={lecture}
                isRestarting={isRestarting}
                restart={() => {
                  restart();
                }}
              />
            </Col>
          </Row>
        </PageFrame>
      </>
    );
  }

  return (
    <>
      {contextHolder}
      <PageFrame showBack={true} breadcrumbs={breadcrumbs}>
        <>
          <Row>
            <Col span={24}>
              <LectureWatchResult
                lecture={lecture}
                isRestarting={isRestarting}
                restart={() => {
                  restart();
                }}
              />
            </Col>
          </Row>
          <Space direction="vertical" size="large">
            {lecture.analysis?.state !== 'ready' &&
              lecture.analysis?.state !== 'failure' && (
                <Row>
                  <Col span={24}>
                    <h1 className={styles.title}>
                      OpenUni.AI is watching the lecture 🍿
                    </h1>
                    <h2 className={styles.subtitle}>
                      This can take a little while, but is only done once per
                      lecture!
                    </h2>
                  </Col>
                </Row>
              )}

            <Row gutter={[20, 20]} justify="start" align="top">
              <Col sm={24} md={12} lg={11}>
                <LecturePreview lecture={lecture}></LecturePreview>
              </Col>
              <Col md={0} lg={2}></Col>
              <Col sm={24} md={12} lg={11}>
                <Space direction="vertical" size="large">
                  <Row>
                    <LectureProgress lecture={lecture} />
                  </Row>
                  <Row>
                    <LectureQueueSummary />
                  </Row>
                  <Row>
                    <CourseTagger
                      lecture={lecture}
                      onLectureUpdated={(lecture) => setLecture(lecture)}
                    />
                  </Row>
                </Space>
              </Col>
            </Row>
          </Space>
        </>
      </PageFrame>
    </>
  );
}
