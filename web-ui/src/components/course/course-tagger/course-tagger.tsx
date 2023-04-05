import styles from './course-tagger.less';
import { Lecture, Course } from '@/types/lecture';
import { Button, Row, Typography, Input, Space, Col, notification } from 'antd';
import {
  DeleteOutlined,
  PlusCircleFilled,
  WarningOutlined,
} from '@ant-design/icons';
import { useMutation } from '@tanstack/react-query';
import { useState } from 'react';
import apiClient, { ServerErrorResponse, ServerResponse } from '@/http';
import {
  emitEvent,
  CATEGORY_COURSE_SELECTOR,
  EVENT_ERROR_RESPONSE,
} from '@/matomo';

const { Search } = Input;
const { Title, Paragraph } = Typography;

interface CourseResponse extends ServerResponse {
  data: Course[];
}

interface CourseSearchProps {
  lecture: Lecture;
  onLectureUpdated: (lecture: Lecture) => void;
}

function CourseSearch(props: CourseSearchProps) {
  const { lecture, onLectureUpdated } = props;
  const [query, setQuery] = useState<string>('');
  const [courses, setCourses] = useState<Course[]>([]);
  const { isLoading: isSearching, mutate: doSearch } = useMutation(
    async () => {
      return await apiClient.post('/search/course', {
        query,
        limit: 5,
      });
    },
    {
      onSuccess: (res: CourseResponse) => {
        const result = {
          data: res.data,
        };
        setCourses(result.data);
      },
      onError: (err: ServerErrorResponse) => {
        console.log(err);
        emitEvent(CATEGORY_COURSE_SELECTOR, EVENT_ERROR_RESPONSE, 'doSearch');
      },
    }
  );

  const search = async (query: string) => {
    await setQuery(query);
    doSearch();
  };

  return (
    <>
      <Row className={styles.search_bar_container}>
        <Search
          placeholder="Search for course: Flervariabelanalys, DD2477, SE1020"
          size="large"
          value={query}
          loading={isSearching}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
            const val = e.target.value;
            search(val);
          }}
        />
      </Row>
      <Space direction="vertical" size="large">
        {lecture.courses.map((course) => (
          <div key={course.course_code}>
            <AddedCourse
              course={course}
              lecture={lecture}
              onLectureUpdated={onLectureUpdated}
            />
          </div>
        ))}
        {courses.map((course) => {
          for (let i = 0; i < lecture.courses.length; i++) {
            const c = lecture.courses[i];
            if (c.course_code === course.course_code) return <></>;
          }

          return (
            <div key={course.course_code}>
              <NonAddedCourse
                course={course}
                lecture={lecture}
                onLectureUpdated={onLectureUpdated}
              />
            </div>
          );
        })}
      </Space>
    </>
  );
}

interface NonAddedCourseProps {
  course: Course;
  lecture: Lecture;
  onLectureUpdated: (lecture: Lecture) => void;
}

function NonAddedCourse(props: NonAddedCourseProps) {
  const { lecture, course, onLectureUpdated } = props;
  const [notificationApi, contextHolder] = notification.useNotification();
  const [loading, setLoading] = useState<boolean>(false);

  const addCourse = async (course_code: string) => {
    await setLoading(true);
    try {
      const response = await apiClient.post(
        `/lectures/${lecture.public_id}/${lecture.language}/course`,
        {
          course_code,
        }
      );
      onLectureUpdated(response.data);
      notificationApi['success']({
        message: `Added lecture to ${course_code}`,
      });
    } catch (err: unknown) {
      notificationApi['error']({
        icon: <WarningOutlined />,
        message: 'Course was not added',
        description: (err as ServerErrorResponse).response.data.detail,
      });
      emitEvent(CATEGORY_COURSE_SELECTOR, EVENT_ERROR_RESPONSE, 'addCourse');
    } finally {
      await setLoading(false);
    }
  };

  return (
    <>
      {contextHolder}
      <Row>
        <Space direction="horizontal" size="large">
          <Col>
            <Button
              onClick={() => addCourse(course.course_code)}
              className={styles.course_list_btn}
              type="primary"
              shape="round"
              loading={loading}
              icon={<PlusCircleFilled />}
            >
              Add
            </Button>
          </Col>
          <Col>
            <span className={styles.course_name}>
              <strong>{course.course_code}</strong> - {course.display_name}
            </span>
          </Col>
        </Space>
      </Row>
    </>
  );
}

interface AddedCourseProps {
  course: Course;
  lecture: Lecture;
  onLectureUpdated: (lecture: Lecture) => void;
}

function AddedCourse(props: AddedCourseProps) {
  const { lecture, course, onLectureUpdated } = props;
  const [notificationApi, contextHolder] = notification.useNotification();
  const [loading, setLoading] = useState<boolean>(false);

  const removeCourse = async (course_code: string) => {
    await setLoading(true);
    try {
      const response = await apiClient.delete(
        `/lectures/${lecture.public_id}/${lecture.language}/course/${course_code}`
      );
      onLectureUpdated(response.data);
    } catch (err: unknown) {
      notificationApi['warning']({
        icon: <WarningOutlined />,
        message: 'Course was not removed',
        description: (err as ServerErrorResponse).response.data.detail,
      });
      emitEvent(CATEGORY_COURSE_SELECTOR, EVENT_ERROR_RESPONSE, 'removeCourse');
    } finally {
      await setLoading(false);
    }
  };

  return (
    <>
      {contextHolder}
      <Row>
        <Space direction="horizontal" size="large">
          <Col>
            <Button
              onClick={() => removeCourse(course.course_code)}
              type="default"
              shape="round"
              loading={loading}
              className={styles.course_list_btn}
              icon={<DeleteOutlined />}
            >
              Remove
            </Button>
          </Col>
          <Col>
            <span className={styles.course_name}>
              <strong>{course.course_code}</strong> - {course.display_name}
            </span>
          </Col>
        </Space>
      </Row>
    </>
  );
}

interface CourseTaggerProps {
  lecture: Lecture;
  onLectureUpdated: (lecture: Lecture) => void;
}

export default function CourseTagger(props: CourseTaggerProps) {
  const { lecture, onLectureUpdated } = props;

  return (
    <>
      <Space direction="vertical">
        <Row>
          <Title className={styles.title} level={4} style={{ margin: 0 }}>
            Select which course this lecture belongs to
          </Title>
        </Row>
        <Row>
          <Paragraph>
            Tagging the lecture with courses help others find it. You can add
            more than one course!
          </Paragraph>
        </Row>

        <Row>
          <CourseSearch lecture={lecture} onLectureUpdated={onLectureUpdated} />
        </Row>
      </Space>
    </>
  );
}
