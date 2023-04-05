import styles from './add.less';
import Frame from '@/components/page/frame/frame';
import { registerPageLoad } from '@/matomo';
import { Col, Row } from 'antd';
import { useEffect, useState } from 'react';
import AddLecture from '@/components/input/add-lecture/add-lecture';

export default function IndexPage() {
  useEffect(() => {
    registerPageLoad();
  }, []);

  return (
    <>
      <Frame
        showBack={true}
        breadcrumbs={[
          {
            title: 'Add New Lecture',
          },
        ]}
      >
        <>
          <Row>
            <Col sm={0} md={4}></Col>
            <Col sm={24} md={16}>
              <AddLecture />
            </Col>
          </Row>
        </>
      </Frame>
    </>
  );
}
