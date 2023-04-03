import { Lecture } from '@/types/lecture';
import Frame from '@/components/page/frame/frame';
import SearchHuge from '@/components/searching/search-huge/search-huge';
import { registerPageLoad } from '@/matomo';
import { Col, Row } from 'antd';
import styles from './index.less';
import { useEffect, useState } from 'react';
import SearchResult from '@/components/searching/search-results/search-result';
import HugeButton from '@/components/buttons/huge-button/huge-button';
import { VideoCameraAddOutlined } from '@ant-design/icons';

export default function IndexPage() {
  const [lectures, setLectures] = useState<Lecture[]>([]);
  const [hasSearched, setHasSearched] = useState<boolean>(false);

  const foundLectures = (lectures: Lecture[]) => {
    setLectures(lectures);
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
              <Col md={8}>image search</Col>
              <Col md={8}>browse</Col>
              <Col md={8}>
                <HugeButton
                  icon={<VideoCameraAddOutlined />}
                  title="Add a new lecture"
                  subtitle="It usually takes between 5 and 15 minutes"
                  url="/add"
                />
              </Col>
            </Row>
          )}
        </Row>
      </Frame>
    </>
  );
}
