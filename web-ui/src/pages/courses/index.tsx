import PageFrame, {
  BreadcrumbItem,
} from '@/components/page/page-frame/page-frame';
import { registerPageLoad } from '@/matomo';
import { Col, Row, Grid } from 'antd';
import { useEffect, useState } from 'react';
import { useParams } from 'umi';
import CourseList from '@/components/course/course-list/course-list';
import CourseContent from '@/components/course/course-content/course-content';
import { Course } from '@/types/lecture';

const { useBreakpoint } = Grid;

export default function IndexPage() {
  const { courseCode } = useParams();
  const screens = useBreakpoint();

  const [selectedCourse, setSelectedCourse] = useState<string | null>(null);
  const [breadcrumbs, setBreadcrumbs] = useState<BreadcrumbItem[]>([]);

  const selectCourse = (course: Course) => {
    setSelectedCourse(course.course_code);

    setBreadcrumbs([
      {
        title: 'Browse Courses',
        href: '/courses',
      },
      {
        title: course.course_code,
      },
    ]);

    // using the regular history API as
    // the umi router doesn't seem to support
    // rewriting the url without reloading the page
    window.history.pushState(
      {},
      course.course_code,
      `/courses/${course.course_code}`
    );

    document.title = `OpenUni.AI | ${course.course_code}`;
  };

  let shouldShowCourseList = false;
  if (selectedCourse === null) {
    shouldShowCourseList = true;
  } else if (screens.md) {
    shouldShowCourseList = true;
  }

  useEffect(() => {
    registerPageLoad();
    if (courseCode !== undefined) {
      document.title = `OpenUni.AI | ${courseCode}`;
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
      document.title = 'OpenUni.AI | Courses';
      setBreadcrumbs([
        {
          title: 'Browse Courses',
        },
      ]);
    }
  }, [courseCode]);

  return (
    <>
      <PageFrame showBack={true} breadcrumbs={breadcrumbs}>
        <>
          <Row>
            {shouldShowCourseList && (
              <Col sm={24} md={8}>
                <CourseList
                  selectedCourse={selectedCourse}
                  onCourseSelect={(course) => selectCourse(course)}
                />
              </Col>
            )}

            {selectedCourse !== undefined && (
              <Col sm={24} md={shouldShowCourseList ? 16 : 24}>
                <CourseContent courseCode={selectedCourse} />
              </Col>
            )}
          </Row>
        </>
      </PageFrame>
    </>
  );
}
