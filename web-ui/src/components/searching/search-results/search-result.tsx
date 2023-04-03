import styles from './search-result.less';
import { Lecture } from '@/components/lecture';
import { Row, Space, Col } from 'antd';
import { history } from 'umi';
import { emitEvent, CATEGORY_SEARCH_TOOL, EVENT_GOTO_LECTURE } from '@/matomo';
import { PreviewCompact } from '@/components/lecture/preview';
import { HighlightText } from '@/components/selector/highlight-text';

interface SearchResultProps {
  lectures: Lecture[];
  className: string;
}

export default function SearchResult(props: SearchResultProps) {
  const { lectures, className } = props;

  const goToLecture = async (lecture: Lecture, newTab = false) => {
    const url = `/questions/lectures/${lecture.public_id}/${lecture.language}`;

    if (newTab) {
      window.open(url, '_blank');
    } else {
      await history.push(url);
    }

    emitEvent(
      CATEGORY_SEARCH_TOOL,
      EVENT_GOTO_LECTURE,
      `${lecture.public_id}/${lecture.language}`
    );
  };

  return (
    <Row className={`${styles.result} ${className}`}>
      <Space direction="vertical" size="large">
        {lectures.map((lecture, index) => {
          return (
            <Row key={lecture.public_id + lecture.language}>
              <Col span={2} className={styles.row_number}>
                {index + 1}
              </Col>
              <Col span={22}>
                <Row>
                  <PreviewCompact
                    lecture={lecture}
                    onClick={() => goToLecture(lecture)}
                    onMetaClick={() => goToLecture(lecture, true)}
                    onCtrlClick={() => goToLecture(lecture, true)}
                  />
                </Row>
                <Row>
                  {lecture.highlight !== null && (
                    <HighlightText
                      highlight={lecture.highlight}
                    ></HighlightText>
                  )}
                </Row>
              </Col>
            </Row>
          );
        })}
      </Space>
    </Row>
  );
}
