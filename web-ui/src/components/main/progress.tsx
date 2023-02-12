import styles from './progress.less';
import {
  Steps,
  Layout,
} from 'antd';

const { Sider } = Layout;

export default function Progress(props: {step: number}) {
  const {step} = props;

  return (
    <>
      <Sider theme='light' className={styles.progress} width={300}>
        <Steps
          direction='vertical'
          className={styles.steps}
          current={step}
          items={[
            {
              title: 'Select Lecture',
              description: 'Provide a recorded lecture for kthGPT to watch'
            },
            {
              title: 'Analyse Lecture',
              description: 'kthGPT will watch and analyse the lecture'
            },
            {
              title: 'Ask Questions',
              description: 'use kthGPT to ask questions about the lecture'
            },
          ]}
        />
      </Sider>
    </>
  );
}
