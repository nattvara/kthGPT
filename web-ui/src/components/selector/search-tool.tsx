import styles from './search-tool.less';
import { Lecture } from '@/components/lecture';
import { Row, Input, Space, Col } from 'antd';
import { useMutation } from '@tanstack/react-query';
import { useState } from 'react';
import apiClient, { ServerErrorResponse, ServerResponse } from '@/http';
import { history } from 'umi';
import { PreviewCompact } from '../preview';
import {
  emitEvent,
  EVENT_ERROR_RESPONSE,
  CATEGORY_SEARCH_TOOL,
  EVENT_GOTO_LECTURE,
} from '@/matomo';
import { HighlightText } from './highlight-text';

const { Search } = Input;

interface LectureResponse extends ServerResponse {
  data: Lecture[];
}

export default function SearchTool() {
  const [query, setQuery] = useState<string>('');
  const [lectures, setLectures] = useState<Lecture[]>([]);

  const { isLoading: isSearching, mutate: doSearch } = useMutation(
    async () => {
      return await apiClient.post('/search/lecture', {
        query,
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
        emitEvent(CATEGORY_SEARCH_TOOL, EVENT_ERROR_RESPONSE, 'doSearch');
      },
    }
  );

  const search = async (query: string) => {
    await setQuery(query);
    doSearch();
  };

  const goToLecture = async (lecture: Lecture, newTab = false) => {
    const url = `/questions/lectures/${lecture.public_id}/${lecture.language}`;

    if (newTab) {
      window.open(url, '_blank');
    } else {
      await history.push(url);
    }

    emitEvent(
      CATEGORY_SEARCH_TOOL,
      EVENT_GOTO_LECTURE,
      `${lecture.public_id}/${lecture.language}`
    );
  };

  return (
    <>
      <Row>
        <Search
          placeholder="Search for anything said in any lecture"
          size="large"
          value={query}
          loading={isSearching}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
            const val = e.target.value;
            search(val);
          }}
        />
      </Row>
      <Row className={styles.result}>
        <Space direction="vertical" size="large">
          {lectures.map((lecture, index) => {
            return (
              <Row key={lecture.public_id + lecture.language}>
                <Col span={2} className={styles.row_number}>
                  {index + 1}
                </Col>
                <Col span={22}>
                  <Row>
                    <PreviewCompact
                      lecture={lecture}
                      onClick={() => goToLecture(lecture)}
                      onMetaClick={() => goToLecture(lecture, true)}
                      onCtrlClick={() => goToLecture(lecture, true)}
                    />
                  </Row>
                  <Row>
                    {lecture.highlight !== null && (
                      <HighlightText
                        highlight={lecture.highlight}
                      ></HighlightText>
                    )}
                  </Row>
                </Col>
              </Row>
            );
          })}
        </Space>
      </Row>
    </>
  );
}
