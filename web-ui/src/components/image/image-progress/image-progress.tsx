import {
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  SyncOutlined,
} from '@ant-design/icons';
import styles from './image-progress.less';
import { Row, Col, Space, Progress, Tag, Collapse, Typography } from 'antd';
import { Image } from '@/types/search';
import { useEffect } from 'react';

interface ImageProgressProps {
  image: Image;
  onUpdate: (result: { failed: boolean }) => void;
}

type ProgressStatus = 'normal' | 'exception' | 'active' | 'success';

const { Panel } = Collapse;
const { Title, Paragraph } = Typography;

export default function ImageProgress(props: ImageProgressProps) {
  const { image, onUpdate } = props;

  const parsingStates = [
    {
      key: 'parse_image_content_ok',
      name: 'Parsing image',
      value: image.parse_image_content_ok,
    },
    {
      key: 'create_description_en_ok',
      name: 'Creating description (English)',
      value: image.create_description_en_ok,
    },
    {
      key: 'create_title_ok',
      name: 'Creating title',
      value: image.create_title_ok,
    },
    {
      key: 'create_description_sv_ok',
      name: 'Creating description (Swedish)',
      value: image.create_description_sv_ok,
    },
    {
      key: 'create_search_queries_sv_ok',
      name: 'Creating search terms (Swedish)',
      value: image.create_search_queries_sv_ok,
    },
    {
      key: 'create_search_queries_en_ok',
      name: 'Creating search terms (English)',
      value: image.create_search_queries_en_ok,
    },
  ];

  let done = 0;
  let notDone = 0;
  let failed = 0;
  for (let i = 0; i < parsingStates.length; i++) {
    if (parsingStates[i].value === true) {
      done++;
    } else if (parsingStates[i].value === false) {
      failed++;
    } else {
      notDone++;
    }
  }
  const percent = Math.round((done / (done + notDone)) * 100);

  let progressStatus: ProgressStatus = 'active';
  if (failed !== 0) {
    progressStatus = 'exception';
  } else if (percent === 100) {
    progressStatus = 'success';
  }

  useEffect(() => {
    if (failed !== 0) {
      onUpdate({ failed: true });
    } else {
      onUpdate({ failed: false });
    }
  }, [failed, done, notDone, onUpdate]);

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
                  Parsing Assignment
                </Title>
                <Paragraph className={styles.meta}>
                  This usually takes around 30 seconds
                </Paragraph>
              </Row>
              <Row>
                <Progress
                  className={styles.overall}
                  showInfo={true}
                  percent={percent}
                  status={progressStatus}
                />
              </Row>
            </>
          }
        >
          <Space direction="vertical" size="large">
            <Row gutter={[20, 10]}>
              {parsingStates.map((state) => (
                <Col key={state.key}>
                  {state.value === true && (
                    <Tag icon={<CheckCircleOutlined />} color="success">
                      {state.name}
                    </Tag>
                  )}
                  {state.value === null && (
                    <Tag icon={<SyncOutlined spin />} color="processing">
                      {state.name}
                    </Tag>
                  )}
                  {state.value === false && (
                    <Tag icon={<ExclamationCircleOutlined />} color="red">
                      {state.name}
                    </Tag>
                  )}
                </Col>
              ))}
            </Row>
          </Space>
        </Panel>
      </Collapse>
    </>
  );
}
