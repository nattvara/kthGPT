import styles from './course-browser.less';
import { Course, Lecture } from '@/components/lecture';
import {
  Row,
  Input,
  Space,
  Col,
  Button,
  Typography,
} from 'antd';
import {
  LeftOutlined,
  RightOutlined,
  VideoCameraOutlined
} from '@ant-design/icons';
import { useMutation } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import apiClient from '@/http';
import { history } from 'umi';
import { PreviewCompact } from '../preview';

const { Search } = Input;
const { Link } = Typography;

const AUTO_UPDATE_INTERVAL = 10000;


interface CourseBrowserProps {
  lecturesWithoutCourses: number
}


export default function CourseBrowser(props: CourseBrowserProps) {
  const { lecturesWithoutCourses } = props;

  const [ step, setStep ] = useState<number>(0);
  const [ courseQuery, setCourseQuery ] = useState<string>('');
  const [ lectureQuery, setLectureQuery ] = useState<string>('');
  const [ courses, setCourses ] = useState<Course[]>([]);
  const [ lectures, setLectures ] = useState<Lecture[]>([]);
  const [ selectedCourse, setSelectedCourse ] = useState<string>('');

  const { isLoading: isSearchingCourses, mutate: doCourseSearch } = useMutation(
    async () => {
      return await apiClient.post('/search/course?include_lectures=true&lecture_count_above_or_equal=1', {
        query: courseQuery,
      });
    },
    {
      onSuccess: (res: any) => {
        const result = {
          data: res.data,
        };
        result.data.push({
          course_code: 'no_course',
          display_name: 'Untagged Lectures',
          lectures: lecturesWithoutCourses,
        });
        setCourses(result.data);
      },
      onError: (err: any) => {
        console.log(err);
      },
    }
  );
  const { isLoading: isSearchingLectures, mutate: doLectureSearch } = useMutation(
    async () => {
      return await apiClient.post(`/search/course/${selectedCourse}`, {
        query: lectureQuery,
      });
    },
    {
      onSuccess: (res: any) => {
        const result = {
          data: res.data,
        };
        setLectures(result.data);
      },
      onError: (err: any) => {
        console.log(err);
      },
    }
  );

  const searchCourses = async (query: string) => {
    await setCourseQuery(query);
    doCourseSearch();
  };

  const searchLectures = async (query: string) => {
    await setLectureQuery(query);
    doLectureSearch();
  };

  const goToCourse = async (courseCode: string) => {
    await setStep(1);
    await setSelectedCourse(courseCode);
    searchLectures('');
  };

  useEffect(() => {
    searchCourses('');
  }, [lecturesWithoutCourses]);

  useEffect(() => {
    const interval = setInterval(() => {
      doCourseSearch();
    }, AUTO_UPDATE_INTERVAL);

    return () => clearInterval(interval);
  }, []);

  return (
    <>
      <div className={styles.search_container}>
        <Row className={`${styles.search_inner_container} ${step === 1 ? styles.left : ''}`}>
          <Col span={12}>
            <Row className={styles.search_bar_container}>
              <Search
                placeholder='Search for course: Flervariabelanalys, DD2477, SE1020'
                size='large'
                value={courseQuery}
                loading={isSearchingCourses}
                onChange={e => {
                  let val = e.target.value;
                  searchCourses(val);
                }}
              />
            </Row>
          </Col>
          <Col span={12}>
            <Row className={styles.search_bar_container}>
              <Col xs={10} sm={8} md={10} lg={7} xl={5}>
                <Button
                  size='large'
                  type='primary'
                  onClick={() => {
                    setStep(0);
                    setSelectedCourse('');
                  }}><LeftOutlined /> Back</Button>
              </Col>
              <Col offset={1} xs={13} sm={14} md={13} lg={16} xl={18}>
                <Search
                  style={{width: '100%'}}
                  placeholder='Search for a lecture...'
                  size='large'
                  value={lectureQuery}
                  loading={isSearchingLectures}
                  onChange={e => {
                    let val = e.target.value;
                    searchLectures(val);
                  }}
                />
              </Col>
            </Row>
          </Col>
        </Row>
      </div>

      <div className={styles.result_container}>
        <Row className={`${styles.result_inner_container} ${step === 1 ? styles.left : ''}`}>
          <Col span={12} className={`${styles.content} ${styles.animate_height} ${step === 1 ? styles.collapsed : ''}`}>
            <Space direction='vertical' size='large'>
              {courses.map(course => {
                if (courseQuery !== '' && course.course_code === 'no_course') {
                  // hide the no_course course if any search input is entered
                  return <div key={course.course_code}></div>;
                }

                return (
                  <Row key={course.course_code} className={styles.course} onClick={() => goToCourse(course.course_code)}>
                    <Col span={20}>
                      <Row>
                        <Col>
                          {course.course_code !== 'no_course' &&
                            <Link className={styles.course_name}><strong>{course.course_code}</strong> - {course.display_name}</Link>
                          }
                          {course.course_code === 'no_course' &&
                            <span className={styles.course_name}>{course.display_name}</span>
                          }
                        </Col>
                      </Row>
                      <Row className={styles.course_meta}>
                        <Col>
                          <VideoCameraOutlined /> {course.lectures}
                          {course.lectures === 1 && <> Lecture</>}
                          {course.lectures !== null && course.lectures > 1 && <> Lectures</>}
                        </Col>
                      </Row>
                    </Col>
                    <Col span={4}>
                      <Row justify='end'>
                        <Button
                          type='default'
                          shape='circle'
                          onClick={() => goToCourse(course.course_code)}><RightOutlined /></Button>
                      </Row>
                    </Col>
                  </Row>
                );
              })}
            </Space>
          </Col>
          <Col span={12} className={`${styles.content} ${styles.animate_height} ${step === 0 ? styles.collapsed : ''}`}>
            <Space direction='vertical' size='large'>
              {lectures.map((lecture, index) => {
                return (
                  <Row key={lecture.public_id + lecture.language}>
                    <Col span={2} className={styles.row_number}>
                      {index + 1}
                    </Col>
                    <Col span={22}>
                      <PreviewCompact
                        lecture={lecture}
                        onClick={() => {
                          history.push(`/questions/lectures/${lecture.public_id}/${lecture.language}`)
                        }}
                      />
                    </Col>
                  </Row>
                );
              })}
            </Space>
          </Col>
        </Row>
      </div>
    </>
  );
}
