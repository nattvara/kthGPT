import styles from './selector.less';
import { Row, Col, Typography, Divider, Statistic } from 'antd';
import { useEffect, useState } from 'react';
import { FileSearchOutlined, VideoCameraAddOutlined } from '@ant-design/icons';
import CourseBrowser from './course-browser';
import apiClient from '@/http';
import LectureAdder from './lecture-adder';
import { emitEvent, CATEGORY_SELECTOR, EVENT_ERROR_RESPONSE } from '@/matomo';

const { Title } = Typography;

interface Stats {
  courses: number;
  lectures: number;
  lectures_without_courses: number;
}

export default function Selector() {
  const [stats, setStats] = useState<Stats>({
    courses: 0,
    lectures: 0,
    lectures_without_courses: 0,
  });

  const fetchStats = async () => {
    try {
      const response = await apiClient.get('/stats');
      await setStats(response.data);
    } catch (err: unknown) {
      console.log(err);
      emitEvent(CATEGORY_SELECTOR, EVENT_ERROR_RESPONSE, 'fetchStats');
    }
  };

  useEffect(() => {
    fetchStats();

    document.title = `kthGPT`;
  }, []);

  return (
    <Row className={styles.selector}>
      <Col xs={24} sm={11}>
        <Title level={2}>
          Find a lecture <FileSearchOutlined />
        </Title>
        <Title level={5} className={styles.subtitle}>
          kthGPT has already watched <Statistic value={stats.lectures} />
          <span> </span>
          lectures from
          <span> </span>
          <Statistic value={stats.courses} />
          <span> </span>
          courses
        </Title>

        <CourseBrowser
          lecturesWithoutCourses={stats.lectures_without_courses}
        />
      </Col>
      <Col xs={0} sm={2} className={styles.divider}>
        <Divider type="vertical" />
      </Col>
      <Col xs={24} sm={11}>
        <Title level={2}>
          ...or add a new lecture <VideoCameraAddOutlined />
        </Title>
        <Title level={5} className={styles.subtitle}>
          Ask kthGPT to watch a new lecture, it's completely automatic.
        </Title>

        <LectureAdder />
      </Col>
    </Row>
  );
}
