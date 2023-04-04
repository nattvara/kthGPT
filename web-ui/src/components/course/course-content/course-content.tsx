import styles from './course-content.less';
import { Course, Lecture } from '@/types/lecture';
import { Col, Divider, Row, Skeleton, Typography } from 'antd';
import { useEffect, useState } from 'react';
import apiClient, { ServerErrorResponse, ServerResponse } from '@/http';
import LectureList from '@/components/lecture/lecture-list/lecture-list';
import { useMutation } from '@tanstack/react-query';

const { Title } = Typography;

interface CourseResponse {
  data: Course;
}

interface CourseContentProps {
  courseCode: string | null;
}

interface LectureResponse extends ServerResponse {
  data: Lecture[];
}

export default function CourseContent(props: CourseContentProps) {
  const { courseCode } = props;

  const [course, setCourse] = useState<Course | null>(null);
  const [youtubeGroups, setYoutubeGroups] = useState<string[]>([]);
  const [selectedYoutubeGroup, setSelectedYoutubeGroup] = useState<
    string | null
  >(null);

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
        },
      }
    );

  const { isLoading: isLoadingYoutubeGroups, mutate: fetchYoutubeGroups } =
    useMutation(
      async () => {
        return await apiClient.post(`/search/course/${course?.course_code}`, {
          query: '',
          source: 'youtube',
        });
      },
      {
        onSuccess: (res: LectureResponse) => {
          const result = {
            data: res.data,
          };
          const groups = new Set(
            result.data
              .map((lecture) => lecture.group)
              .filter((group) => group !== null)
          );
          setYoutubeGroups(Array.from(groups));
        },
        onError: (err: ServerErrorResponse) => {
          console.error(err);
        },
      }
    );

  useEffect(() => {
    if (courseCode !== null) {
      fetchCourseInfo();
    }
  }, [courseCode]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (course !== null) {
      fetchYoutubeGroups();
    }
  }, [course]); // eslint-disable-line react-hooks/exhaustive-deps

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

      <Row>
        <Col md={12}>
          <Divider orientation="left">KTH Play</Divider>
          <LectureList source="kth" courseCode={course.course_code} />
        </Col>
        <Col md={1}></Col>
        <Col md={11}>
          <Divider orientation="left">Youtube</Divider>
          {isLoadingYoutubeGroups && <Skeleton active></Skeleton>}
          <LectureList source="youtube" courseCode={course.course_code} />
          {/* {!isLoadingYoutubeGroups && (
            <Row>
              <Space direction="horizontal">
                {youtubeGroups.map((group) => (
                  <Col key={group}>
                    <Button type="primary">{group}</Button>
                  </Col>
                ))}
              </Space>
            </Row>
          )} */}
        </Col>
      </Row>
    </div>
  );
}
