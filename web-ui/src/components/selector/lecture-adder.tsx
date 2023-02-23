import styles from './lecture-adder.less';
import { Course, Lecture } from '@/components/lecture';
import {
  Row,
  Input,
  Space,
  Col,
  Button,
  Typography,
  Popover,
  Card,
  Image,
  InputRef,
  Form,
  Alert,
} from 'antd';
import {
  BulbOutlined,
  LeftOutlined,
  PlayCircleOutlined,
  RightOutlined,
  VideoCameraOutlined
} from '@ant-design/icons';
import { useMutation } from '@tanstack/react-query';
import { useEffect, useRef, useState } from 'react';
import apiClient from '@/http';
import { history } from 'umi';
import { PreviewCompact } from '../preview';
import kthLogo from '@/assets/kth.svg';
import youtubeLogo from '@/assets/youtube.svg';
import svFlag from '@/assets/flag-sv.svg';
import enFlag from '@/assets/flag-en.svg';
import {
  emitEvent,
  EVENT_SUBMIT_URL,
} from '@/matomo';


const { Title, Link, Paragraph } = Typography;
const { Meta } = Card;

const SOURCE_KTH = 'kth';
const SOURCE_YOUTUBE = 'youtube';

const LANGUAGE_ENGLISH = 'en';
const LANGUAGE_SWEDISH = 'sv';

interface SourcePopoverProps {
  dismiss: Function
  setSource: Function
}

function SourcePopover(props: SourcePopoverProps) {
  const { dismiss, setSource } = props;

  return (
    <>
      <Row justify='center'>
        <Space>
          <Col>
            <Card
              hoverable
              className={styles.source}
              onClick={() => {
                setSource(SOURCE_KTH);
                dismiss();
              }}
              cover={<Image preview={false} src={kthLogo} />}>
              <>
                <Meta title={<div style={{padding: '10px'}}>KTH Play</div>} />
              </>
            </Card>
          </Col>
          <Col>
            <Card
              hoverable
              className={styles.source}
              onClick={() => {
                setSource(SOURCE_YOUTUBE);
                dismiss();
              }}
              cover={<Image preview={false} src={youtubeLogo} />}>
              <>
                <Meta title={<div style={{padding: '10px'}}>YouTube</div>} />
              </>
            </Card>
          </Col>
        </Space>
      </Row>
      <Row justify='center'>
        <Col>
          <Button type='link' onClick={() => dismiss()}>Close</Button>
        </Col>
      </Row>
    </>
  );
}


interface LanguagePopoverProps {
  dismiss: Function
  setLanguage: Function
}

function LanguagePopover(props: LanguagePopoverProps) {
  const { dismiss, setLanguage } = props;

  return (
    <>
      <Row justify='center'>
        <Space>
          <Col>
          <Image
              src={enFlag}
              height={50}
              className={styles.flag}
              preview={false}
              onClick={() => {
                setLanguage(LANGUAGE_ENGLISH);
                dismiss();
              }}
            />
          </Col>
          <Col>
            <Image
              src={svFlag}
              height={50}
              className={styles.flag}
              preview={false}
              onClick={() => {
                setLanguage(LANGUAGE_SWEDISH);
                dismiss();
              }}
            />
          </Col>
        </Space>
      </Row>
      <Row justify='center'>
        <Col>
          <Button type='link' onClick={() => dismiss()}>Close</Button>
        </Col>
      </Row>
    </>
  );
}


interface UrlPopoverProps {
  dismiss: Function
  setUrl: Function
  url: string
  source: string
}

function UrlPopover(props: UrlPopoverProps) {
  const {
    dismiss,
    setUrl,
    url,
    source
  } = props;

  const [ localUrl, setLocalUrl ] = useState<string>('');

  const ref = useRef<InputRef>(null);
  const [ form ] = Form.useForm();

  let placeholder = '';
  if (source === SOURCE_YOUTUBE) {
    placeholder = 'Enter video.. eg. https://www.youtube.com/watch?v=nnkCE...';
  } else if (source === SOURCE_KTH) {
    placeholder = 'Enter video.. eg. https://play.kth.se/media/...';
  } else {
    placeholder = 'Enter video.. eg. https://play.kth.se/media/...'
  }

  const save = async () => {
    await setUrl(localUrl);
    await dismiss();
  };

  useEffect(() => {
    ref.current?.input?.focus();
    setLocalUrl(url);
  }, [url]);

  return (
    <>
      <Space direction='vertical'>
        <Row justify='center'>
          <Col>
            <Form
              form={form}
              layout='vertical'
              autoComplete='off'
            >
              <Form.Item
                name='Lecture URL'
                label='Lecture URL'
                rules={[{ required: true }, { type: 'url', warningOnly: true }]}
              >
                <Input
                  ref={ref}
                  className={styles.url_input}
                  value={localUrl}
                  onChange={e => setLocalUrl(e.target.value)}
                  onPressEnter={() => save()}
                  placeholder={placeholder}
                  prefix={<PlayCircleOutlined />} />
              </Form.Item>
            </Form>
          </Col>
        </Row>
        <Row justify='center'>
          <Col>
            <Button type='link' onClick={() => dismiss()}>Close</Button>
          </Col>
          <Col>
            <Button type='primary' onClick={() => save()}>Save</Button>
          </Col>
        </Row>
      </Space>
    </>
  );
}


interface LectureAdderProps {}


export default function LectureAdder(props: LectureAdderProps) {
  const [ sourceOpen, setSourceOpen ] = useState(false);
  const [ languageOpen, setLanguageOpen ] = useState(false);
  const [ urlOpen, setUrlOpen ] = useState(false);

  const [ source, setSource ] = useState<string>('');
  const [ language, setLanguage ] = useState<string>('');
  const [ url, setUrl ] = useState<string>('');
  const [ error, setError ] = useState<string>('');

  const canSubmit = source !== '' && language !== '' && url !== '';

  const { isLoading: isPosting, mutate: postUrl } = useMutation(
    async () => {
      return await apiClient.post(`/url/${source}`, {
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
        setError(err.response.data.detail);
      },
    }
  );

  const submit = async () => {
    await postUrl();
    emitEvent(EVENT_SUBMIT_URL);
  };

  return (
    <>
      <Paragraph className={styles.paragraph}>
        <Title level={2} className={styles.link}>
          Please watch a lecture on

          <Popover
            style={{ width: 500 }}
            content={
              <SourcePopover
                dismiss={() => setSourceOpen(false)}
                setSource={(s: any) => setSource(s)}
              />
            }
            title='Select where the lecture is hosted'
            trigger='hover'
            open={sourceOpen}
          >
          <Link className={styles.link} onClick={() => {
            setSourceOpen(true);
            setLanguageOpen(false);
            setUrlOpen(false);
          }}>
            {source === '' && <> select source</>}
            {source === SOURCE_KTH && <> KTH Play</>}
            {source === SOURCE_YOUTUBE && <> Youtube</>}
          </Link>
          </Popover>

          <>. The lecture is in </>
          <Popover
            style={{ width: 500 }}
            content={
              <LanguagePopover
                dismiss={() => setLanguageOpen(false)}
                setLanguage={(s: any) => setLanguage(s)}
              />
            }
            title='Select the spoken language of the lecture'
            trigger='hover'
            open={languageOpen}
          >
            <Link className={styles.link} onClick={() => {
              setLanguageOpen(true);
              setSourceOpen(false);
              setUrlOpen(false);
            }}>
              {language === '' && <> select language</>}
              {language === LANGUAGE_SWEDISH && <> Swedish</>}
              {language === LANGUAGE_ENGLISH && <> English</>}
            </Link>
          </Popover>

          <>. The link to the lecture is </>
          <Popover
            style={{ width: 500 }}
            content={
              <UrlPopover
                dismiss={() => setUrlOpen(false)}
                setUrl={(s: any) => setUrl(s)}
                url={url}
                source={source}
              />
            }
            title='Select the spoken language of the lecture'
            trigger='hover'
            open={urlOpen}
          >
            <Link className={styles.link} onClick={() => {
                setLanguageOpen(false);
                setSourceOpen(false);
                setUrlOpen(true);
              }}>
                {url === '' && <> enter URL</>}
                {url !== '' && <> {url}</>}
            </Link>
          </Popover>
        </Title>
      </Paragraph>

      <Space direction='vertical' style={{width: '100%'}} size='large'>
        {error !== '' &&
          <Row justify='center'>
            <Col>
              <Alert
                message='The URL was not accepted'
                description={error}
                type='error'
                showIcon
              />
            </Col>
          </Row>
        }

        <Row justify='center'>
          <Col>
            <Button
              onClick={submit}
              type='primary'
              icon={<BulbOutlined />}
              size='large'
              loading={isPosting}
              disabled={!canSubmit}
            >
              {!isPosting && <>Watch the video</>}
              {isPosting && <>Verifying video URL . . .</>}
            </Button>
          </Col>
        </Row>
      </Space>
    </>
  );
}