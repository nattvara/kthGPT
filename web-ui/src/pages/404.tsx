import PageFrame from '@/components/page/page-frame/page-frame';
import { registerPageLoad } from '@/matomo';
import { Result, Button, Row, Col } from 'antd';
import { useEffect } from 'react';
import { history } from 'umi';
import styles from './404.less';

export default function NotFoundPage() {
  useEffect(() => {
    document.title = 'OpenUni.AI | Not Found';
    registerPageLoad();
  }, []);

  return (
    <>
      <PageFrame showDescription={false}>
        <Result
          status="404"
          className={styles.result}
          title={
            <>
              <Row justify="center" align="middle">
                <Col>
                  <h1 className={styles.huge}>This page was not found</h1>
                </Col>
              </Row>
              <Row justify="center" align="middle">
                <Button
                  onClick={() => history.push('/')}
                  type="primary"
                  key="btn"
                  size="large"
                >
                  Go to OpenUni.AI
                </Button>
              </Row>
            </>
          }
        />
      </PageFrame>
    </>
  );
}
