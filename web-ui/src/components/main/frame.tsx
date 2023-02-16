import { GithubOutlined } from '@ant-design/icons';
import styles from './frame.less';
import {
  Space,
  Row,
  Col,
  Layout,
  Image,
  Button,
} from 'antd';
import kthLogo from '../../assets/logo.svg';
import Progress from './progress';

const GITHUB_URL = 'https://github.com/nattvara/kthGPT';


export default function Frame(props: {step: number, children: JSX.Element}) {
  const {step, children} = props;

  const goToGithub = () => {
    window.open(GITHUB_URL, '_blank')
  };

  return (
    <>
      <Row>
        <Col span={24}>
          <div className={styles.hero}>
            <Row justify={'center'}>
              <Space direction='horizontal' size='small'>
                <Image
                  height={100}
                  src={kthLogo}
                  className={styles.logo}
                  preview={false}
                />
                <h1 className={styles.huge}>kthGPT</h1>
              </Space>
            </Row>
            <h1 className={styles.subtitle}>Ask GPT-3 questions about KTH lectures</h1>
            <p className={styles.subtitle}>
              <Button type='dashed' onClick={() => goToGithub()}><GithubOutlined /> Source Code</Button>
            </p>
          </div>
        </Col>
      </Row>

      <Layout className={styles.main}>
        <Progress step={step}></Progress>

        <Layout className={styles.noBg}>
          {children}
        </Layout>
      </Layout>
    </>
  );
}
