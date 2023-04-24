import styles from './lecture-list.less';
import { Lecture } from '@/types/lecture';
import { Row, Input, Typography, Col, Button } from 'antd';
import { useMutation } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import apiClient, { ServerErrorResponse, ServerResponse } from '@/http';
import { history } from 'umi';
import { LecturePreviewCompact } from '@/components/lecture/lecture-preview/lecture-preview';
import { emitEvent } from '@/matomo';
import { SearchResultLoading } from '@/components/search/search-result-loading/search-result-loading';
import {
  ACTION_NONE,
  CATEGORY_LECTURE_LIST,
  EVENT_ERROR_RESPONSE,
  EVENT_GOTO_LECTURE,
  EVENT_LOAD_MORE,
  EVENT_SEARCHED,
} from '@/matomo/events';

const { Search } = Input;

const { Paragraph } = Typography;

const AUTO_UPDATE_INTERVAL = 10000;

const PAGINATE_AFTER = 25;

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
  const [lastQuery, setLastQuery] = useState<string>('');
  const [lastCourseCode, setLastCourseCode] = useState<string>('');
  const [lectures, setLectures] = useState<Lecture[]>([]);
  const [limit, setLimit] = useState<number>(PAGINATE_AFTER);

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
          if (
            lectureQuery !== lastQuery ||
            lastCourseCode !== courseCode ||
            firstLoad
          ) {
            setLimit(Math.min(PAGINATE_AFTER, result.data.length));
          }
          setFirstLoad(false);
          setLastQuery(lectureQuery);
          setLastCourseCode(courseCode);
        },
        onError: (err: ServerErrorResponse) => {
          console.log(err);
          emitEvent(
            CATEGORY_LECTURE_LIST,
            EVENT_ERROR_RESPONSE,
            'doLectureSearch'
          );
        },
      }
    );

  const searchLectures = async (query: string) => {
    await setLectureQuery(query);
    doLectureSearch();
    emitEvent(CATEGORY_LECTURE_LIST, EVENT_SEARCHED, query);
  };

  const loadMore = () => {
    if (limit + PAGINATE_AFTER > lectures.length) {
      setLimit(lectures.length);
    } else {
      setLimit(limit + PAGINATE_AFTER);
    }

    emitEvent(CATEGORY_LECTURE_LIST, EVENT_LOAD_MORE, ACTION_NONE);
  };

  const goToLecture = async (lecture: Lecture, newTab = false) => {
    const url = `/lectures/${lecture.public_id}/${lecture.language}/questions`;

    if (newTab) {
      window.open(url, '_blank');
    } else {
      await history.push(url);
    }

    emitEvent(
      CATEGORY_LECTURE_LIST,
      EVENT_GOTO_LECTURE,
      lecture.title === null ? ACTION_NONE : lecture.title
    );
  };

  useEffect(() => {
    searchLectures('');

    if (courseCode !== lastCourseCode) {
      setFirstLoad(true);
    }
  }, [courseCode, lastCourseCode]); // eslint-disable-line react-hooks/exhaustive-deps

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

      {!firstLoad && (
        <Row className={styles.result_container}>
          {isSearchingLectures && firstLoad && (
            <SearchResultLoading size={4} min={1} max={100} />
          )}
          <div className={styles.result_inner_container}>
            {lectures.map((lecture, index) => {
              if (index + 1 > limit) {
                return <div key={lecture.public_id + lecture.language}></div>;
              }

              return (
                <Row
                  key={lecture.public_id + lecture.language}
                  className={styles.item}
                >
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
          </div>

          <div className={styles.load_more}>
            <Row justify="center" className={styles.full_width}>
              <Col>
                <Button
                  onClick={() => loadMore()}
                  type="primary"
                  key="btn"
                  size="large"
                  disabled={lectures.length <= limit}
                >
                  Load {PAGINATE_AFTER} more hits
                </Button>
              </Col>
            </Row>
            <Row justify="center" className={styles.hits}>
              <Paragraph>
                Showing {limit} / {lectures.length} lectures
              </Paragraph>
            </Row>
          </div>
        </Row>
      )}
    </>
  );
}
