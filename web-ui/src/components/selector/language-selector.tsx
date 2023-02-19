import {
  AudioOutlined,
} from '@ant-design/icons';
import styles from './language-selector.less';
import {
  Row,
  Col,
  Button,
  Radio,
  Image,
  RadioChangeEvent,
} from 'antd';
import enFlag from '@/assets/flag-en.svg';
import svFlag from '@/assets/flag-sv.svg';


interface LanguageSelectorProps {
  onChange: (e: RadioChangeEvent) => void
  language: string
}


export default function LanguageSelector(props: LanguageSelectorProps) {
  const { onChange, language } = props;

  return (
    <Radio.Group onChange={onChange} value={language} defaultValue='en' buttonStyle='solid' size='large'>
      <Button type='text' size='large' style={{pointerEvents: 'none'}}>
        <AudioOutlined /> Select lecture language:
      </Button>
      <Radio value='en'>
        <Row justify='center' align='middle'>
          <Col><Image
            src={enFlag}
            height={30}
            width={60}
            preview={false}
            className={`${language !== 'en' ? styles.grayscale : ''} ${styles.flag}`}
          /></Col>
        </Row>
      </Radio>
      <Radio value='sv'>
        <Row justify='center' align='middle'>
          <Col><Image
            src={svFlag}
            height={30}
            width={50}
            preview={false}
            className={`${language !== 'sv' ? styles.grayscale : ''} ${styles.flag}`}
          /></Col>
        </Row>
      </Radio>
    </Radio.Group>
  );
}
