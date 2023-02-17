import {
  BulbOutlined,
  PlayCircleOutlined,
  NotificationOutlined,
  AudioOutlined,
} from '@ant-design/icons';
import styles from './selector.less';
import {
  Input,
  Row,
  Col,
  Space,
  Button,
  Radio,
  Image,
} from 'antd';
import { notification } from 'antd';
import { useMutation } from '@tanstack/react-query';
import { useState } from 'react';
import apiClient from '@/http';
import { history } from 'umi';
import {
  EVENT_FEELING_LUCKY,
  emitEvent,
  EVENT_SUBMIT_URL,
} from '@/matomo';
import enFlag from '@/assets/flag-en.svg';
import svFlag from '@/assets/flag-sv.svg';


export default function Selector() {
  const [language, setLanguage] = useState('en');
  const [url, setUrl] = useState('');

  const [notificationApi, contextHolder] = notification.useNotification();

  const { isLoading: isPosting, mutate: postUrl } = useMutation(
    async () => {
      return await apiClient.post(`/url`, {
        url,
        language,
      });
    },
    {
      onSuccess: (res: any) => {
        const result = {
          status: res.status + '-' + res.statusText,
          headers: res.headers,
          data: res.data,
        };
        history.push('/analyse' + result.data.uri);
      },
      onError: (err: any) => {
        notificationApi['error']({
          message: 'Failed to get lecture',
          description: err.response.data.detail,
        });
      },
    }
  );

  const { isLoading: isWaitingForRandom, mutate: requestRandom } = useMutation(
    async () => {
      return await apiClient.get(`/lectures?random=true`);
    },
    {
      onSuccess: (res: any) => {
        const result = {
          status: res.status + '-' + res.statusText,
          headers: res.headers,
          data: res.data,
        };
        const lecture = result.data[0];
        history.push(`/questions/lectures/${lecture.public_id}/${lecture.language}`);
      },
      onError: (err: any) => {
        notificationApi['error']({
          message: 'Failed to get a random lecture',
          description: err.response.data.detail,
        });
      },
    }
  );

  const submit = async () => {
    await postUrl();
    emitEvent(EVENT_SUBMIT_URL);
  };

  const random = async () => {
    await requestRandom();
    emitEvent(EVENT_FEELING_LUCKY);
  };

  return (
    <>
      {contextHolder}
      <Space direction='vertical' size='large' style={{width: '100%'}}>
        <Row>
          <Col span={24}>
            <Input
              className={styles.hugeInput}
              value={url}
              onChange={e => setUrl(e.target.value)}
              onPressEnter={submit}
              placeholder='Enter video.. eg. https://play.kth.se/media/...'
              prefix={<PlayCircleOutlined />} />
          </Col>
        </Row>
        <Row gutter={[10, 10]}>
          <Col>
            <Button onClick={submit} type='primary' icon={<BulbOutlined />} size='large' loading={isPosting}>
              {!isPosting && <>Analyze</>}
              {isPosting && <>Verifying video URL . . .</>}
            </Button>
          </Col>
          <Col>
            <Radio.Group onChange={e => setLanguage(e.target.value)} value={language} defaultValue='en' buttonStyle='solid' size='large'>
              <Button type='text' size='large' style={{pointerEvents: 'none'}}>
                <AudioOutlined /> Select lecture language:
              </Button>
              <Radio value='en'>
                <Row justify='center' align='middle'>
                  <Col><Image
                    src={enFlag}
                    height={40}
                    preview={false}
                    className={`${language !== 'en' ? styles.grayscale : ''}`}
                  /></Col>
                </Row>
              </Radio>
              <Radio value='sv'>
                <Row justify='center' align='middle'>
                  <Col><Image
                    src={svFlag}
                    height={40}
                    preview={false}
                    className={`${language !== 'sv' ? styles.grayscale : ''}`}
                  /></Col>
                </Row>
              </Radio>
            </Radio.Group>
          </Col>
          <Col>
            <Button type='text' size='large' style={{pointerEvents: 'none'}}>
              Click here to try on a random lecture:
            </Button>
          </Col>
          <Button onClick={random} type='dashed' icon={<NotificationOutlined />} size='large' loading={isWaitingForRandom}>
            I'm feeling lucky!
          </Button>
        </Row>
      </Space>
    </>
  );
}
