import Frame from '@/components/page/frame/frame';
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
      <Frame>
        <>
          <Title level={3}>Lectures that has failed</Title>
          <TableFailures />
        </>
      </Frame>
    </>
  );
}
