import styles from './selector.less';
import {
  Row,
  Col,
  Space,
  Image,
  Card,
  Steps,
  Typography,
  Divider,
} from 'antd';
import kthLogo from '@/assets/kth.svg';
import youtubeLogo from '@/assets/youtube.svg';
import { useState } from 'react';
import { CloudOutlined, FileSearchOutlined, VideoCameraAddOutlined, VideoCameraOutlined } from '@ant-design/icons';
import KTH from './kth';
import Youtube from './youtube';
import CourseBrowser from './course-browser';

const SOURCE_KTH = 'kth';

const SOURCE_YOUTUBE = 'youtube';

const { Title } = Typography;
const { Meta } = Card;

export default function Selector() {
  const [currentTab, setCurrentTab] = useState(0);
  const [source, setSource] = useState<string | null>(null);

  const goToTab = (newValue: number) => {
    if (newValue === 1 && source === null) return;
    setCurrentTab(newValue);
  };

  const selectSource = async (source: string) => {
    await setSource(source);
    setCurrentTab(1);
  }

  let sourcePretty = 'Select where the lecture is hosted';
  if (source === SOURCE_KTH) {
    sourcePretty = 'https://play.kth.se'
  } else if (source === SOURCE_YOUTUBE) {
    sourcePretty = 'https://youtube.com'
  }

  return (
    <Row>
      <Col xs={24} sm={11}>
        <Title level={2}>Browse courses <FileSearchOutlined /></Title>
        <Title level={5} className={styles.subtitle}>There are 45 lectures in 3 courses</Title>

        <CourseBrowser />
      </Col>
      <Col xs={0} sm={2} className={styles.divider}>
        <Divider type='vertical' />
      </Col>
      <Col xs={24} sm={11}>
        <Title level={2}>...or add a lecture <VideoCameraAddOutlined /></Title>
        <Title level={5} className={styles.subtitle}>Ask kthGPT to watch a new lecture</Title>
      </Col>
    </Row>
  );
}
