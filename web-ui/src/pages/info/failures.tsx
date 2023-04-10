import PageFrame from '@/components/page/page-frame/page-frame';
import { registerPageLoad } from '@/matomo';
import { useEffect } from 'react';
import { Typography } from 'antd';
import TableFailures from '@/components/table/table-failures/table-failures';

const { Title } = Typography;

export default function FailuresPage() {
  useEffect(() => {
    document.title = 'kthGPT - Failures';
    registerPageLoad();
  }, []);

  return (
    <>
      <PageFrame>
        <>
          <Title level={3}>Lectures that has failed</Title>
          <TableFailures />
        </>
      </PageFrame>
    </>
  );
}
