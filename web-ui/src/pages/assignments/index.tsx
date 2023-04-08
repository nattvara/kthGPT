import styles from './index.less';
import Frame from '@/components/page/frame/frame';
import { registerPageLoad } from '@/matomo';
import {
  Button,
  Col,
  Result,
  Row,
  Skeleton,
  Space,
  Typography,
  notification,
} from 'antd';
import { useMutation } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import { useParams } from 'umi';
import apiClient, { ServerErrorResponse, ServerResponse } from '@/http';
import { Image } from '@/types/search';
import ImageUpload from '@/components/image/image-upload/image-upload';
import ImageProgress from '@/components/image/image-progress/image-progress';
import { history } from 'umi';
import ImageDescription from '@/components/image/image-description/image-description';
import ImageQuestion from '@/components/image/image-question/image-question';
import ImageLectureMatches from '@/components/searching/search-by-image/search-by-image';
import ImageParseFailure from '@/components/image/image-parse-failure/image-parse-failure';

const { Title, Paragraph } = Typography;

const UPDATE_INTERVAL = 1000;

interface ImageResponse extends ServerResponse {
  data: Image;
}

export default function AssignmentsIndexPage() {
  const { id } = useParams();

  const [uploadId, setUploadId] = useState<string | undefined>(id);
  const [image, setImage] = useState<null | Image>(null);
  const [parseFailed, setParseFailed] = useState<boolean>(false);
  const [notificationApi, contextHolder] = notification.useNotification();
  const [notFound, setNotFound] = useState<boolean | null>(null);

  const breadcrumbs = [
    {
      title: 'Assignments',
    },
  ];

  const { mutate: fetchImage } = useMutation(
    async () => {
      return await apiClient.get(`/assignments/image/${id}`);
    },
    {
      onSuccess: (res: ImageResponse) => {
        const result = {
          status: res.status + '-' + res.statusText,
          headers: res.headers,
          data: res.data,
        };
        setImage(result.data);
      },
      onError: (err: ServerErrorResponse) => {
        if (err.response.status === 404) {
          setNotFound(true);
        } else {
          notificationApi['error']({
            message: 'Failed to get image upload',
            description: err.response.data.detail,
          });
        }
      },
    }
  );

  const onImageUploadComplete = (i: Image) => {
    if (image && i.id !== image.id) {
      setImage(null);
    }
    history.push(`/assignments/${i.id}`);
  };

  const onRestart = (image: Image) => {
    fetchImage();
  };

  useEffect(() => {
    registerPageLoad();
  }, []);

  useEffect(() => {
    setUploadId(id);
  }, [id]);

  useEffect(() => {
    if (id !== null) fetchImage();
  }, [id, fetchImage]);

  useEffect(() => {
    const interval = setInterval(() => {
      if (uploadId !== null) fetchImage();
    }, UPDATE_INTERVAL);

    return () => clearInterval(interval);
  }, [uploadId, fetchImage]);

  if (notFound) {
    return (
      <>
        <Frame showBack={true} breadcrumbs={breadcrumbs}>
          <Result
            status="404"
            title="Could not find assignment"
            extra={[
              <Button
                onClick={() => history.push('/')}
                type="primary"
                key="btn"
                size="large"
              >
                Go back home
              </Button>,
            ]}
          />
        </Frame>
      </>
    );
  }

  if (uploadId === undefined) {
    return (
      <>
        <Frame showBack={true} breadcrumbs={breadcrumbs}>
          <Skeleton active paragraph={{ rows: 4 }} />
        </Frame>
      </>
    );
  }
  if (image === null) {
    return (
      <>
        <Frame showBack={true} breadcrumbs={breadcrumbs}>
          <Skeleton active paragraph={{ rows: 4 }} />
        </Frame>
      </>
    );
  }

  return (
    <>
      {contextHolder}
      <Frame showBack={true} breadcrumbs={breadcrumbs}>
        <Row>
          <Col sm={24} md={8} className={styles.padding_left_right}>
            <Space direction="vertical" size="large">
              <Row>
                <ImageUpload
                  uploadId={uploadId}
                  noMargin={true}
                  onUploadComplete={(image) => onImageUploadComplete(image)}
                />
              </Row>
              <Row>
                {parseFailed && (
                  <ImageParseFailure
                    image={image}
                    onRestart={(image) => {
                      setParseFailed(false);
                      onRestart(image);
                    }}
                  />
                )}
              </Row>
              <Row>
                <ImageProgress
                  image={image}
                  onUpdate={(result) => setParseFailed(result.failed)}
                />
              </Row>
              <Row>
                <ImageDescription image={image} />
              </Row>
            </Space>
          </Col>
          <Col sm={24} md={8} className={styles.padding_left_right}>
            <Row>
              <ImageQuestion image={image} />
            </Row>
          </Col>
          <Col sm={24} md={8} className={styles.padding_left_right}>
            <Row>
              <Title level={2} className={styles.section_title}>
                Where can I learn how to solve this assignment?
              </Title>
              <Paragraph>
                kthGPT is trying to find which lectures and where you can learn
                how to solve this assignment.
              </Paragraph>
              <Row className={styles.full_width}>
                <ImageLectureMatches image={image} />
              </Row>
            </Row>
          </Col>
        </Row>
      </Frame>
    </>
  );
}
