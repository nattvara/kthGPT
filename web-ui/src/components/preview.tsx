import styles from './preview.less';
import {
  Image,
  Card,
  Spin,
} from 'antd';
import { Lecture } from '@/components/lecture';
import { makeUrl } from '@/http';

interface PreviewProps {
  lecture: Lecture
}

const { Meta } = Card;

export default function Preview(props: PreviewProps) {
  const { lecture } = props;

  const openKthPlay = (url: string) => {
    window.open(url, '_blank');
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
                style={{minHeight: '100px'}}
                src={lecture.preview_uri === null ? '' : makeUrl(lecture.preview_uri!)} />
            </Spin>
          </>
        }>
      <Meta title='Lecture' description={lecture.content_link} />
    </Card>
  )
}
