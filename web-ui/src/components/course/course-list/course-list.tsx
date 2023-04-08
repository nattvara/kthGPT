import styles from './course-list.less';
import { Course } from '@/types/lecture';
import { Row, Input, Space, Col, Button, Typography } from 'antd';
import { RightOutlined, VideoCameraOutlined } from '@ant-design/icons';
import { useMutation } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import apiClient, { ServerErrorResponse, ServerResponse } from '@/http';
import {
  CATEGORY_COURSE_BROWSER,
  CATEGORY_SELECTOR,
  emitEvent,
  EVENT_ERROR_RESPONSE,
} from '@/matomo';
import { SearchResultLoading } from '@/components/searching/search-result-loading/search-result-loading';

const { Search } = Input;
const { Link } = Typography;

const AUTO_UPDATE_INTERVAL = 10000;

interface CourseResponse extends ServerResponse {
  data: Course[];
}

interface CourseBrowserProps {
  onCourseSelect: (course: Course) => void;
  selectedCourse?: null | string;
  small?: boolean;
}

export default function CourseList(props: CourseBrowserProps) {
  const { onCourseSelect, selectedCourse, small } = props;

  const [firstLoad, setFirstLoad] = useState<boolean>(true);
  const [courseQuery, setCourseQuery] = useState<string>('');
  const [courses, setCourses] = useState<Course[]>([]);
  const [lecturesWithoutCourse, setLecturesWithoutCourse] = useState<number>(0);

  const { isLoading: isSearchingCourses, mutate: doCourseSearch } = useMutation(
    async () => {
      return await apiClient.post(
        '/search/course?include_lectures=true&lecture_count_above_or_equal=1',
        {
          query: courseQuery,
        }
      );
    },
    {
      onSuccess: (res: CourseResponse) => {
        const result = {
          data: res.data,
        };
        result.data.push({
          course_code: 'no_course',
          display_name: 'Untagged Lectures',
          lectures: lecturesWithoutCourse,
        });
        setCourses(result.data);
        setFirstLoad(false);
      },
      onError: (err: ServerErrorResponse) => {
        console.log(err);
        emitEvent(
          CATEGORY_COURSE_BROWSER,
          EVENT_ERROR_RESPONSE,
          'doCourseSearch'
        );
      },
    }
  );

  const fetchStats = async () => {
    try {
      const response = await apiClient.get('/stats');
      await setLecturesWithoutCourse(response.data.lectures_without_courses);
    } catch (err: unknown) {
      console.log(err);
      emitEvent(CATEGORY_SELECTOR, EVENT_ERROR_RESPONSE, 'fetchStats');
    }
  };

  const searchCourses = async (query: string) => {
    await setCourseQuery(query);
    doCourseSearch();
  };

  useEffect(() => {
    searchCourses('');
    fetchStats();
  }, [lecturesWithoutCourse]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    const interval = setInterval(() => {
      doCourseSearch();
    }, AUTO_UPDATE_INTERVAL);

    return () => clearInterval(interval);
  }, [doCourseSearch]);

  return (
    <>
      {small !== true && (
        <Row className={styles.search_bar}>
          <Search
            placeholder="Search for course: Flervariabelanalys, DD2477, SE1020"
            size="large"
            value={courseQuery}
            loading={isSearchingCourses}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
              const val = e.target.value;
              searchCourses(val);
            }}
          />
        </Row>
      )}

      <div className={styles.result_container}>
        {isSearchingCourses && firstLoad && (
          <>
            <SearchResultLoading size={4} min={1} max={100} />
          </>
        )}
        <Space direction="vertical" size="large">
          {courses.map((course) => {
            if (courseQuery !== '' && course.course_code === 'no_course') {
              // hide the no_course course if any search input is entered
              return <div key={course.course_code}></div>;
            }

            return (
              <Row
                key={course.course_code}
                className={`${styles.course} ${
                  selectedCourse === course.course_code ? styles.selected : ''
                }${small === true ? styles.small : ''}`}
                onClick={() => onCourseSelect(course)}
              >
                <Col span={20}>
                  <Row>
                    <Col>
                      {course.course_code !== 'no_course' && (
                        <Link className={styles.course_name}>
                          <strong>{course.course_code}</strong>
                          <span>-</span>
                          <span> </span>
                          {course.display_name}
                        </Link>
                      )}
                      {course.course_code === 'no_course' && (
                        <span className={styles.course_name}>
                          {course.display_name}
                        </span>
                      )}
                    </Col>
                  </Row>
                  <Row className={styles.course_meta}>
                    <Col>
                      <VideoCameraOutlined /> {course.lectures}
                      {course.lectures === 1 && <> Lecture</>}
                      {course.lectures !== null && course.lectures > 1 && (
                        <> Lectures</>
                      )}
                    </Col>
                  </Row>
                </Col>
                <Col span={4}>
                  <Row justify="end">
                    <Button
                      type={
                        selectedCourse === course.course_code
                          ? 'primary'
                          : 'default'
                      }
                      shape="circle"
                      onClick={() => onCourseSelect(course)}
                    >
                      <RightOutlined />
                    </Button>
                  </Row>
                </Col>
              </Row>
            );
          })}
        </Space>
      </div>
    </>
  );
}
