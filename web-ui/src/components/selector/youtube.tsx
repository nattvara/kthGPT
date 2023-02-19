import {
  BulbOutlined,
  PlayCircleOutlined,
} from '@ant-design/icons';
import styles from './kth.less';
import {
  Input,
  Row,
  Col,
  Button,
  Typography,
  Space,
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


const { Title, Paragraph } = Typography;

export default function Youtube() {
  const [language, setLanguage] = useState('en');
  const [url, setUrl] = useState('');

  const [notificationApi, contextHolder] = notification.useNotification();

  const { isLoading: isPosting, mutate: postUrl } = useMutation(
    async () => {
      return await apiClient.post(`/url/youtube`, {
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
    await postUrl();
    emitEvent(EVENT_SUBMIT_URL);
  };

  return (
    <Space direction='vertical' size='large' style={{width: '100%'}}>
      {contextHolder}
      <Row>
        <Col span={24}>
          <Input
            className={styles.hugeInput}
            value={url}
            onChange={e => setUrl(e.target.value)}
            onPressEnter={submit}
            placeholder='Enter video.. eg. https://www.youtube.com/watch?v=nnkCE...'
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
  );
}
