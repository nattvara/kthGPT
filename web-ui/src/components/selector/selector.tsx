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
  Statistic,
} from 'antd';
import kthLogo from '@/assets/kth.svg';
import youtubeLogo from '@/assets/youtube.svg';
import { useEffect, useState } from 'react';
import { CloudOutlined, FileSearchOutlined, VideoCameraAddOutlined, VideoCameraOutlined } from '@ant-design/icons';
import KTH from './kth';
import Youtube from './youtube';
import CourseBrowser from './course-browser';
import apiClient from '@/http';

const SOURCE_KTH = 'kth';

const SOURCE_YOUTUBE = 'youtube';

const { Title } = Typography;
const { Meta } = Card;

interface Stats {
  courses: number
  lectures: number
  lectures_without_courses: number
}


export default function Selector() {
  const [ currentTab, setCurrentTab ] = useState(0);
  const [ source, setSource ] = useState<string | null>(null);
  const [ stats, setStats ] = useState<Stats>({});

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

  const fetchStats = async () => {
    try {
      const response = await apiClient.get('/stats');
      await setStats(response.data);
    } catch (err: any) {
      console.log(err);
    }
  }

  useEffect(() => {
    fetchStats();
  }, []);

  return (
    <Row>
      <Col xs={24} sm={11}>
        <Title level={2}>Find a lecture <FileSearchOutlined /></Title>
        <Title
          level={5}
          className={styles.subtitle}
        >kthGPT has already watched <Statistic value={stats.lectures} /> lectures from <Statistic value={stats.courses} /> courses</Title>

        <CourseBrowser lecturesWithoutCourses={stats.lectures_without_courses} />
      </Col>
      <Col xs={0} sm={2} className={styles.divider}>
        <Divider type='vertical' />
      </Col>
      <Col xs={24} sm={11}>
        <Title level={2}>...or add a new lecture <VideoCameraAddOutlined /></Title>
        <Title level={5} className={styles.subtitle}>Ask kthGPT to watch a new lecture</Title>
      </Col>
    </Row>
  );
}
