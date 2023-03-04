import { GithubOutlined } from '@ant-design/icons';
import styles from './frame.less';
import { Space, Row, Col, Layout, Image, Button } from 'antd';
import kthLogo from '../../assets/logo.svg';
import Progress from './progress';
import { history } from 'umi';

const GITHUB_URL = 'https://github.com/nattvara/kthGPT';

interface FrameProps {
  step?: number;
  showDescription?: boolean;
  children: JSX.Element;
}

function Frame(props: FrameProps) {
  const { step, showDescription, children } = props;

  const goToGithub = () => {
    window.open(GITHUB_URL, '_blank');
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
                  className={styles.logo}
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
                <p className={styles.subtitle}>
                  <Button type="dashed" onClick={() => goToGithub()}>
                    <GithubOutlined /> Source Code
                  </Button>
                </p>
              </>
            )}
          </div>
        </Col>
      </Row>

      <Layout className={styles.main}>
        {step !== undefined && <Progress step={step}></Progress>}

        <Layout className={styles.noBg}>{children}</Layout>
      </Layout>
    </>
  );
}

Frame.defaultProps = {
  showDescription: true,
};

export default Frame;
