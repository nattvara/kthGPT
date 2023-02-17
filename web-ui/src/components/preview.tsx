import styles from './preview.less';
import {
  Image,
  Card,
  Spin,
  Row,
  Col,
  Space,
} from 'antd';
import { Lecture } from '@/components/lecture';
import { makeUrl } from '@/http';
import { EVENT_GOTO_LECTURE, emitEvent } from '@/matomo';
import svFlag from '@/assets/flag-sv.svg';
import enFlag from '@/assets/flag-en.svg';
import { AudioOutlined } from '@ant-design/icons';

interface PreviewProps {
  lecture: Lecture
}

const { Meta } = Card;

export default function Preview(props: PreviewProps) {
  const { lecture } = props;

  const openKthPlay = (url: string) => {
    window.open(url, '_blank');
    emitEvent(EVENT_GOTO_LECTURE);
  }

  let flagIcon = '';
  if (lecture.language == 'sv') {
    flagIcon = svFlag;
  }
  else if (lecture.language == 'en') {
    flagIcon = enFlag;
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
      <>
        <Meta title='Lecture' description={<>
          <Row>
            {lecture.content_link}
          </Row>
          <Row justify='start' align='middle'>
            <Space direction='horizontal'>
              <Col>
                <h3 className={styles.language}><AudioOutlined /> Language</h3>
              </Col>
              <Col>
                <Image
                  src={flagIcon}
                  height={30}
                  className={styles.flag}
                  preview={false}
                  />
              </Col>
            </Space>
          </Row>
        </>} />
      </>
    </Card>
  )
}
