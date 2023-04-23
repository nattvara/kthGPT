import styles from './page-back.less';
import { LeftOutlined } from '@ant-design/icons';
import { Button, Col, Row, Typography } from 'antd';
import { history } from 'umi';
import {
  ACTION_NONE,
  CATEGORY_PAGE_FRAME,
  EVENT_GO_BACK,
} from '@/matomo/events';
import { emitEvent } from '@/matomo';

const { Link } = Typography;

export default function PageBack() {
  const goBack = () => {
    history.back();
    emitEvent(CATEGORY_PAGE_FRAME, EVENT_GO_BACK, ACTION_NONE);
  };

  return (
    <>
      <Row justify="start" className={styles.container}>
        <Col sm={24} md={16}>
          <Link onClick={() => goBack()}>
            <Button type="primary">
              <LeftOutlined /> Back
            </Button>
          </Link>
        </Col>
      </Row>
    </>
  );
}
