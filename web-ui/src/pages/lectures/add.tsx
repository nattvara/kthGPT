import PageFrame from '@/components/page/page-frame/page-frame';
import { registerPageLoad } from '@/matomo';
import { Col, Row } from 'antd';
import { useEffect } from 'react';
import LectureAddNewForm from '@/components/lecture/lecture-add-new-form/lecture-add-new-form';

export default function IndexPage() {
  useEffect(() => {
    document.title = 'OpenUni.AI | Add Lecture';
    registerPageLoad();
  }, []);

  return (
    <>
      <PageFrame
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
              <LectureAddNewForm />
            </Col>
          </Row>
        </>
      </PageFrame>
    </>
  );
}
