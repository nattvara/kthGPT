import PageFrame from '@/components/page/page-frame/page-frame';
import { registerPageLoad } from '@/matomo';
import { useEffect } from 'react';
import { Typography } from 'antd';
import TableQueue from '@/components/table/table-queue/table-queue';

const { Title } = Typography;

export default function QueuePage() {
  useEffect(() => {
    document.title = 'kthGPT - Queue';
    registerPageLoad();
  }, []);

  return (
    <>
      <PageFrame>
        <>
          <Title level={3}>Current queue of videos for kthGPT to watch</Title>
          <TableQueue />
        </>
      </PageFrame>
    </>
  );
}
