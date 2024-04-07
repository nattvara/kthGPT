import { Lecture } from '@/types/lecture';
import PageFrame from '@/components/page/page-frame/page-frame';
import SearchHuge from '@/components/search/search-huge/search-huge';
import { emitEvent, registerPageLoad } from '@/matomo';
import { Button, Col, Row, Grid, Result } from 'antd';
import styles from './index.less';
import { useEffect, useState } from 'react';
import SearchResult from '@/components/search/search-results/search-result';
import ButtonHuge from '@/components/button/button-huge/button-huge';
import {
  BulbOutlined,
  FileSearchOutlined,
  VideoCameraAddOutlined,
} from '@ant-design/icons';
import ButtonHugeWithPreview from '@/components/button/button-huge-with-preview/button-huge-with-preview';
import apiClient from '@/http';
import CourseList from '@/components/course/course-list/course-list';
import ImageUpload from '@/components/image/image-upload/image-upload';
import { Image } from '@/types/search';
import { history } from 'umi';
import HelpAssignmentExamples from '@/components/help/help-assignment-examples/help-assignment-examples';
import { CATEGORY_PAGE_INDEX, EVENT_RANDOM_ASSIGNMENT } from '@/matomo/events';

const { useBreakpoint } = Grid;

const RANDOM_ASSIGNMENT_SUBJECT = 'Mathematics';

export default function IndexPage() {
  const [lectures, setLectures] = useState<Lecture[]>([]);
  const [hasSearched, setHasSearched] = useState<boolean>(false);
  const screens = useBreakpoint();

  const foundLectures = (lectures: Lecture[]) => {
    setLectures(lectures);
  };

  const onImageUploadComplete = (image: Image) => {
    history.push(`/assignments/${image.id}`);
  };

  const goToRandomAssignment = async () => {
    try {
      const response = await apiClient.get(
        `/assignments/image/random/${RANDOM_ASSIGNMENT_SUBJECT}`
      );
      const id = response.data.id;
      history.push(`/assignments/${id}`);
      emitEvent(CATEGORY_PAGE_INDEX, EVENT_RANDOM_ASSIGNMENT, id);
    } catch (err: unknown) {
      console.error(err);
    }
  };

  useEffect(() => {
    document.title = 'OpenUni.AI';
    registerPageLoad();
  }, []);

  return (
    <>
      <PageFrame>
        <Row className={`${styles.fullwidth} ${styles.alert}`}>
          <Result
            className={styles.fullwidth}
            title="This tool has been paused"
            subTitle="Running this is very expensive, so to fund other tools, most functionality in this tool has been shut off."
          />
        </Row>
        <Row>
          <Row className={styles.fullwidth}>
            <SearchHuge
              className={styles.maxwidth}
              onChange={(hasInput: boolean) => setHasSearched(hasInput)}
              foundLectures={(lectures: Lecture[]) => foundLectures(lectures)}
            ></SearchHuge>
          </Row>

          {hasSearched && (
            <Row className={styles.fullwidth}>
              <SearchResult className={styles.maxwidth} lectures={lectures} />
            </Row>
          )}

          {!hasSearched && (
            <Row className={styles.fullwidth}>
              <Col sm={24} md={8}>
                {screens.md && <HelpAssignmentExamples />}
                <ImageUpload
                  onUploadComplete={(image) => onImageUploadComplete(image)}
                />
                <Row justify="center">
                  <Col>
                    <Button
                      onClick={() => goToRandomAssignment()}
                      type="primary"
                      size="large"
                    >
                      <BulbOutlined /> Test with an example!
                    </Button>
                  </Col>
                </Row>
              </Col>
              <Col sm={24} md={8}>
                <ButtonHugeWithPreview
                  icon={<FileSearchOutlined />}
                  title="Find a lecture"
                  subtitle="Find a lecture from the lectures OpenUni.AI has already watched"
                  url="/courses"
                  preview={
                    <CourseList onCourseSelect={() => null} small={true} />
                  }
                />
              </Col>
              <Col sm={24} md={8}>
                <ButtonHuge
                  icon={<VideoCameraAddOutlined />}
                  title="Add a new lecture"
                  subtitle="It usually takes between 5 and 15 minutes"
                  url="/lectures/add"
                />
              </Col>
            </Row>
          )}
        </Row>
      </PageFrame>
    </>
  );
}
