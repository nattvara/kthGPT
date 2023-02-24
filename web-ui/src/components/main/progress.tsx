import styles from './progress.less';
import {
  Steps,
  Layout,
} from 'antd';
import { history } from 'umi';

const { Sider } = Layout;

export default function Progress(props: {step: number}) {
  const { step } = props;

  const onChange = (value: number) => {
    if (value === 0) {
      history.push('/');
    }
  };

  return (
    <>
      <Sider theme='light' className={styles.progress} width={300}>
        <Steps
          direction='vertical'
          className={styles.steps}
          current={step}
          onChange={onChange}
          items={[
            {
              title: 'Select Lecture',
              description: 'Select a lecture for kthGPT to watch'
            },
            {
              title: 'Watch Lecture',
              description: 'kthGPT will watch and analyze the lecture'
            },
            {
              title: 'Ask Questions',
              description: 'Use kthGPT to ask questions about the lecture'
            },
          ]}
        />
      </Sider>
    </>
  );
}
