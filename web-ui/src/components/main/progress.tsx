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
      <Sider theme='light' className={styles.progress}>
        <Steps
          direction="vertical"
          className={styles.steps}
          current={step}
          items={[
          {
            title: 'Select Lecture',
          },
          {
            title: 'Analyse Lecture',
          },
          {
            title: 'Ask Questions',
          },
          ]}
        />
      </Sider>
    </>
  );
}
