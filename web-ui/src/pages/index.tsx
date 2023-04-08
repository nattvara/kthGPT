import { Lecture } from '@/types/lecture';
import Frame from '@/components/page/frame/frame';
import SearchHuge from '@/components/searching/search-huge/search-huge';
import { registerPageLoad } from '@/matomo';
import { Col, Row } from 'antd';
import styles from './index.less';
import { useEffect, useState } from 'react';
import SearchResult from '@/components/searching/search-results/search-result';
import HugeButton from '@/components/buttons/huge-button/huge-button';
import { FileSearchOutlined, VideoCameraAddOutlined } from '@ant-design/icons';
import HugePreviewButton from '@/components/buttons/huge-preview-button/huge-preview-button';
import CourseList from '@/components/course/course-list/course-list';
import ImageUpload from '@/components/image/image-upload/image-upload';
import { Image } from '@/types/search';
import { history } from 'umi';

export default function IndexPage() {
  const [lectures, setLectures] = useState<Lecture[]>([]);
  const [hasSearched, setHasSearched] = useState<boolean>(false);

  const foundLectures = (lectures: Lecture[]) => {
    setLectures(lectures);
  };

  const onImageUploadComplete = (image: Image) => {
    history.push(`/assignments/${image.id}`);
  };

  useEffect(() => {
    registerPageLoad();
  }, []);

  return (
    <>
      <Frame>
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
                <ImageUpload
                  onUploadComplete={(image) => onImageUploadComplete(image)}
                />
              </Col>
              <Col sm={24} md={8}>
                <HugePreviewButton
                  icon={<FileSearchOutlined />}
                  title="Find a lecture"
                  subtitle="Find a lecture from the lectures kthGPT has already watched"
                  url="/courses"
                  preview={
                    <CourseList onCourseSelect={() => null} small={true} />
                  }
                />
              </Col>
              <Col sm={24} md={8}>
                <HugeButton
                  icon={<VideoCameraAddOutlined />}
                  title="Add a new lecture"
                  subtitle="It usually takes between 5 and 15 minutes"
                  url="/lectures/add"
                />
              </Col>
            </Row>
          )}
        </Row>
      </Frame>
    </>
  );
}
