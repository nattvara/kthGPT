import PageFrame from '@/components/page/page-frame/page-frame';
import DeniedTable from '@/components/table/table-denied/table-denied';
import { registerPageLoad } from '@/matomo';
import { useEffect } from 'react';
import { Typography } from 'antd';

const { Title } = Typography;

export default function DeniedPage() {
  useEffect(() => {
    document.title = 'kthGPT - Denied';
    registerPageLoad();
  }, []);

  return (
    <>
      <PageFrame>
        <>
          <Title level={3}>Lectures that where denied by kthGPT</Title>
          <DeniedTable />
        </>
      </PageFrame>
    </>
  );
}
