import styles from './frame.less';
import {
  Space,
  Row,
  Col,
  Layout,
  Image,
} from 'antd';
import kthLogo from '../../assets/kth.svg';
import Progress from './progress';

export default function Frame(props: {step: number, children: JSX.Element}) {
  const {step, children} = props;

  return (
    <>
      <Row>
        <Col span={24}>
          <div className={styles.hero}>
            <Row justify={'center'}>
              <Space direction="horizontal" size="small">
                <Image
                  height={100}
                  src={kthLogo}
                  preview={false}
                />
                <h1 className={styles.huge}>kthGPT</h1>
              </Space>
            </Row>
            <h1 className={styles.subtitle}>Ask GPT-3 questions about KTH lectures</h1>
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
