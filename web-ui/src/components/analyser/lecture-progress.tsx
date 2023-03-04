import { ClockCircleOutlined } from '@ant-design/icons';
import styles from './lecture-progress.less';
import {
  Row,
  Col,
  Space,
  Alert,
  Progress,
  Tag,
  Collapse,
  Button,
  Typography,
} from 'antd';
import { Lecture } from '@/components/lecture';

interface LectureProgressProps {
  lecture: Lecture;
}

const { Panel } = Collapse;
const { Title } = Typography;

const prettyTimeElapsedString = (date: Date) => {
  const currentDate = new Date();
  const elapsedTime = currentDate.getTime() - date.getTime();
  let seconds = Math.floor(elapsedTime / 1000);
  const minutes = Math.floor(seconds / 60);
  seconds = seconds % 60;

  if (minutes > 180) {
    return 'long ago...';
  }

  if (minutes > 120) {
    return 'over 2h ago';
  }

  if (minutes > 60) {
    return 'over 1h ago';
  }

  if (minutes === 0) {
    if (seconds < 5) {
      return 'Just now';
    }

    return `${seconds}s ago`;
  }

  return `${minutes}min ${seconds}s ago`;
};

export default function LectureProgress(props: LectureProgressProps) {
  const { lecture } = props;

  return (
    <>
      <Collapse
        className={styles.collapsible}
        collapsible="header"
        defaultActiveKey={[]}
        expandIcon={() => <></>}
      >
        <Panel
          key="0"
          className={styles.overall}
          header={
            <>
              <Row>
                <Title level={4} style={{ margin: 0 }}>
                  Lecture Progress
                </Title>
              </Row>
              <Row>
                <Progress
                  className={styles.overall}
                  showInfo={true}
                  percent={lecture.analysis?.overall_progress}
                />
              </Row>
              <Row gutter={[20, 10]}>
                {lecture.analysis !== null &&
                  lecture.analysis?.last_message !== null &&
                  lecture.analysis?.state !== 'ready' && (
                    <Col sm={24} md={16}>
                      <Tag
                        className={styles.tag}
                        icon={<ClockCircleOutlined />}
                        color="#108ee9"
                      >
                        {prettyTimeElapsedString(
                          new Date(lecture.analysis.last_message?.timestamp)
                        )}
                      </Tag>
                      <Alert
                        message={
                          <>
                            <Space direction="horizontal" size="small">
                              <strong>
                                {lecture.analysis?.last_message?.title}
                              </strong>
                              <span>
                                {lecture.analysis?.last_message?.body}
                              </span>
                            </Space>
                          </>
                        }
                        type="info"
                        showIcon
                      />
                    </Col>
                  )}
                <Col sm={24} md={8}>
                  <Row
                    justify="center"
                    align="middle"
                    style={{ height: '100%' }}
                  >
                    <Col>
                      <Button type="dashed" size="large">
                        Show More Info
                      </Button>
                    </Col>
                  </Row>
                </Col>
              </Row>
            </>
          }
        >
          <Space direction="vertical" size="large">
            <Row gutter={[20, 10]}>
              <Col span={24}>
                Downloading video
                <Progress
                  percent={lecture.analysis?.mp4_progress}
                  showInfo={lecture.analysis?.mp4_progress !== 0}
                />
                Extracting audio
                <Progress
                  percent={lecture.analysis?.mp3_progress}
                  showInfo={lecture.analysis?.mp3_progress !== 0}
                />
                Transcribing lecture
                <Progress
                  percent={lecture.analysis?.transcript_progress}
                  showInfo={lecture.analysis?.transcript_progress !== 0}
                />
                Generating summary
                <Progress
                  percent={lecture.analysis?.summary_progress}
                  showInfo={lecture.analysis?.summary_progress !== 0}
                />
              </Col>
            </Row>
          </Space>
        </Panel>
      </Collapse>
    </>
  );
}
