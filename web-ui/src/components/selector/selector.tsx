import {
  BulbOutlined,
  PlayCircleOutlined,
  NotificationOutlined,
} from '@ant-design/icons';
import styles from './selector.less';
import {
  Input,
  Row,
  Col,
  Space,
  Button,
  Radio,
} from 'antd';
import { notification } from 'antd';
import { useMutation } from '@tanstack/react-query';
import { useState } from 'react';
import apiClient from '@/http';
import { history } from 'umi';

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
  };

  const random = async () => {
    await requestRandom();
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
              Analyze
            </Button>
          </Col>
          <Col>
            <Radio.Group onChange={e => setLanguage(e.target.value)} value={language} defaultValue='en' buttonStyle='solid' size='large'>
              <Radio.Button value='en'>English lecture</Radio.Button>
              <Radio.Button value='sv'>Swedish lecture</Radio.Button>
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
