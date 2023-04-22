import { useEffect, useState } from 'react';
import styles from './help-assignment-examples.less';
import { Row, Image } from 'antd';
import example1 from '@/assets/example_1.png';
import example2 from '@/assets/example_2.png';
import example3 from '@/assets/example_3.png';
import example4 from '@/assets/example_4.png';
import example5 from '@/assets/example_5.png';
import example6 from '@/assets/example_6.png';
import example7 from '@/assets/example_7.png';
import arrow from '@/assets/arrow.svg';

type ExampleKeys =
  | 'example_1'
  | 'example_2'
  | 'example_3'
  | 'example_4'
  | 'example_5'
  | 'example_6'
  | 'example_7';

type Examples = {
  [key in ExampleKeys]: string;
};

const EXAMPLES: Examples = {
  example_1: example1,
  example_2: example2,
  example_3: example3,
  example_4: example4,
  example_5: example5,
  example_6: example6,
  example_7: example7,
};

const randomInt = (min: number, max: number) => {
  return Math.floor(Math.random() * (max - min + 1)) + min;
};

interface ImageExampleProps {
  example: ExampleKeys;
}

function ImageExample(props: ImageExampleProps) {
  const { example } = props;

  const [rotation, setRotation] = useState<number>(0);
  const [src, setSrc] = useState<string>('');

  useEffect(() => {
    setRotation(randomInt(-30, 30));
    setSrc(EXAMPLES[example]);
  }, [example]);

  return (
    <Image
      className={styles.image}
      style={{ transform: `rotate(${rotation}deg)` }}
      src={src}
      preview={false}
    />
  );
}

export default function HelpAssignmentExamples() {
  const getRandomExample = (): string => {
    return Object.keys(EXAMPLES)[
      randomInt(0, Object.keys(EXAMPLES).length - 1)
    ];
  };

  const [examples] = useState<string[]>(() => {
    const newExamples: string[] = [];
    for (let i = 0; i < 5; i++) {
      const example = getRandomExample();
      if (newExamples.includes(example)) {
        i--;
        continue;
      }
      newExamples.push(example);
    }
    return newExamples;
  });

  return (
    <Row className={styles.container}>
      {examples.map((example) => (
        <ImageExample key={example} example={example as ExampleKeys} />
      ))}
      <Image src={arrow} className={styles.arrow} preview={false} />
    </Row>
  );
}
