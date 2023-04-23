import styles from './search-huge.less';
import { Lecture } from '@/types/lecture';
import { Row, Input } from 'antd';
import { useMutation } from '@tanstack/react-query';
import { useState } from 'react';
import apiClient, { ServerErrorResponse, ServerResponse } from '@/http';
import { emitEvent } from '@/matomo';
import {
  CATEGORY_SEARCH_HUGE,
  EVENT_ERROR_RESPONSE,
  EVENT_SEARCHED,
} from '@/matomo/events';

const { Search } = Input;

interface LectureResponse extends ServerResponse {
  data: Lecture[];
}

interface SearchHugeProps {
  className: string;
  foundLectures: (lectures: Lecture[]) => void;
  onChange: (hasInput: boolean) => void;
}

export default function SearchHuge(props: SearchHugeProps) {
  const { className, foundLectures, onChange } = props;

  const [query, setQuery] = useState<string>('');
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
        foundLectures(result.data);
      },
      onError: (err: ServerErrorResponse) => {
        console.error(err);
        emitEvent(CATEGORY_SEARCH_HUGE, EVENT_ERROR_RESPONSE, 'doSearch');
      },
    }
  );

  const search = async (query: string) => {
    await setQuery(query);
    doSearch();
    emitEvent(CATEGORY_SEARCH_HUGE, EVENT_SEARCHED, query);
  };

  return (
    <div className={`${styles.fullwidth} ${className}`}>
      <Row>
        <Search
          className={styles.search_tool}
          placeholder="Search for anything said in any lecture"
          size="large"
          value={query}
          loading={isSearching}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
            const val = e.target.value;
            search(val);
            onChange(val !== '');
          }}
        />
      </Row>
    </div>
  );
}
