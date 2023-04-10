import styles from './lecture-list.less';
import { Lecture } from '@/types/lecture';
import { Row, Input, Space, Col } from 'antd';
import { useMutation } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import apiClient, { ServerErrorResponse, ServerResponse } from '@/http';
import { history } from 'umi';
import { LecturePreviewCompact } from '@/components/lecture/lecture-preview/lecture-preview';
import {
  CATEGORY_COURSE_BROWSER,
  emitEvent,
  EVENT_GOTO_LECTURE,
  EVENT_ERROR_RESPONSE,
} from '@/matomo';
import { SearchResultLoading } from '@/components/search/search-result-loading/search-result-loading';

const { Search } = Input;

const AUTO_UPDATE_INTERVAL = 10000;

interface LectureResponse extends ServerResponse {
  data: Lecture[];
}

interface LectureListProps {
  courseCode: string;
  source?: string;
}

export default function LectureList(props: LectureListProps) {
  const { courseCode, source } = props;

  const [firstLoad, setFirstLoad] = useState<boolean>(true);
  const [lectureQuery, setLectureQuery] = useState<string>('');
  const [lectures, setLectures] = useState<Lecture[]>([]);

  const { isLoading: isSearchingLectures, mutate: doLectureSearch } =
    useMutation(
      async () => {
        let params = {};
        if (source !== undefined) {
          params = {
            query: lectureQuery,
            source: source,
          };
        } else {
          params = {
            query: lectureQuery,
            source: source,
          };
        }

        return await apiClient.post(`/search/course/${courseCode}`, params);
      },
      {
        onSuccess: (res: LectureResponse) => {
          const result = {
            data: res.data,
          };
          setLectures(result.data);
          setFirstLoad(false);
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
    const url = `/lectures/${lecture.public_id}/${lecture.language}/questions`;

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
        {isSearchingLectures && firstLoad && (
          <SearchResultLoading size={4} min={1} max={100} />
        )}
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
                  <LecturePreviewCompact
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
