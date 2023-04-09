import styles from './image-subjects.less';
import { Col, Row, Skeleton, Tag, Typography } from 'antd';
import { Image } from '@/types/search';

interface ImageSubjectsProps {
  image: Image;
}

const { Title } = Typography;

export default function ImageSubjects(props: ImageSubjectsProps) {
  const { image } = props;

  return (
    <>
      <Title level={5} className={styles.title}>
        Subjects
      </Title>
      <Row className={styles.full_width}>
        {image.classify_subjects_ok === null && (
          <Skeleton active paragraph={{ rows: 1 }}></Skeleton>
        )}
      </Row>
      <Row className={styles.full_width}>
        {image.subjects.map((subject, index) => (
          <Col key={index}>
            <Tag color="magenta">{subject}</Tag>
          </Col>
        ))}
      </Row>
    </>
  );
}
