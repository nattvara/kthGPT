import { FileTextOutlined, GithubOutlined } from '@ant-design/icons';
import styles from './page-frame.less';
import {
  Space,
  Row,
  Col,
  Layout,
  Image,
  Button,
  Typography,
  Divider,
  Breadcrumb,
} from 'antd';
import kthLogo from '../../../assets/logo.svg';
import { history } from 'umi';
import { buildDate, isProduction } from '@/version';
import PageBack from '../page-back/page-back';
import {
  ACTION_NONE,
  CATEGORY_PAGE_FRAME,
  EVENT_GOTO_GITHUB,
} from '@/matomo/events';
import { emitEvent } from '@/matomo';

const { Link } = Typography;

const GITHUB_URL = 'https://github.com/nattvara/kthGPT';

export interface BreadcrumbItem {
  href?: string;
  title: string;
}

interface PageFrameProps {
  showDescription?: boolean;
  showBack?: boolean;
  breadcrumbs?: BreadcrumbItem[];
  children: JSX.Element;
}

function PageFrame(props: PageFrameProps) {
  const { showDescription, showBack, breadcrumbs, children } = props;

  const goToGithub = () => {
    window.open(GITHUB_URL, '_blank');
    emitEvent(CATEGORY_PAGE_FRAME, EVENT_GOTO_GITHUB, ACTION_NONE);
  };

  return (
    <>
      <Row>
        <Col span={24}>
          <div className={styles.hero}>
            <Row justify={'center'}>
              <Space
                className={styles.logo_container}
                direction="horizontal"
                size="small"
                onClick={(e) => {
                  if (e.metaKey) return window.open('/', '_blank');
                  if (e.ctrlKey) return window.open('/', '_blank');
                  history.push('/');
                }}
              >
                <Image
                  height={100}
                  width={100}
                  src={kthLogo}
                  className={`${styles.logo} ${
                    !isProduction ? styles.development : ''
                  }`}
                  preview={false}
                />
                <h1 className={styles.huge}>kthGPT</h1>
              </Space>
            </Row>
            {showDescription && (
              <>
                <h1 className={styles.subtitle}>
                  Ask GPT-3 questions about KTH lectures
                </h1>
                <Row className={styles.subtitle} justify="center">
                  <Col className={styles.header_btn}>
                    <Button type="dashed" onClick={() => goToGithub()}>
                      <GithubOutlined /> Source Code
                    </Button>
                  </Col>
                  <Col className={styles.header_btn}>
                    <Link href="/about">
                      <Button type="dashed">
                        <FileTextOutlined /> About
                      </Button>
                    </Link>
                  </Col>
                  <Col className={styles.header_btn}>
                    <Link
                      href="https://github.com/nattvara/kthGPT/releases"
                      target="_blank"
                    >
                      <Button type="dashed">
                        {isProduction && (
                          <>
                            kthGPT <strong>{buildDate}</strong> Version
                          </>
                        )}
                        {!isProduction && <>Development build</>}
                      </Button>
                    </Link>
                  </Col>
                </Row>
              </>
            )}
          </div>
        </Col>
      </Row>

      {showBack === true && (
        <Row>
          <PageBack></PageBack>
        </Row>
      )}

      <Row className={styles.breadcrumbs_container}>
        <Divider orientation="left">
          <div className={styles.breadcrumbs}>
            <Breadcrumb>
              <Breadcrumb.Item href="/">Home</Breadcrumb.Item>
              {breadcrumbs &&
                breadcrumbs.map((b, index) =>
                  b.href === undefined ? (
                    <Breadcrumb.Item key={index}>{b.title}</Breadcrumb.Item>
                  ) : (
                    <Breadcrumb.Item key={index} href={b.href}>
                      {b.title}
                    </Breadcrumb.Item>
                  )
                )}
            </Breadcrumb>
          </div>
        </Divider>
      </Row>

      <Layout className={styles.main}>
        <Layout className={styles.noBg}>{children}</Layout>
      </Layout>
    </>
  );
}

PageFrame.defaultProps = {
  showDescription: true,
};

export default PageFrame;
