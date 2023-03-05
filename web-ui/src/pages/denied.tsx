import Frame from '@/components/main/frame';
import DeniedTable from '@/components/tables/denied-table';
import { registerPageLoad } from '@/matomo';
import { useEffect } from 'react';
import { Typography } from 'antd';

const { Title } = Typography;

export default function DeniedPage() {
  useEffect(() => {
    registerPageLoad();
  }, []);

  return (
    <>
      <Frame>
        <>
          <Title level={3}>Lectures that where denied by kthGPT</Title>
          <DeniedTable />
        </>
      </Frame>
    </>
  );
}
