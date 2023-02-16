import Frame from '@/components/main/frame';
import {
  Result,
  Button,
  Row,
  Col,
  Tag,
} from 'antd';
import { history } from 'umi';
import styles from './404.less';


export default function IndexPage() {

  return (
    <>
      <Frame showDescription={false}>
        <Result
        status='404'
        className={styles.result}
        title={<>
          <Row justify='center' align='middle'>
            <Col><h1 className={styles.huge}>This page was not found</h1></Col>
          </Row>
          <Row justify='center' align='middle'>
            <Button
              onClick={() => history.push('/')}
              type='primary'
              key='btn'
              size='large'>
              Go to kthgpt.com
            </Button>
          </Row>
        </>}
        />
      </Frame>
    </>
  );
}
