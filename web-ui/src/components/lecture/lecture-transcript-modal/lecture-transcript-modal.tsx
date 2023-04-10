import { FileTextOutlined } from '@ant-design/icons';
import styles from './lecture-transcript-modal.less';
import { Button, Modal } from 'antd';
import { useMutation } from '@tanstack/react-query';
import { useState } from 'react';
import apiClient, { ServerErrorResponse } from '@/http';
import { Lecture } from '@/types/lecture';
import { emitEvent, CATEGORY_QUESTIONS, EVENT_ERROR_RESPONSE } from '@/matomo';
import { SearchResultLoading } from '@/components/search/search-result-loading/search-result-loading';

interface TranscriptResponse {
  data: string;
  headers: object;
  status: number;
  statusText: string;
}

interface LectureTranscriptProps {
  lecture: Lecture;
}

export default function LectureTranscript(props: LectureTranscriptProps) {
  const { lecture } = props;

  const [showTranscript, setShowTranscript] = useState<boolean>(false);
  const [transcript, setTranscript] = useState<string>('');

  const { isLoading: isFetchingTranscript, mutate: fetchTranscript } =
    useMutation(
      async () => {
        setTranscript('');
        return await apiClient.get(
          `/lectures/${lecture.public_id}/${lecture.language}/transcript`
        );
      },
      {
        onSuccess: (res: TranscriptResponse) => {
          const result = {
            status: res.status + '-' + res.statusText,
            headers: res.headers,
            data: res.data,
          };
          setTranscript(result.data);
        },
        onError: (err: ServerErrorResponse) => {
          console.error(err);
          emitEvent(
            CATEGORY_QUESTIONS,
            EVENT_ERROR_RESPONSE,
            'fetchTranscript'
          );
        },
      }
    );

  return (
    <>
      <Button
        size="large"
        type="default"
        onClick={() => {
          fetchTranscript();
          setShowTranscript(true);
        }}
      >
        <FileTextOutlined /> Show transcript
      </Button>

      <Modal
        title="Lecture Transcript"
        open={showTranscript}
        onCancel={() => setShowTranscript(false)}
        onOk={() => setShowTranscript(false)}
        cancelText="Close"
        width={1000}
      >
        <div className={styles.transcript}>
          {isFetchingTranscript && (
            <SearchResultLoading size={4} min={1} max={100} />
          )}
          {!isFetchingTranscript && (
            <>
              <pre className={styles.response}>{transcript}</pre>
            </>
          )}
        </div>
      </Modal>
    </>
  );
}
