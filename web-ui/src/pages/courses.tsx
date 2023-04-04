import styles from './courses.less';
import Frame, { BreadcrumbItem } from '@/components/page/frame/frame';
import { registerPageLoad } from '@/matomo';
import { Col, Row } from 'antd';
import { useEffect, useState } from 'react';
import { history, useParams } from 'umi';
import CourseList from '@/components/course/course-list/course-list';
import { Course } from '@/types/lecture';
import CourseContent from '@/components/course/course-content/course-content';

export default function IndexPage() {
  const { courseCode } = useParams();
  const [selectedCourse, setSelectedCourse] = useState<string | null>(null);
  const [breadcrumbs, setBreadcrumbs] = useState<BreadcrumbItem[]>([]);

  useEffect(() => {
    registerPageLoad();
    if (courseCode !== undefined) {
      setSelectedCourse(courseCode);
      setBreadcrumbs([
        {
          title: 'Browse Courses',
          href: '/courses',
        },
        {
          title: courseCode,
        },
      ]);
    } else {
      setBreadcrumbs([
        {
          title: 'Browse Courses',
        },
      ]);
    }
  }, [courseCode]);

  return (
    <>
      <Frame showBack={true} breadcrumbs={breadcrumbs}>
        <>
          <Row>
            <Col sm={24} md={8}>
              <CourseList
                selectedCourse={selectedCourse}
                onCourseSelect={(course) => {
                  setSelectedCourse(course.course_code);
                  history.replace(`/courses/${course.course_code}`);
                }}
              />
            </Col>
            {selectedCourse !== undefined && (
              <Col sm={24} md={16}>
                <CourseContent courseCode={selectedCourse} />
              </Col>
            )}
          </Row>
        </>
      </Frame>
    </>
  );
}
