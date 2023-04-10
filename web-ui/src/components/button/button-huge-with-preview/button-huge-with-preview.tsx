import styles from './button-huge-with-preview.less';
import { Row, Typography } from 'antd';
import { useState } from 'react';
import { history } from 'umi';

const { Title } = Typography;

interface ButtonHugeWithPreviewProps {
  icon: JSX.Element;
  title: string;
  subtitle: string;
  url: string;
  preview: JSX.Element;
}

export default function ButtonHugeWithPreview(
  props: ButtonHugeWithPreviewProps
) {
  const [hovering, setHovering] = useState<boolean>(false);

  const goToUrl = async (url: string, newTab = false) => {
    if (newTab) {
      window.open(url, '_blank');
    } else {
      await history.push(url);
    }
  };

  return (
    <div
      className={styles.container}
      onMouseEnter={() => setHovering(true)}
      onMouseLeave={() => setHovering(false)}
      onClick={(e: React.MouseEvent) => {
        if (e.metaKey) return goToUrl(props.url, true);
        if (e.ctrlKey) return goToUrl(props.url, true);
        goToUrl(props.url);
      }}
    >
      <Row className={`${styles.icon} ${hovering ? styles.hovering : ''}`}>
        {props.icon}
      </Row>
      <Row className={`${styles.title} ${hovering ? styles.hovering : ''}`}>
        <Title level={3}>{props.title}</Title>
      </Row>
      <Row className={`${styles.subtitle} ${hovering ? styles.hovering : ''}`}>
        <Title level={5}>{props.subtitle}</Title>
      </Row>
      <div className={styles.background}>{props.preview}</div>
    </div>
  );
}
