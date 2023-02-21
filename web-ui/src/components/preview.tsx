import styles from './preview.less';
import {
  Image,
  Card,
  Spin,
  Row,
  Col,
  Space,
} from 'antd';
import { Lecture } from '@/components/lecture';
import { makeUrl } from '@/http';
import { EVENT_GOTO_LECTURE, emitEvent } from '@/matomo';
import svFlag from '@/assets/flag-sv.svg';
import enFlag from '@/assets/flag-en.svg';
import {
  AudioOutlined,
  BookOutlined,
  ClockCircleOutlined,
  NumberOutlined,
} from '@ant-design/icons';

interface PreviewProps {
  lecture: Lecture
}

const { Meta } = Card;

const prettyLengthString = (seconds: number) => {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);

  return `${hours}h ${minutes}min`;
}

export default function Preview(props: PreviewProps) {
  const { lecture } = props;

  const openKthPlay = (url: string) => {
    window.open(url, '_blank');
    emitEvent(EVENT_GOTO_LECTURE);
  }

  let flagIcon = '';
  if (lecture.language == 'sv') {
    flagIcon = svFlag;
  }
  else if (lecture.language == 'en') {
    flagIcon = enFlag;
  }

  let dateString = '';
  if (lecture.date !== null) {
    dateString = new Date(lecture.date).toISOString().split('T')[0];
  }

  return (
    <Card
      hoverable
      className={styles.preview}
      onClick={() => openKthPlay(lecture.content_link)}
      cover={
          <>
            <Spin tip="Loading..." spinning={lecture.preview_uri === null}>
              <Image
                preview={false}
                style={{minHeight: '100px'}}
                src={lecture.preview_uri === null ? '' : makeUrl(lecture.preview_uri!)} />
            </Spin>
          </>
        }>
      <>
        <Meta title={
          lecture.title === null ? '' : lecture.title
        } description={<>
          {lecture.date !== null &&
            <Row>
              <strong>{dateString}</strong>
            </Row>
          }
          <Row>
            {lecture.content_link}
          </Row>
          <div className={styles.meta_container}>
            <div className={styles.meta}>
              <Row justify='start' align='middle'>
                <Space direction='horizontal'>
                  <Col>
                    <h3 className={styles.language}><AudioOutlined /> Language</h3>
                  </Col>
                  <Col>
                    <Image
                      src={flagIcon}
                      height={20}
                      className={styles.flag}
                      preview={false}
                      />
                  </Col>
                </Space>
              </Row>
            </div>

            {lecture.length !== 0 &&
              <div className={styles.meta}>
                <Row justify='start' align='middle'>
                  <Space direction='horizontal'>
                    <Col>
                      <h3 className={styles.length}><ClockCircleOutlined /> Length</h3>
                    </Col>
                    <Col>
                      {prettyLengthString(lecture.length!)}
                    </Col>
                  </Space>
                </Row>
              </div>
            }
            {lecture.words !== 0 &&
              <div className={styles.meta}>
                <Row justify='start' align='middle' className={styles.stat}>
                  <Space direction='horizontal'>
                    <Col>
                      <h3 className={styles.words}><NumberOutlined /> Words</h3>
                    </Col>
                    <Col>
                      {lecture.words!.toLocaleString('sv')}
                    </Col>
                  </Space>
                </Row>
              </div>
            }
            {lecture.courses.map(course =>
              <div key={course.course_code} className={`${styles.meta} ${styles.course}`}>
                <Row justify='start' align='middle' className={styles.stat}>
                  <Space direction='horizontal'>
                    <Col>
                      <h3 className={styles.course}><BookOutlined /> {course.course_code}</h3>
                    </Col>
                  </Space>
                </Row>
              </div>
            )}
        </div>
        </>} />
      </>
    </Card>
  )
}
