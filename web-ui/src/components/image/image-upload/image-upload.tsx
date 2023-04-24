import styles from './image-upload.less';
import { Row, Col, Alert, Upload, Image, Typography, notification } from 'antd';
import type { UploadProps } from 'antd';
import { useMutation } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import apiClient, {
  makeUrl,
  ServerErrorResponse,
  ServerResponse,
} from '@/http';
import { FileImageOutlined } from '@ant-design/icons';
import { UploadChangeParam, UploadFile } from 'antd/es/upload';
import { Image as ImageType } from '@/types/search';
import {
  ACTION_NONE,
  CATEGORY_IMAGE_UPLOAD,
  EVENT_ERROR_RESPONSE,
  EVENT_IMAGE_UPLOADED,
} from '@/matomo/events';
import { emitEvent } from '@/matomo';

const { Title } = Typography;
const { Dragger } = Upload;

interface ImageResponse extends ServerResponse {
  data: ImageType;
}

interface ImageUploadProps {
  uploadId?: string;
  noMargin?: boolean;
  compact?: boolean;
  onUploadComplete: (image: ImageType) => void;
}

export default function ImageUpload(props: ImageUploadProps) {
  const { uploadId, onUploadComplete, noMargin, compact } = props;

  const [id, setId] = useState<null | string>(null);
  const [error, setError] = useState<string>('');
  const [hovering, setHovering] = useState<boolean>(false);
  const [image, setImage] = useState<null | ImageType>(null);
  const [notificationApi, contextHolder] = notification.useNotification();

  const previewUrl = makeUrl(`/assignments/image/${id}/img`);

  const uploadProps: UploadProps = {
    name: 'file',
    multiple: false,
    action: makeUrl('/assignments/image'),
    maxCount: 1,
    async onChange(info: UploadChangeParam<UploadFile>) {
      const { status } = info.file;
      if (status === 'done') {
        setId(info.file.response.id);
        setError('');
        emitEvent(CATEGORY_IMAGE_UPLOAD, EVENT_IMAGE_UPLOADED, ACTION_NONE);
      } else if (status === 'error') {
        if (info.file.response) {
          setError(info.file.response.detail);
        } else {
          setError(
            'Something went wrong when uploading the image. Please try again.'
          );
        }
        emitEvent(CATEGORY_IMAGE_UPLOAD, EVENT_ERROR_RESPONSE, 'uploadProps');
      }
    },
  };

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
        onUploadComplete(result.data);
      },
      onError: (err: ServerErrorResponse) => {
        notificationApi['error']({
          message: 'Failed to get image',
          description: err.response.data.detail,
        });
        emitEvent(CATEGORY_IMAGE_UPLOAD, EVENT_ERROR_RESPONSE, 'fetchImage');
      },
    }
  );

  useEffect(() => {
    if (uploadId === undefined) {
      return;
    }
    setId(uploadId);
  }, [uploadId]);

  useEffect(() => {
    if (id !== null) fetchImage();
  }, [id, fetchImage]);

  return (
    <div
      className={styles.image_upload}
      onMouseEnter={() => setHovering(true)}
      onMouseLeave={() => setHovering(false)}
    >
      {contextHolder}
      <Row>
        <Dragger
          className={`${styles.dragger} ${noMargin ? styles.no_margin : ''} ${
            compact === true ? styles.compact : ''
          }`}
          {...uploadProps}
        >
          {(id === null || image === null) && (
            <>
              <Row
                className={`${styles.icon} ${hovering ? styles.hovering : ''}`}
              >
                <FileImageOutlined />
              </Row>
              <Row
                className={`${styles.title} ${hovering ? styles.hovering : ''}`}
              >
                {(compact === undefined || compact === false) && (
                  <Title level={3}>Ask a question about an assignment</Title>
                )}
                {compact === true && (
                  <Title level={5}>
                    Ask a question about another assignment
                  </Title>
                )}
              </Row>
              <Row
                className={`${styles.subtitle} ${
                  hovering ? styles.hovering : ''
                }`}
              >
                {(compact === undefined || compact === false) && (
                  <Title level={5}>
                    Click or drag an image of an assignment, lecture slide or
                    lab to this area to upload
                  </Title>
                )}
              </Row>
            </>
          )}
          {!(id === null || image === null) && (
            <Image height={200} src={previewUrl} preview={false} />
          )}
        </Dragger>
      </Row>
      <Row>
        {error !== '' && (
          <Row justify="center">
            <Col>
              <Alert
                message="The image was not accepted"
                description={error}
                type="error"
                showIcon
              />
            </Col>
          </Row>
        )}
      </Row>
    </div>
  );
}
