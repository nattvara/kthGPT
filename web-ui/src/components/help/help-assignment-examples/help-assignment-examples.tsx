import { useEffect, useState } from 'react';
import styles from './help-assignment-examples.less';
import { Row, Image } from 'antd';
import example1 from '@/assets/examples/example_1.png';
import example2 from '@/assets/examples/example_2.png';
import example3 from '@/assets/examples/example_3.png';
import example4 from '@/assets/examples/example_4.png';
import example5 from '@/assets/examples/example_5.png';
import example6 from '@/assets/examples/example_6.png';
import example7 from '@/assets/examples/example_7.png';
import example8 from '@/assets/examples/example_8.png';
import example9 from '@/assets/examples/example_9.png';
import example10 from '@/assets/examples/example_10.png';
import example11 from '@/assets/examples/example_11.png';
import example12 from '@/assets/examples/example_12.png';
import example13 from '@/assets/examples/example_13.png';
import example14 from '@/assets/examples/example_14.png';
import example15 from '@/assets/examples/example_15.png';
import example16 from '@/assets/examples/example_16.png';
import example17 from '@/assets/examples/example_17.png';
import example18 from '@/assets/examples/example_18.png';
import example19 from '@/assets/examples/example_19.png';
import example20 from '@/assets/examples/example_20.png';
import example21 from '@/assets/examples/example_21.png';
import example22 from '@/assets/examples/example_22.png';
import example23 from '@/assets/examples/example_23.png';
import example24 from '@/assets/examples/example_24.png';
import example25 from '@/assets/examples/example_25.png';
import example26 from '@/assets/examples/example_26.png';
import example27 from '@/assets/examples/example_27.jpg';
import example28 from '@/assets/examples/example_28.jpg';
import example29 from '@/assets/examples/example_29.jpg';
import example30 from '@/assets/examples/example_30.jpg';
import example31 from '@/assets/examples/example_31.jpg';
import example32 from '@/assets/examples/example_32.png';
import example33 from '@/assets/examples/example_33.png';
import example34 from '@/assets/examples/example_34.png';
import example35 from '@/assets/examples/example_35.png';
import example36 from '@/assets/examples/example_36.jpg';
import example37 from '@/assets/examples/example_37.jpg';
import example38 from '@/assets/examples/example_38.jpg';
import example39 from '@/assets/examples/example_39.jpg';
import arrow from '@/assets/arrow.svg';

type ExampleKeys =
  | 'example_1'
  | 'example_2'
  | 'example_3'
  | 'example_4'
  | 'example_5'
  | 'example_6'
  | 'example_7'
  | 'example_8'
  | 'example_9'
  | 'example_10'
  | 'example_11'
  | 'example_12'
  | 'example_13'
  | 'example_14'
  | 'example_15'
  | 'example_16'
  | 'example_17'
  | 'example_18'
  | 'example_19'
  | 'example_20'
  | 'example_21'
  | 'example_22'
  | 'example_23'
  | 'example_24'
  | 'example_25'
  | 'example_26'
  | 'example_27'
  | 'example_28'
  | 'example_29'
  | 'example_30'
  | 'example_31'
  | 'example_32'
  | 'example_33'
  | 'example_34'
  | 'example_35'
  | 'example_36'
  | 'example_37'
  | 'example_38'
  | 'example_39';

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
  example_8: example8,
  example_9: example9,
  example_10: example10,
  example_11: example11,
  example_12: example12,
  example_13: example13,
  example_14: example14,
  example_15: example15,
  example_16: example16,
  example_17: example17,
  example_18: example18,
  example_19: example19,
  example_20: example20,
  example_21: example21,
  example_22: example22,
  example_23: example23,
  example_24: example24,
  example_25: example25,
  example_26: example26,
  example_27: example27,
  example_28: example28,
  example_29: example29,
  example_30: example30,
  example_31: example31,
  example_32: example32,
  example_33: example33,
  example_34: example34,
  example_35: example35,
  example_36: example36,
  example_37: example37,
  example_38: example38,
  example_39: example39,
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
  const [loaded, setLoaded] = useState<boolean>(false);
  const [src, setSrc] = useState<string>('');

  useEffect(() => {
    setRotation(randomInt(-30, 30));
    setSrc(EXAMPLES[example]);
  }, [example]);

  return (
    <Image
      className={`${styles.image} ${styles.fade_in} ${
        loaded ? styles.loaded : ''
      }`}
      style={{ transform: `rotate(${rotation}deg)` }}
      src={src}
      preview={false}
      onLoad={() => setLoaded(true)}
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
      <Image src={arrow} className={styles.arrow} preview={false} />
      {examples.map((example) => (
        <ImageExample key={example} example={example as ExampleKeys} />
      ))}
    </Row>
  );
}
