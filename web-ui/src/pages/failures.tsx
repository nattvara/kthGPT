import Frame from '@/components/main/frame';
import DeniedTable from '@/components/tables/failures-table/failures-table';
import { registerPageLoad } from '@/matomo';
import { useEffect } from 'react';
import { Typography } from 'antd';

const { Title } = Typography;

export default function FailuresPage() {
  useEffect(() => {
    registerPageLoad();
  }, []);

  return (
    <>
      <Frame>
        <>
          <Title level={3}>Lectures that has failed</Title>
          <DeniedTable />
        </>
      </Frame>
    </>
  );
}
