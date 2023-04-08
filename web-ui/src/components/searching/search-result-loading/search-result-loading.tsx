import styles from './search-result-loading.less';
import { Col, Row, Skeleton } from 'antd';
import { useEffect, useState } from 'react';

const randomInt = (min: number, max: number) => {
  return Math.floor(Math.random() * (max - min + 1)) + min;
};

interface SearchResultLoadingProps {
  size: number;
  min: number;
  max: number;
}

export function SearchResultLoading(props: SearchResultLoadingProps) {
  const { size, min, max } = props;

  const [paragraphs, setParagraphs] = useState<number[]>([]);

  useEffect(() => {
    const p = [];
    for (let i = 0; i < size; i++) {
      p.push(randomInt(min, max));
    }

    setParagraphs(p);
  }, [size, min, max]);

  return (
    <>
      <Row className={styles.full_width}>
        <Col span={24}>
          {paragraphs.map((p, index) => (
            <Skeleton key={index} active paragraph={{ rows: p }} />
          ))}
        </Col>
      </Row>
    </>
  );
}
