import Frame from '@/components/page/frame/frame';
import QueueTable from '@/components/tables/queue-table/queue-table';
import { registerPageLoad } from '@/matomo';
import { useEffect } from 'react';
import { Typography } from 'antd';

const { Title } = Typography;

export default function QueuePage() {
  useEffect(() => {
    document.title = 'kthGPT - Queue';
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
