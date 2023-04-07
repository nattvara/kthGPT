import styles from './questions.less';
import { Row, Col, Button, Skeleton, Result } from 'antd';
import { useMutation } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import apiClient, { ServerErrorResponse, ServerResponse } from '@/http';
import { history } from 'umi';
import Preview from '@/components/lecture/preview/preview';
import { Lecture } from '@/types/lecture';
import { emitEvent, CATEGORY_QUESTIONS, EVENT_ERROR_RESPONSE } from '@/matomo';
import Frame from '@/components/page/frame/frame';
import { useParams } from 'umi';
import { registerPageLoad } from '@/matomo';
import LectureQuestion from '@/components/lecture/lecture-question/lecture-question';
import CourseTagger from '@/components/course/course-tagger/course-tagger';

interface LectureResponse extends ServerResponse {
  data: Lecture;
}

export default function QuestionsPage() {
  const { id, language } = useParams();

  const [lecture, setLecture] = useState<Lecture | null>(null);
  const [notFound, setNotFound] = useState<boolean | null>(null);

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
        emitEvent(CATEGORY_QUESTIONS, EVENT_ERROR_RESPONSE, 'fetchLecture');
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
      title: 'Unknown',
    });
  } else {
    breadcrumbs.push({
      title: lecture.title !== null ? lecture.title : 'Unknown lecture',
    });
  }
  breadcrumbs.push({
    title: 'Questions',
  });

  useEffect(() => {
    registerPageLoad();
    fetchLecture();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (lecture && lecture.title) {
      document.title = `kthGPT - ${lecture.title}`;
    }
  }, [lecture]);

  let smLeft;
  let smRight;
  let mdLeft;
  let mdRight;
  let lgLeft;
  let lgRight;
  if (lecture !== null && lecture.courses_can_change) {
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
        <Frame showBack={true} breadcrumbs={breadcrumbs}>
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
        </Frame>
      </>
    );
  }

  // Loading
  if (lecture === null) {
    return (
      <>
        <Frame showBack={true} breadcrumbs={breadcrumbs}>
          <Skeleton active paragraph={{ rows: 4 }} />
        </Frame>
      </>
    );
  }

  return (
    <>
      <Frame showBack={true} breadcrumbs={breadcrumbs}>
        <>
          <Row>
            <Col sm={smLeft} md={mdLeft} lg={lgLeft}>
              <LectureQuestion lecture={lecture} />
            </Col>
            <Col sm={smRight} md={mdRight} lg={lgRight}>
              <div className={styles.preview_container}>
                {lecture.courses_can_change && (
                  <Row>
                    <CourseTagger
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
      </Frame>
    </>
  );
}
