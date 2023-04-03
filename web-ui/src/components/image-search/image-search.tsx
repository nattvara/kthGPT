import styles from './image-search.less';
import {
  Row,
  Col,
  Alert,
  Upload,
  Image,
  Space,
  Typography,
  notification,
  Tag,
} from 'antd';
import type { UploadProps } from 'antd';
import { useMutation } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import apiClient, {
  makeUrl,
  ServerErrorResponse,
  ServerResponse,
} from '@/http';
import {
  CheckCircleOutlined,
  FileImageOutlined,
  SyncOutlined,
} from '@ant-design/icons';
import {
  emitEvent,
  CATEGORY_IMAGE_SEARCH,
  EVENT_ERROR_RESPONSE,
} from '@/matomo';
import { UploadChangeParam, UploadFile } from 'antd/es/upload';
import { Image as ImageType, Question } from '../search';
import QuestionInput from '../question-input/question-input';
import { Lecture } from '../lecture';
import { PreviewCompact } from '@/components/lecture/preview';
import { history } from 'umi';
import { QuestionAnswer } from './question-answer';

const { Dragger } = Upload;

const { Paragraph } = Typography;

const UPDATE_INTERVAL = 1000;

const DEFAULT_QUERY_STRING = 'Where can I find the answer to this assignment?';

interface ParsingStateType {
  key: string;
  name: string;
  value: null | boolean;
}

interface ImageResponse extends ServerResponse {
  data: ImageType;
}

interface QuestionResponse extends ServerResponse {
  data: Question;
}

export default function ImageSearch() {
  const [id, setId] = useState<null | string>(null);
  const [error, setError] = useState<string>('');
  const [image, setImage] = useState<null | ImageType>(null);
  const [queryString, setQueryString] = useState<string>('');
  const [questionId, setQuestionId] = useState<string>('');
  const [lectures, setLectures] = useState<Lecture[]>([]);
  const [notificationApi, contextHolder] = notification.useNotification();

  const previewUrl = makeUrl(`/search/image/${id}/img`);

  const uploadProps: UploadProps = {
    name: 'file',
    multiple: true,
    action: makeUrl('/search/image'),
    maxCount: 1,
    onChange(info: UploadChangeParam<UploadFile>) {
      const { status } = info.file;
      if (status === 'done') {
        setId(info.file.response.id);
        setError('');
      } else if (status === 'error') {
        emitEvent(CATEGORY_IMAGE_SEARCH, EVENT_ERROR_RESPONSE, 'upload');
        setError(info.file.response.detail);
      }
    },
  };

  const { mutate: fetchImage } = useMutation(
    async () => {
      return await apiClient.get(`/search/image/${id}`);
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
        notificationApi['error']({
          message: 'Failed to get lectures',
          description: err.response.data.detail,
        });
        emitEvent(CATEGORY_IMAGE_SEARCH, EVENT_ERROR_RESPONSE, 'fetchImage');
      },
    }
  );

  const { isLoading: isAskingQuestion, mutate: sendQuestion } = useMutation(
    async () => {
      return await apiClient.post(`/search/image/${id}/questions`, {
        query: queryString,
      });
    },
    {
      onSuccess: (res: QuestionResponse) => {
        const result = {
          data: res.data,
        };
        setLectures(result.data.hits);
        setQuestionId(result.data.id);
      },
      onError: (err: ServerErrorResponse) => {
        console.log(err);
      },
    }
  );

  const askQuestion = async (q: string) => {
    await setQueryString(q);

    if (isAskingQuestion) return;

    sendQuestion();
  };

  const goToLecture = async (lecture: Lecture, newTab = false) => {
    const url = `/questions/lectures/${lecture.public_id}/${lecture.language}`;

    if (newTab) {
      window.open(url, '_blank');
    } else {
      await history.push(url);
    }

    // TODO:
    // emitEvent(
    // );
  };

  let canAskQuestion = false;
  let parsingStates: ParsingStateType[] = [];
  if (image !== null) {
    if (
      image.parse_image_content_ok &&
      image.create_description_en_ok &&
      image.create_description_sv_ok &&
      image.create_search_queries_sv_ok &&
      image.create_search_queries_en_ok
    ) {
      canAskQuestion = true;
    }

    parsingStates = [
      {
        key: 'parse_image_content_ok',
        name: 'Parsing image',
        value: image.parse_image_content_ok,
      },
      {
        key: 'create_description_en_ok',
        name: 'Creating description (english)',
        value: image.create_description_en_ok,
      },
      {
        key: 'create_description_sv_ok',
        name: 'Creating description (swedish)',
        value: image.create_description_sv_ok,
      },
      {
        key: 'create_search_queries_sv_ok',
        name: 'Search terms (swedish)',
        value: image.create_search_queries_sv_ok,
      },
      {
        key: 'create_search_queries_en_ok',
        name: 'Search terms (english)',
        value: image.create_search_queries_en_ok,
      },
    ];
  }

  useEffect(() => {
    if (id !== null) fetchImage();
  }, [id, fetchImage]);

  useEffect(() => {
    const interval = setInterval(() => {
      if (id !== null) fetchImage();
    }, UPDATE_INTERVAL);

    return () => clearInterval(interval);
  }, [id, fetchImage]);

  return (
    <div className={styles.image_search}>
      {contextHolder}
      <Space direction="vertical" style={{ width: '100%' }}>
        <Row>
          {(id === null || image === null) && (
            <Dragger className={styles.dragger} {...uploadProps}>
              <p className="ant-upload-drag-icon">
                <FileImageOutlined />
              </p>
              <p className="ant-upload-text">
                Click or drag image to this area to upload
              </p>
            </Dragger>
          )}
          {!(id === null || image === null) && (
            <Dragger className={styles.dragger} {...uploadProps}>
              <Image height={200} src={previewUrl} preview={false} />
            </Dragger>
          )}
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
        <div className={styles.progress_box}>
          <Space size={[0, 8]} wrap>
            {parsingStates.map((state) => (
              <div key={state.key}>
                {state.value === true && (
                  <Tag icon={<CheckCircleOutlined />} color="success">
                    {state.name}
                  </Tag>
                )}
                {state.value !== true && (
                  <Tag icon={<SyncOutlined spin />} color="processing">
                    {state.name}
                  </Tag>
                )}
              </div>
            ))}
          </Space>
        </div>
        <div className={styles.question_box}>
          <QuestionInput
            language={'en'}
            placeholder={'Enter a question about this image...'}
            disabled={!canAskQuestion}
            defaultQueryString={DEFAULT_QUERY_STRING}
            isAsking={isAskingQuestion}
            examples={[
              {
                titleEn: 'Help me find the answer',
                titleSv: '',
                queryStringEn:
                  'Where can I find the answer to this assignment?',
                queryStringSv: '',
              },
              {
                titleEn: 'Find similar assignments',
                titleSv: '',
                queryStringEn:
                  'Where can I find similar assignments to this question?',
                queryStringSv: '',
              },
            ]}
            huge={false}
            onAsk={(queryString: string) => askQuestion(queryString)}
          />
          {image !== null && (
            <Row className={styles.description}>
              <Paragraph>
                <blockquote>
                  Description (english): {image.description_en}
                </blockquote>
                <blockquote>
                  Description (swedish): {image.description_sv}
                </blockquote>
              </Paragraph>
            </Row>
          )}
          {image !== null && questionId !== null && (
            <Row className={styles.result}>
              <Space direction="vertical" size="large">
                {lectures.map((lecture, index) => {
                  return (
                    <Row key={lecture.public_id + lecture.language}>
                      <Col span={2} className={styles.row_number}>
                        {index + 1}
                      </Col>
                      <Col span={22}>
                        <Row>
                          <PreviewCompact
                            lecture={lecture}
                            onClick={() => goToLecture(lecture)}
                            onMetaClick={() => goToLecture(lecture, true)}
                            onCtrlClick={() => goToLecture(lecture, true)}
                          />
                        </Row>
                        <Row>
                          <QuestionAnswer
                            lecture={lecture}
                            imageId={image.id}
                            questionId={questionId}
                          />
                        </Row>
                      </Col>
                    </Row>
                  );
                })}
              </Space>
            </Row>
          )}
        </div>
      </Space>
    </div>
  );
}
