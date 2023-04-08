import { Button, Col, Result, Row, Space, Typography } from 'antd';
import styles from './search-by-image.less';
import { Image, Question } from '@/types/search';
import { useEffect, useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import apiClient, { ServerErrorResponse, ServerResponse } from '@/http';
import { ReloadOutlined } from '@ant-design/icons';
import { SearchResultLoading } from '@/components/searching/search-result-loading/search-result-loading';
import { history } from 'umi';
import { LecturePreviewCompact } from '@/components/lecture/lecture-preview/lecture-preview';
import { Highlight, Lecture } from '@/types/lecture';
import { HighlightText } from '@/components/text/highlight-text/highlight-text';

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

interface SearchByImageProps {
  image: Image;
}

export default function SearchByImage(props: SearchByImageProps) {
  const { image } = props;

  const [error, setError] = useState<string>('');
  const [lectures, setLectures] = useState<Lecture[]>([]);
  const [searchQuestionId, setSearchQuestionId] = useState<string>('');
  const [notReady, setNotReady] = useState<boolean | null>(null);

  const { isLoading: isSearching, mutate: doSearch } = useMutation(
    async () => {
      return await apiClient.post(`/search/image/${image.id}/questions`, {
        query: QUESTION,
      });
    },
    {
      onSuccess: (res: QuestionResponse) => {
        const result = {
          data: res.data,
        };
        setNotReady(false);
        setLectures(result.data.hits);
        setSearchQuestionId(result.data.id);
      },
      onError: (err: ServerErrorResponse) => {
        if (err.response.status === 409) {
          setNotReady(true);
          return;
        }

        if (err.response && err.response.data.detail) {
          setError(err.response.data.detail);
        }

        console.error(err);
      },
    }
  );

  const search = async () => {
    if (isSearching) return;
    doSearch();
  };

  const goToLecture = async (lecture: Lecture, newTab = false) => {
    const url = `/questions/lectures/${lecture.public_id}/${lecture.language}`;

    if (newTab) {
      window.open(url, '_blank');
    } else {
      await history.push(url);
    }
  };

  useEffect(() => {
    search();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

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
        {(isSearching || notReady) && (
          <SearchResultLoading size={6} min={3} max={6} />
        )}
      </Row>

      {!isSearching && (
        <Row>
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
                        <LecturePreviewCompact
                          lecture={lecture}
                          onClick={() => goToLecture(lecture)}
                          onMetaClick={() => goToLecture(lecture, true)}
                          onCtrlClick={() => goToLecture(lecture, true)}
                        />
                      </Row>
                      <Row>
                        <QuestionAnswer
                          lecture={lecture}
                          imageId={image.id}
                          searchQuestionId={searchQuestionId}
                        />
                      </Row>
                    </Col>
                  </Row>
                );
              })}
            </Space>
          </Row>
        </Row>
      )}
    </>
  );
}

interface QuestionAnswerProps {
  imageId: string;
  searchQuestionId: string;
  lecture: Lecture;
}

export function QuestionAnswer(props: QuestionAnswerProps) {
  const { imageId, searchQuestionId, lecture } = props;

  const [answer, setAnswer] = useState<Highlight>();
  const [relevance, setRelevance] = useState<string>('');

  const { isLoading: isLoadingRelevance, mutate: fetchRelevance } = useMutation(
    async () => {
      return await apiClient.get(
        `/search/image/${imageId}/questions/${searchQuestionId}/${lecture.public_id}/${lecture.language}/relevance`
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
        console.log(err);
      },
    }
  );

  const { isLoading: isLoadingAnswer, mutate: fetchAnswer } = useMutation(
    async () => {
      return await apiClient.get(
        `/search/image/${imageId}/questions/${searchQuestionId}/${lecture.public_id}/${lecture.language}/answer`
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
        console.log(err);
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
              <HighlightText highlight={answer}></HighlightText>
            )}
          </Paragraph>
        )}
      </Row>
    </>
  );
}
