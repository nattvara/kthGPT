import {
  BulbOutlined,
  PlayCircleOutlined,
  WarningOutlined,
} from '@ant-design/icons';
import styles from './kth.less';
import {
  Input,
  Row,
  Col,
  Space,
  Button,
} from 'antd';
import { notification } from 'antd';
import { useMutation } from '@tanstack/react-query';
import { useState } from 'react';
import apiClient from '@/http';
import { history } from 'umi';
import {
  emitEvent,
  EVENT_SUBMIT_URL,
} from '@/matomo';
import LanguageSelector from './language-selector';


export default function KTH() {
  const [language, setLanguage] = useState(null);
  const [url, setUrl] = useState('');

  const [notificationApi, contextHolder] = notification.useNotification();

  const { isLoading: isPosting, mutate: postUrl } = useMutation(
    async () => {
      return await apiClient.post(`/url/kth`, {
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

  const submit = async () => {
    if (language === null) {
      notificationApi['warning']({
        icon: <WarningOutlined />,
        message: 'You must select a language for the lecture',
        description: 'Choose either English or Swedish',
      });
      return;
    }
    await postUrl();
    emitEvent(EVENT_SUBMIT_URL);
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
            <LanguageSelector onChange={e => setLanguage(e.target.value)} language={language} />
          </Col>
        </Row>
      </Space>
    </>
  );
}
