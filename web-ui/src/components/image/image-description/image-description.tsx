import styles from './image-description.less';
import { Skeleton, Typography } from 'antd';
import { Image } from '@/types/search';

interface ImageDescriptionProps {
  image: Image;
}

const { Title, Paragraph } = Typography;

export default function ImageDescription(props: ImageDescriptionProps) {
  const { image } = props;

  return (
    <>
      <Title level={5} className={styles.title}>
        Description
      </Title>
      {image.create_description_en_ok === null && <Skeleton active></Skeleton>}
      <Paragraph>{image.description_en}</Paragraph>
    </>
  );
}
