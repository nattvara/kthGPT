import { Lecture } from '@/types/lecture';
import { useMutation } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import apiClient, { ServerErrorResponse, ServerResponse } from '@/http';
import { Alert, notification, Typography } from 'antd';
import {
  CATEGORY_LECTURE_QUEUE_SUMMARY,
  EVENT_ERROR_RESPONSE,
} from '@/matomo/events';
import { emitEvent } from '@/matomo';

const { Link } = Typography;

const UPDATE_QUEUE_INTERVAL = 10000;

interface LecturesResponse extends ServerResponse {
  data: Lecture[];
}

export default function LectureQueueSummary() {
  const [unfinishedLectures, setUnfinishedLectures] = useState<Lecture[]>([]);
  const [notificationApi, contextHolder] = notification.useNotification();

  const { mutate: fetchUnfinishedLectures } = useMutation(
    async () => {
      return await apiClient.get(`/lectures?summary=true&only_unfinished=true`);
    },
    {
      onSuccess: (res: LecturesResponse) => {
        const result = {
          status: res.status + '-' + res.statusText,
          headers: res.headers,
          data: res.data,
        };
        setUnfinishedLectures(result.data);
      },
      onError: (err: ServerErrorResponse) => {
        notificationApi['error']({
          message: 'Failed to get lecture queue',
          description: err.response.data.detail,
        });
        emitEvent(
          CATEGORY_LECTURE_QUEUE_SUMMARY,
          EVENT_ERROR_RESPONSE,
          'fetchUnfinishedLectures'
        );
      },
    }
  );

  useEffect(() => {
    fetchUnfinishedLectures();
  }, [fetchUnfinishedLectures]);

  useEffect(() => {
    const interval = setInterval(() => {
      fetchUnfinishedLectures();
    }, UPDATE_QUEUE_INTERVAL);

    return () => clearInterval(interval);
  }, [fetchUnfinishedLectures]);

  return (
    <>
      {contextHolder}
      {unfinishedLectures.length - 1 > 0 && (
        <Alert
          message={
            <>
              OpenUni.AI has limited capacity. Currently there is
              <strong> {unfinishedLectures.length - 1} </strong>
              other lectures being watched. view the progress
              <Link href="/info/queue" target="_blank">
                <strong> here </strong>
              </Link>
            </>
          }
          type="info"
          showIcon
        />
      )}
    </>
  );
}
