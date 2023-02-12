import {
  SearchOutlined,
} from '@ant-design/icons';
import styles from './questions.less';
import {
  Input,
  Row,
  Col,
  Space,
} from 'antd';
import { notification } from 'antd';
import { useMutation } from '@tanstack/react-query';
import { useState } from 'react';
import apiClient from '@/http';
import { history } from 'umi';

interface QuestionsProps {
  id: string
  language: string
}

export default function Questions(props: QuestionsProps) {
  const { id, language } = props;
  const [queryString, setQueryString] = useState('');

  const [notificationApi, contextHolder] = notification.useNotification();

  return (
    <>
      {contextHolder}
      <Space direction="vertical" size="large" style={{width: '100%'}}>
        <Row>
          <Col span={24}>
            <Input
              className={styles.hugeInput}
              value={queryString}
              onChange={e => setQueryString(e.target.value)}
              onPressEnter={() => {}}
              placeholder="Enter Query"
              prefix={<SearchOutlined />} />
          </Col>
        </Row>
        <Row gutter={[10, 10]}>
          {id}
          {language}
        </Row>
      </Space>
    </>
  );
}
