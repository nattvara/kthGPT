import Frame from '@/components/main/frame';
import QueueTable from '@/components/tables/queue-table';
import { registerPageLoad } from '@/matomo';
import { useEffect } from 'react';
import { Typography } from 'antd';

const { Title } = Typography;

export default function QueuePage() {
  useEffect(() => {
    registerPageLoad();
  }, []);

  return (
    <>
      <Frame>
        <>
          <Title level={3}>Current queue of videos for kthGPT to watch</Title>
          <QueueTable />
        </>
      </Frame>
    </>
  );
}
