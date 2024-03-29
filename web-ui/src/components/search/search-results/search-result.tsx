import styles from './search-result.less';
import { Lecture } from '@/types/lecture';
import { Row, Space, Col } from 'antd';
import { history } from 'umi';
import { emitEvent } from '@/matomo';
import { LecturePreviewCompact } from '@/components/lecture/lecture-preview/lecture-preview';
import { TextHighlight } from '@/components/text/text-highlight/text-highlight';
import {
  ACTION_NONE,
  CATEGORY_SEARCH_RESULTS,
  EVENT_GOTO_LECTURE,
} from '@/matomo/events';

interface SearchResultProps {
  lectures: Lecture[];
  className: string;
}

export default function SearchResult(props: SearchResultProps) {
  const { lectures, className } = props;

  const goToLecture = async (lecture: Lecture, newTab = false) => {
    const url = `/lectures/${lecture.public_id}/${lecture.language}/questions`;

    if (newTab) {
      window.open(url, '_blank');
    } else {
      await history.push(url);
    }

    emitEvent(
      CATEGORY_SEARCH_RESULTS,
      EVENT_GOTO_LECTURE,
      lecture.title === null ? ACTION_NONE : lecture.title
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
                  <LecturePreviewCompact
                    lecture={lecture}
                    onClick={() => goToLecture(lecture)}
                    onMetaClick={() => goToLecture(lecture, true)}
                    onCtrlClick={() => goToLecture(lecture, true)}
                  />
                </Row>
                <Row>
                  {lecture.highlight !== null && (
                    <TextHighlight
                      highlight={lecture.highlight}
                    ></TextHighlight>
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
