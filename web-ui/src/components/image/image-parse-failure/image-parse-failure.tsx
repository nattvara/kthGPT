import styles from './image-parse-failure.less';
import { FileImageOutlined } from '@ant-design/icons';
import { Button, Row, Typography, notification, Col } from 'antd';
import { Image } from '@/types/search';
import { useMutation } from '@tanstack/react-query';
import apiClient, { ServerErrorResponse, ServerResponse } from '@/http';

const { Title, Paragraph } = Typography;

interface ImageResponse extends ServerResponse {
  data: Image;
}

interface ImageParseFailureProps {
  image: Image;
  onRestart: (image: Image) => void;
}

export default function ImageParseFailure(props: ImageParseFailureProps) {
  const { image, onRestart } = props;

  const [notificationApi, contextHolder] = notification.useNotification();

  const { isLoading: isRestarting, mutate: restart } = useMutation(
    async () => {
      return await apiClient.post(
        `/assignments/image/${image.id}?restart=true`
      );
    },
    {
      onSuccess: (res: ImageResponse) => {
        const result = {
          status: res.status + '-' + res.statusText,
          headers: res.headers,
          data: res.data,
        };
        onRestart(result.data);
      },
      onError: (err: ServerErrorResponse) => {
        notificationApi['error']({
          message: 'Failed to get image',
          description: err.response.data.detail,
        });
      },
    }
  );

  return (
    <>
      {contextHolder}
      <Row>
        <Title level={4}>
          Something went wrong when analyzing the lecture!
        </Title>
        <Paragraph>
          Unfortunately something must have gone wrong, click the button to try
          parsing the assignment again. Sometimes restarting just fixes things
          ¯\_(ツ)_/¯
        </Paragraph>
      </Row>
      <Row justify="center" style={{ width: '100%' }}>
        <Col>
          <Button
            onClick={() => restart()}
            loading={isRestarting}
            type="primary"
            key="btn"
            icon={<FileImageOutlined />}
            size="large"
          >
            Restart
          </Button>
        </Col>
      </Row>
    </>
  );
}
