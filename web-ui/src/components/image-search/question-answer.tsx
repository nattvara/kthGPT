import styles from './question-answer.less';
import { Row, Skeleton, Typography } from 'antd';
import { Highlight, Lecture } from '@/components/lecture';
import apiClient, { ServerErrorResponse, ServerResponse } from '@/http';
import { useMutation } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import { HighlightText } from '../selector/highlight-text';

const { Paragraph } = Typography;

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

interface QuestionAnswerProps {
  imageId: string;
  questionId: string;
  lecture: Lecture;
}

export function QuestionAnswer(props: QuestionAnswerProps) {
  const { imageId, questionId, lecture } = props;

  const [answer, setAnswer] = useState<Highlight>();
  const [relevance, setRelevance] = useState<string>('');

  const { isLoading: isLoadingRelevance, mutate: fetchRelevance } = useMutation(
    async () => {
      return await apiClient.get(
        `/search/image/${imageId}/questions/${questionId}/${lecture.public_id}/${lecture.language}/relevance`
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
        `/search/image/${imageId}/questions/${questionId}/${lecture.public_id}/${lecture.language}/answer`
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
  }, [questionId, fetchAnswer, fetchRelevance]);

  return (
    <>
      <Row className={styles.fullwidth}>
        {isLoadingRelevance && (
          <div className={styles.fullwidth}>
            <Skeleton active paragraph={{ rows: 1 }}></Skeleton>
          </div>
        )}
        {!isLoadingRelevance && <Paragraph>{relevance}</Paragraph>}
      </Row>

      <Row className={styles.fullwidth}>
        {isLoadingAnswer && (
          <div className={styles.fullwidth}>
            <Skeleton active></Skeleton>
          </div>
        )}
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
