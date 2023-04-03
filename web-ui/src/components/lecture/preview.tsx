import styles from './preview.less';
import { Image, Card, Spin, Row, Col, Space } from 'antd';
import { Lecture } from '@/components/lecture';
import { makeUrl } from '@/http';
import { EVENT_GOTO_CONTENT, CATEGORY_PREVIEW, emitEvent } from '@/matomo';
import {
  AudioOutlined,
  BookOutlined,
  ClockCircleOutlined,
  NumberOutlined,
} from '@ant-design/icons';
import svFlag from '@/assets/flag-sv.svg';
import enFlag from '@/assets/flag-en.svg';
import kthLogo from '@/assets/kth.svg';
import youtubeLogoSmall from '@/assets/youtube-small.svg';

const { Meta } = Card;

const prettyLengthString = (seconds: number) => {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);

  return `${hours}h ${minutes}min`;
};

interface PreviewCompactProps {
  lecture: Lecture;
  onClick: () => void;
  onMetaClick: () => void;
  onCtrlClick: () => void;
}

export function PreviewCompact(props: PreviewCompactProps) {
  const { lecture, onClick, onCtrlClick, onMetaClick } = props;

  let flagIcon = '';
  if (lecture.language === 'sv') {
    flagIcon = svFlag;
  } else if (lecture.language === 'en') {
    flagIcon = enFlag;
  }

  let dateString = '';
  if (lecture.date !== null) {
    dateString = new Date(lecture.date).toISOString().split('T')[0];
  }

  let icon = '';
  if (lecture.source === 'youtube') {
    icon = youtubeLogoSmall;
  } else if (lecture.source === 'kth') {
    icon = kthLogo;
  } else if (lecture.source === 'kth_raw') {
    icon = kthLogo;
  }

  return (
    <Card
      className={styles.compact}
      hoverable
      onClick={(e: React.MouseEvent) => {
        if (e.metaKey) return onMetaClick();
        if (e.ctrlKey) return onCtrlClick();
        onClick();
      }}
    >
      <Row>
        <Col span={8}>
          <div className={styles.image}>
            <Spin
              tip="Loading..."
              spinning={lecture.preview_small_uri === null}
            >
              <Image
                preview={false}
                src={
                  lecture.preview_small_uri === null
                    ? ''
                    : makeUrl(lecture.preview_small_uri)
                }
              />
            </Spin>
          </div>
        </Col>
        <Col span={16} className={styles.body}>
          <Row className={styles.title}>
            <strong>{lecture.title}</strong>
          </Row>
          <Row align="middle" justify="start">
            <Space direction="horizontal">
              <Col>
                <strong>{dateString}</strong>
              </Col>
              <Col>
                <Image
                  src={flagIcon}
                  height={18}
                  width={lecture.language === 'en' ? 36 : 29}
                  className={styles.flag}
                  preview={false}
                />
              </Col>
              <Col>
                <Image
                  src={icon}
                  height={20}
                  width={20}
                  className={styles.logo}
                  preview={false}
                />
              </Col>
            </Space>
          </Row>
        </Col>
      </Row>
    </Card>
  );
}

interface PreviewProps {
  lecture: Lecture;
}

export default function Preview(props: PreviewProps) {
  const { lecture } = props;

  const openKthPlay = (url: string) => {
    window.open(url, '_blank');
    emitEvent(CATEGORY_PREVIEW, EVENT_GOTO_CONTENT, url);
  };

  let flagIcon = '';
  if (lecture.language === 'sv') {
    flagIcon = svFlag;
  } else if (lecture.language === 'en') {
    flagIcon = enFlag;
  }

  let icon = '';
  if (lecture.source === 'youtube') {
    icon = youtubeLogoSmall;
  } else if (lecture.source === 'kth') {
    icon = kthLogo;
  } else if (lecture.source === 'kth_raw') {
    icon = kthLogo;
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
              style={{ minHeight: '100px' }}
              src={
                lecture.preview_uri === null ? '' : makeUrl(lecture.preview_uri)
              }
            />
          </Spin>
        </>
      }
    >
      <>
        <Meta
          title={lecture.title === null ? '' : lecture.title}
          description={
            <>
              {lecture.date !== null && (
                <Row>
                  <strong>{dateString}</strong>
                </Row>
              )}
              <Row>{lecture.content_link}</Row>
              <div className={styles.meta_container}>
                <div className={styles.meta}>
                  <Row justify="start" align="middle">
                    <Space direction="horizontal">
                      <Col>
                        <h3 className={styles.language}>
                          <AudioOutlined /> Language
                        </h3>
                      </Col>
                      <Col>
                        <Image
                          src={flagIcon}
                          height={20}
                          className={styles.flag}
                          preview={false}
                        />
                      </Col>
                      <Col>
                        <h3 className={styles.source}>From</h3>
                      </Col>
                      <Col>
                        <Image
                          src={icon}
                          height={20}
                          width={20}
                          className={styles.logo}
                          preview={false}
                        />
                      </Col>
                    </Space>
                  </Row>
                </div>
                {lecture.length !== null && lecture.length !== 0 && (
                  <div className={styles.meta}>
                    <Row justify="start" align="middle">
                      <Space direction="horizontal">
                        <Col>
                          <h3 className={styles.length}>
                            <ClockCircleOutlined /> Length
                          </h3>
                        </Col>
                        <Col>{prettyLengthString(lecture.length)}</Col>
                      </Space>
                    </Row>
                  </div>
                )}
                {lecture.words !== null && lecture.words !== 0 && (
                  <div className={styles.meta}>
                    <Row justify="start" align="middle" className={styles.stat}>
                      <Space direction="horizontal">
                        <Col>
                          <h3 className={styles.words}>
                            <NumberOutlined /> Words
                          </h3>
                        </Col>
                        <Col>{lecture.words.toLocaleString('sv')}</Col>
                      </Space>
                    </Row>
                  </div>
                )}
                {lecture.courses &&
                  lecture.courses.map((course) => (
                    <div
                      key={course.course_code}
                      className={`${styles.meta} ${styles.course}`}
                    >
                      <Row
                        justify="start"
                        align="middle"
                        className={styles.stat}
                      >
                        <Space direction="horizontal">
                          <Col>
                            <h3 className={styles.course}>
                              <BookOutlined /> {course.course_code}
                            </h3>
                          </Col>
                        </Space>
                      </Row>
                    </div>
                  ))}
              </div>
            </>
          }
        />
      </>
    </Card>
  );
}
