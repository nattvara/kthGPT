import { PlayCircleOutlined } from '@ant-design/icons';
import { DownloadOutlined } from '@ant-design/icons';
import styles from './selector.less';
import {
  Input,
  Row,
  Col,
  Space,
  Button,
  Radio,
} from 'antd';

export default function Selector() {
  return (
    <div>
      <Space direction="vertical" size="large" style={{width: '100%'}}>
        <Row>
          <Col span={24}>
            <Input
              className={styles.hugeInput}
              placeholder="Enter video.. eg. https://play.kth.se/media/..."
              prefix={<PlayCircleOutlined />} />
          </Col>
        </Row>
        <Row gutter={[10, 10]}>
          <Col>
            <Button type="primary" icon={<DownloadOutlined />} size="large">
              Analyze
            </Button>
          </Col>
          <Col>
            <Radio.Group defaultValue="a" buttonStyle="solid" size="large">
              <Radio.Button value="a">English lecture</Radio.Button>
              <Radio.Button value="b">Swedish lecture</Radio.Button>
            </Radio.Group>
          </Col>
        </Row>
      </Space>
    </div>
  );
}
