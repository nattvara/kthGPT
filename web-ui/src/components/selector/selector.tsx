import styles from './selector.less';
import {
  Row,
  Col,
  Space,
  Image,
  Card,
  Steps,
} from 'antd';
import kthLogo from '@/assets/kth.svg';
import youtubeLogo from '@/assets/youtube.svg';
import { useState } from 'react';
import { CloudOutlined, VideoCameraOutlined } from '@ant-design/icons';
import KTH from './kth';
import Youtube from './youtube';

const SOURCE_KTH = 'kth';

const SOURCE_YOUTUBE = 'youtube';


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
    <>
      <Space direction='vertical' size='large'>
        <Row>
          <Steps
          type="navigation"
          size="small"
          current={currentTab}
          onChange={goToTab}
          className="site-navigation-steps"
          items={[
            {
              title: 'Lecture Source',
              description: sourcePretty,
              icon: <CloudOutlined />,
            },
            {
              title: 'Video URL',
              description: 'Enter URL to the video',
              icon: <VideoCameraOutlined />,
            },
          ]}
        />
        </Row>

        {currentTab === 0 &&
          <Row>
            <Space direction='horizontal'>
              <Col>
                <Card
                  hoverable
                  className={styles.source}
                  onClick={() => selectSource(SOURCE_KTH)}
                  cover={<Image preview={false} src={kthLogo} />}>
                  <>
                    <Meta title='KTH Play' />
                  </>
                </Card>
              </Col>
              <Col>
                <Card
                  hoverable
                  className={styles.source}
                  onClick={() => selectSource(SOURCE_YOUTUBE)}
                  cover={<Image preview={false} src={youtubeLogo} />}>
                  <>
                    <Meta title='YouTube' />
                  </>
                </Card>
              </Col>
            </Space>
          </Row>
        }
        {currentTab === 1 &&
          <Row>
          {source === SOURCE_KTH && <KTH />}
          {source === SOURCE_YOUTUBE && <Youtube />}
          </Row>
        }
      </Space>
    </>
  );
}
