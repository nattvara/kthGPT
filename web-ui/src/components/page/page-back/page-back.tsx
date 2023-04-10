import styles from './page-back.less';
import { LeftOutlined } from '@ant-design/icons';
import { Button, Col, Row, Typography } from 'antd';
import { history } from 'umi';

const { Link } = Typography;

export default function PageBack() {
  return (
    <>
      <Row justify="start" className={styles.container}>
        <Col sm={24} md={16}>
          <Link onClick={() => history.back()}>
            <Button type="primary">
              <LeftOutlined /> Back
            </Button>
          </Link>
        </Col>
      </Row>
    </>
  );
}
