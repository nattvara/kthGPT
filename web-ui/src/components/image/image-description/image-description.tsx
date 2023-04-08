import styles from './image-description.less';
import { Typography } from 'antd';
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
      <Paragraph>{image.description_en}</Paragraph>
    </>
  );
}
