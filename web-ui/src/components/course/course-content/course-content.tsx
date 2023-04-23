import styles from './course-content.less';
import { Course } from '@/types/lecture';
import { Col, Divider, Row, Skeleton, Typography } from 'antd';
import { useEffect, useState } from 'react';
import apiClient, { ServerErrorResponse } from '@/http';
import LectureList from '@/components/lecture/lecture-list/lecture-list';
import { useMutation } from '@tanstack/react-query';
import { CATEGORY_COURSE_CONTENT, EVENT_ERROR_RESPONSE } from '@/matomo/events';
import { emitEvent } from '@/matomo';

const { Title } = Typography;

interface CourseResponse {
  data: Course;
}

interface CourseContentProps {
  courseCode: string | null;
}

export default function CourseContent(props: CourseContentProps) {
  const { courseCode } = props;

  const [course, setCourse] = useState<Course | null>(null);

  const { isLoading: isLoadingCourseInfo, mutate: fetchCourseInfo } =
    useMutation(
      async () => {
        return await apiClient.get(`/courses/${courseCode}`);
      },
      {
        onSuccess: (res: CourseResponse) => {
          const result = {
            data: res.data,
          };
          setCourse(result.data);
        },
        onError: (err: ServerErrorResponse) => {
          console.error(err);
          emitEvent(
            CATEGORY_COURSE_CONTENT,
            EVENT_ERROR_RESPONSE,
            'fetchCourseInfo'
          );
        },
      }
    );

  useEffect(() => {
    if (courseCode !== null) {
      fetchCourseInfo();
    }
  }, [courseCode]); // eslint-disable-line react-hooks/exhaustive-deps

  if (course === null) {
    return <></>;
  }

  return (
    <div className={styles.course_content}>
      {isLoadingCourseInfo && (
        <Skeleton active paragraph={{ rows: 1 }}></Skeleton>
      )}
      {!isLoadingCourseInfo && (
        <>
          <Row>
            <Title level={2} className={styles.course_code}>
              {course.course_code}
            </Title>
          </Row>
          <Row>
            <Title level={3} className={styles.display_name}>
              {course.display_name}
            </Title>
          </Row>
        </>
      )}

      {/* Separate KTH Play and YouTube videos on desktop */}
      <Row>
        <Col sm={0} md={12}>
          <Divider orientation="left">KTH Play</Divider>
          <LectureList source="kth" courseCode={course.course_code} />
        </Col>
        <Col sm={0} md={1}></Col>
        <Col sm={0} md={11}>
          <Divider orientation="left">Youtube</Divider>
          <LectureList source="youtube" courseCode={course.course_code} />
        </Col>
      </Row>

      {/* Show all sources in one list on mobile */}
      <Row>
        <Col sm={24} md={0}>
          <LectureList courseCode={course.course_code} />
        </Col>
      </Row>
    </div>
  );
}
