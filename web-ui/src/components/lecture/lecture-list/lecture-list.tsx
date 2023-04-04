import styles from './lecture-list.less';
import { Lecture } from '@/types/lecture';
import { Row, Input, Space, Col } from 'antd';
import { useMutation } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import apiClient, { ServerErrorResponse, ServerResponse } from '@/http';
import { history } from 'umi';
import { PreviewCompact } from '@/components/lecture/preview/preview';
import {
  CATEGORY_COURSE_BROWSER,
  emitEvent,
  EVENT_GOTO_LECTURE,
  EVENT_ERROR_RESPONSE,
} from '@/matomo';

const { Search } = Input;

const AUTO_UPDATE_INTERVAL = 10000;

interface LectureResponse extends ServerResponse {
  data: Lecture[];
}

interface LectureListProps {
  courseCode: string;
  source: string;
}

export default function LectureList(props: LectureListProps) {
  const { courseCode, source } = props;

  const [lectureQuery, setLectureQuery] = useState<string>('');
  const [lectures, setLectures] = useState<Lecture[]>([]);

  const { isLoading: isSearchingLectures, mutate: doLectureSearch } =
    useMutation(
      async () => {
        return await apiClient.post(`/search/course/${courseCode}`, {
          query: lectureQuery,
          source: source,
        });
      },
      {
        onSuccess: (res: LectureResponse) => {
          const result = {
            data: res.data,
          };
          setLectures(result.data);
        },
        onError: (err: ServerErrorResponse) => {
          console.log(err);
          emitEvent(
            CATEGORY_COURSE_BROWSER,
            EVENT_ERROR_RESPONSE,
            'doLectureSearch'
          );
        },
      }
    );

  const searchLectures = async (query: string) => {
    await setLectureQuery(query);
    doLectureSearch();
  };

  const goToLecture = async (lecture: Lecture, newTab = false) => {
    const url = `/questions/lectures/${lecture.public_id}/${lecture.language}`;

    if (newTab) {
      window.open(url, '_blank');
    } else {
      await history.push(url);
    }

    emitEvent(
      CATEGORY_COURSE_BROWSER,
      EVENT_GOTO_LECTURE,
      `${lecture.public_id}/${lecture.language}`
    );
  };

  useEffect(() => {
    searchLectures('');
  }, [courseCode]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    const interval = setInterval(() => {
      doLectureSearch();
    }, AUTO_UPDATE_INTERVAL);

    return () => clearInterval(interval);
  }, [doLectureSearch]);

  return (
    <>
      <Row className={styles.search_bar}>
        <Search
          style={{ width: '100%' }}
          placeholder="Search for a lecture..."
          size="large"
          value={lectureQuery}
          loading={isSearchingLectures}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
            const val = e.target.value;
            searchLectures(val);
          }}
        />
      </Row>

      <Row className={styles.result_container}>
        <Space
          direction="vertical"
          size="large"
          className={styles.result_inner_container}
        >
          {lectures.map((lecture, index) => {
            return (
              <Row key={lecture.public_id + lecture.language}>
                <Col span={2} className={styles.row_number}>
                  {index + 1}
                </Col>
                <Col span={22}>
                  <PreviewCompact
                    lecture={lecture}
                    onClick={() => goToLecture(lecture)}
                    onMetaClick={() => goToLecture(lecture, true)}
                    onCtrlClick={() => goToLecture(lecture, true)}
                  />
                </Col>
              </Row>
            );
          })}
        </Space>
      </Row>
    </>
  );
}
