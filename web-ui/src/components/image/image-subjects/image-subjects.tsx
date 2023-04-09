import styles from './image-subjects.less';
import { Col, Row, Tag, Typography } from 'antd';
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
      <Row>
        {image.subjects.map((subject, index) => (
          <Col key={index}>
            <Tag color="magenta">{subject}</Tag>
          </Col>
        ))}
      </Row>
    </>
  );
}
