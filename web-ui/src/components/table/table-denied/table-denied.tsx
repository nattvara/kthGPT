import { Table, Image, Typography } from 'antd';
import { notification } from 'antd';
import { useEffect, useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import apiClient, { ServerErrorResponse, ServerResponse } from '@/http';
import { Lecture } from '@/types/lecture';
import styles from './table-denied.less';
import { ColumnsType } from 'antd/es/table';
import svFlag from '@/assets/flag-sv.svg';
import enFlag from '@/assets/flag-en.svg';
import kthLogo from '@/assets/kth.svg';
import youtubeLogo from '@/assets/youtube.svg';
import { emitEvent } from '@/matomo';
import { CATEGORY_TABLE_DENIED, EVENT_ERROR_RESPONSE } from '@/matomo/events';

const { Link } = Typography;

const UPDATE_INTERVAL = 5000;

const columns: ColumnsType<Lecture> = [
  {
    title: 'Source',
    dataIndex: 'source',
    render: (source: string) => {
      let icon = '';
      if (source === 'youtube') {
        icon = youtubeLogo;
      } else if (source === 'kth') {
        icon = kthLogo;
      }
      return (
        <Image src={icon} height={30} className={styles.logo} preview={false} />
      );
    },
  },
  {
    title: 'Title',
    dataIndex: 'title',
  },
  {
    title: 'Content Link',
    dataIndex: 'content_link',
    render: (content_link: string) => (
      <>
        <Link href={content_link} target="_blank">
          {content_link}
        </Link>
      </>
    ),
  },
  {
    title: 'Language',
    dataIndex: 'language',
    render: (val: string) => {
      let flagIcon = '';
      if (val === 'sv') {
        flagIcon = svFlag;
      } else if (val === 'en') {
        flagIcon = enFlag;
      }
      return (
        <Image
          src={flagIcon}
          height={30}
          className={styles.flag}
          preview={false}
        />
      );
    },
  },
  {
    title: 'Added At',
    dataIndex: 'created_at',
    render: (val: string) => {
      const d = new Date(val);
      const date = d.toDateString();
      const time = d.toLocaleTimeString('sv');
      return (
        <>
          {date}, {time}
        </>
      );
    },
  },
  {
    title: 'State',
    dataIndex: 'state',
    render: (val: string) => {
      val = val.replaceAll('_', ' ');

      const titleCase = val
        .toLowerCase()
        .replace(/(^|\s)\S/g, (match) => match.toUpperCase());
      return <>{titleCase}</>;
    },
  },
];

interface LectureResponse extends ServerResponse {
  data: Lecture[];
}

export default function TableDenied() {
  const [lectures, setLectures] = useState<Lecture[]>([]);
  const [notificationApi, contextHolder] = notification.useNotification();

  const { mutate: fetchLectures } = useMutation(
    async () => {
      return await apiClient.get(`/lectures?summary=true&only_denied=true`);
    },
    {
      onSuccess: (res: LectureResponse) => {
        const result = {
          status: res.status + '-' + res.statusText,
          headers: res.headers,
          data: res.data,
        };
        for (let i = 0; i < res.data.length; i++) {
          const lecture = res.data[i];
          lecture.combined_public_id_and_lang = `${lecture.public_id}/${lecture.language}`;
          lecture['key'] = lecture.combined_public_id_and_lang;
        }
        setLectures(result.data as Lecture[]);
      },
      onError: (err: ServerErrorResponse) => {
        notificationApi['error']({
          message: 'Failed to get lectures',
          description: err.response.data.detail,
        });
        emitEvent(CATEGORY_TABLE_DENIED, EVENT_ERROR_RESPONSE, 'fetchLectures');
      },
    }
  );

  useEffect(() => {
    fetchLectures();
  }, [fetchLectures]);

  useEffect(() => {
    const interval = setInterval(() => {
      fetchLectures();
    }, UPDATE_INTERVAL);

    return () => clearInterval(interval);
  }, [fetchLectures]);

  return (
    <>
      {contextHolder}
      <Table columns={columns} dataSource={lectures} />
    </>
  );
}
