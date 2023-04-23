import { Button, Col, Result, Row, Space, Typography } from 'antd';
import styles from './search-by-image.less';
import { Hit, Image, Question } from '@/types/search';
import { useEffect, useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import apiClient, { ServerErrorResponse, ServerResponse } from '@/http';
import { LoadingOutlined, ReloadOutlined } from '@ant-design/icons';
import { SearchResultLoading } from '@/components/search/search-result-loading/search-result-loading';
import { history } from 'umi';
import { LecturePreviewCompact } from '@/components/lecture/lecture-preview/lecture-preview';
import { Highlight, Lecture } from '@/types/lecture';
import { TextHighlight } from '@/components/text/text-highlight/text-highlight';
import {
  ACTION_NONE,
  CATEGORY_SEARCH_BY_IMAGE,
  EVENT_ERROR_RESPONSE,
  EVENT_FETCH_ANSWER,
  EVENT_FETCH_RELEVANCE,
  EVENT_GOTO_LECTURE,
  EVENT_LOAD_MORE,
  EVENT_SEARCH_BY_IMAGE,
} from '@/matomo/events';
import { emitEvent } from '@/matomo';

const { Paragraph } = Typography;

interface QuestionResponse extends ServerResponse {
  data: Question;
}

interface AnswerResponse extends ServerResponse {
  data: {
    answer: string;
  };
}

interface RelevanceResponse extends ServerResponse {
  data: {
    relevance: string;
  };
}

const QUESTION =
  'Where in this lecture can I learn how to solve this assignment?';

const HITS_TO_PAGINATE_AFTER = 3;

interface SearchByImageProps {
  image: Image;
}

export default function SearchByImage(props: SearchByImageProps) {
  const { image } = props;

  const [error, setError] = useState<string>('');
  const [hits, setHits] = useState<Hit[]>([]);
  const [searchQuestionId, setSearchQuestionId] = useState<string>('');
  const [notReady, setNotReady] = useState<boolean | null>(null);
  const [limit, setLimit] = useState<number>(HITS_TO_PAGINATE_AFTER);

  const { isLoading: isSearching, mutate: doSearch } = useMutation(
    async () => {
      setNotReady(false);
      return await apiClient.post(
        `/search/image/${image.id}/questions`,
        {
          query: QUESTION,
        },
        {
          timeout: 1000 * 40, // 40s timeout
        }
      );
    },
    {
      onSuccess: (res: QuestionResponse) => {
        const result = {
          data: res.data,
        };
        setError('');
        setHits(result.data.hits);
        setSearchQuestionId(result.data.id);
      },
      onError: (err: ServerErrorResponse) => {
        emitEvent(CATEGORY_SEARCH_BY_IMAGE, EVENT_ERROR_RESPONSE, 'doSearch');

        if (err.code === 'ECONNABORTED') {
          setError('Search took to long to response, try again!');
          emitEvent(
            CATEGORY_SEARCH_BY_IMAGE,
            EVENT_ERROR_RESPONSE,
            'ECONNABORTED'
          );
        }

        if (err.response.status === 409) {
          setNotReady(true);
          return;
        }

        if (err.response && err.response.data.detail) {
          setError(err.response.data.detail);
          emitEvent(
            CATEGORY_SEARCH_BY_IMAGE,
            EVENT_ERROR_RESPONSE,
            err.response.data.detail
          );
          return;
        }

        console.error(err);
        setError(`Something wen't wrong`);
      },
    }
  );

  const search = async () => {
    if (isSearching) return;
    doSearch();
    emitEvent(CATEGORY_SEARCH_BY_IMAGE, EVENT_SEARCH_BY_IMAGE, ACTION_NONE);
  };

  const goToLecture = async (lecture: Lecture, newTab = false) => {
    const url = `/lectures/${lecture.public_id}/${lecture.language}/questions`;

    if (newTab) {
      window.open(url, '_blank');
    } else {
      await history.push(url);
    }

    emitEvent(
      CATEGORY_SEARCH_BY_IMAGE,
      EVENT_GOTO_LECTURE,
      `${lecture.public_id}/${lecture.language}`
    );
  };

  const increaseLimit = () => {
    if (limit + HITS_TO_PAGINATE_AFTER > hits.length) {
      setLimit(hits.length);
    } else {
      setLimit(limit + HITS_TO_PAGINATE_AFTER);
    }

    emitEvent(CATEGORY_SEARCH_BY_IMAGE, EVENT_LOAD_MORE, ACTION_NONE);
  };

  useEffect(() => {
    search();
  }, [image.parse_image_upload_complete]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <>
      {error !== '' && (
        <Row>
          <Col span={24}>
            <>
              <Result
                status="500"
                title="Sorry, something went wrong."
                subTitle={error}
                extra={
                  <Button
                    onClick={() => search()}
                    loading={isSearching}
                    type="primary"
                    size="large"
                  >
                    <ReloadOutlined /> Try Again
                  </Button>
                }
              />
            </>
          </Col>
        </Row>
      )}

      <Row className={styles.full_width}>
        {notReady && (
          <Result
            icon={<LoadingOutlined />}
            title="Once kthGPT has understood the assignment, it will try to find the relevant lectures and display them here"
          />
        )}
      </Row>

      <Row className={styles.full_width}>
        {isSearching && <SearchResultLoading size={6} min={3} max={6} />}
      </Row>

      {!isSearching && (
        <Row className={styles.result}>
          {hits.map((hit, index) => {
            if (index + 1 > limit) {
              return <div key={hit.id}></div>;
            }

            return (
              <Row key={hit.id}>
                <Col span={2} className={styles.row_number}>
                  {index + 1}
                </Col>
                <Col span={22}>
                  <Space direction="vertical" size="middle">
                    <Row>
                      <LecturePreviewCompact
                        lecture={hit.lecture}
                        onClick={() => goToLecture(hit.lecture)}
                        onMetaClick={() => goToLecture(hit.lecture, true)}
                        onCtrlClick={() => goToLecture(hit.lecture, true)}
                      />
                    </Row>
                    <Row>
                      <ImageQuestionHit
                        hit={hit}
                        imageId={image.id}
                        searchQuestionId={searchQuestionId}
                      />
                    </Row>
                  </Space>
                </Col>
              </Row>
            );
          })}
        </Row>
      )}

      {!isSearching && !notReady && (
        <>
          <Row justify="center" className={styles.full_width}>
            <Col>
              <Button
                onClick={() => increaseLimit()}
                type="primary"
                key="btn"
                size="large"
              >
                Load 3 more hits
              </Button>
            </Col>
          </Row>
          <Row justify="center" className={styles.full_width}>
            <Paragraph>
              Showing {limit} / {hits.length} hits
            </Paragraph>
          </Row>
        </>
      )}
    </>
  );
}

interface ImageQuestionHitProps {
  imageId: string;
  searchQuestionId: string;
  hit: Hit;
}

export function ImageQuestionHit(props: ImageQuestionHitProps) {
  const { imageId, searchQuestionId, hit } = props;

  const [answer, setAnswer] = useState<Highlight>();
  const [relevance, setRelevance] = useState<string>('');

  const { isLoading: isLoadingRelevance, mutate: fetchRelevance } = useMutation(
    async () => {
      emitEvent(CATEGORY_SEARCH_BY_IMAGE, EVENT_FETCH_RELEVANCE, ACTION_NONE);
      return await apiClient.get(
        `/search/image/${imageId}/questions/${searchQuestionId}/hits/${hit.id}/relevance`
      );
    },
    {
      onSuccess: (res: RelevanceResponse) => {
        const result = {
          data: res.data,
        };
        setRelevance(result.data.relevance);
      },
      onError: (err: ServerErrorResponse) => {
        console.error(err);
        emitEvent(
          CATEGORY_SEARCH_BY_IMAGE,
          EVENT_ERROR_RESPONSE,
          'fetchAnswer'
        );
      },
    }
  );

  const { isLoading: isLoadingAnswer, mutate: fetchAnswer } = useMutation(
    async () => {
      emitEvent(CATEGORY_SEARCH_BY_IMAGE, EVENT_FETCH_ANSWER, ACTION_NONE);
      return await apiClient.get(
        `/search/image/${imageId}/questions/${searchQuestionId}/hits/${hit.id}/answer`
      );
    },
    {
      onSuccess: (res: AnswerResponse) => {
        const result = {
          data: res.data,
        };
        setAnswer({
          transcript: [result.data.answer],
          title: [''],
        });
      },
      onError: (err: ServerErrorResponse) => {
        console.error(err);
        emitEvent(
          CATEGORY_SEARCH_BY_IMAGE,
          EVENT_ERROR_RESPONSE,
          'fetchAnswer'
        );
      },
    }
  );

  useEffect(() => {
    fetchAnswer();
    fetchRelevance();
  }, [searchQuestionId, fetchAnswer, fetchRelevance]);

  return (
    <>
      <Row className={styles.full_width}>
        {isLoadingRelevance && <SearchResultLoading size={1} min={1} max={1} />}
        {!isLoadingRelevance && <Paragraph>{relevance}</Paragraph>}
      </Row>

      <Row className={styles.full_width}>
        {isLoadingAnswer && <SearchResultLoading size={2} min={1} max={1} />}
        {!isLoadingAnswer && (
          <Paragraph>
            {answer !== undefined && (
              <TextHighlight highlight={answer}></TextHighlight>
            )}
          </Paragraph>
        )}
      </Row>
    </>
  );
}
