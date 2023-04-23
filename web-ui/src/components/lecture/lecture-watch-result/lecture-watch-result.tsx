import { emitEvent } from '@/matomo';
import {
  ACTION_NONE,
  CATEGORY_PAGE_FRAME,
  EVENT_GOTO_GITHUB_ISSUES,
} from '@/matomo/events';
import { Lecture } from '@/types/lecture';
import { BulbOutlined, GithubFilled, LoadingOutlined } from '@ant-design/icons';
import { Button, Col, Result, Row, Typography } from 'antd';
import { history } from 'umi';

const { Paragraph } = Typography;

interface LectureWatchResultProps {
  lecture: Lecture;
  restart: () => void;
  isRestarting: boolean;
}

const openGithubIssues = () => {
  window.open('https://github.com/nattvara/kthGPT/issues', '_blank');
  emitEvent(CATEGORY_PAGE_FRAME, EVENT_GOTO_GITHUB_ISSUES, ACTION_NONE);
};

export default function LectureWatchResult(props: LectureWatchResultProps) {
  const { lecture, restart, isRestarting } = props;

  const goToQuestions = async () => {
    await history.push(
      `/lectures/${lecture.public_id}/${lecture.language}/questions`
    );
  };

  if (lecture.approved === null && lecture.analysis?.state === 'failure') {
    return (
      <>
        <Result
          status="500"
          title="Something went wrong when classifying the video!"
          subTitle="Unfortunately something must have gone wrong, click the button to try analyzing the video again. Sometimes restarting just fixes things ¯\_(ツ)_/¯"
          extra={[
            <Button
              onClick={() => restart()}
              loading={isRestarting}
              type="primary"
              key="btn"
              icon={<BulbOutlined />}
              size="large"
            >
              Restart
            </Button>,
          ]}
        />
      </>
    );
  }

  if (lecture.approved === null) {
    return (
      <>
        <Result
          icon={<LoadingOutlined />}
          title="Waiting for the video to be approved"
          subTitle={
            <>
              <Row justify="center">
                <Col xs={24} sm={12}>
                  <Paragraph>
                    Since kthGPT has limited capacity only relevant videos are
                    allowed. kthGPT is currently trying to figure out if the
                    video is relevant. Relevant videos are educational videos,
                    such as recorded lectures, tutorials about math, programming
                    etc.
                  </Paragraph>
                  <Paragraph>
                    kthGPT will also not watch videos longer than 4 hours.
                  </Paragraph>
                  <Paragraph>
                    <strong>This can take a few minutes.</strong>
                  </Paragraph>
                </Col>
              </Row>
            </>
          }
        />
      </>
    );
  }

  if (lecture.approved === false) {
    return (
      <>
        <Result
          status="error"
          title="The video was denied by kthGPT"
          subTitle={
            <>
              <Row justify="center">
                <Col xs={24} sm={12} style={{ textAlign: 'left' }}>
                  <Paragraph>
                    <strong>
                      Since kthGPT has limited capacity only relevant videos are
                      allowed.
                    </strong>
                    <span> </span>
                    kthGPT is using AI to determine which videos are relevant.
                    And this video was denied. There is a few reasons why this
                    could have happened. However, most likely this is because
                    the video was off-topic.
                  </Paragraph>
                  <Paragraph>
                    Youtube videos should be about a topic that is relevant for
                    a course at KTH, which is the purpose of kthGPT.
                  </Paragraph>
                  <Paragraph>
                    <strong>If you feel this video should be admitted</strong>
                    <span> </span>
                    please feel free to open an issue on github.
                  </Paragraph>
                </Col>
              </Row>
            </>
          }
          extra={[
            <Button
              onClick={() => openGithubIssues()}
              type="primary"
              key="btn"
              icon={<GithubFilled />}
              size="large"
            >
              Open an issue
            </Button>,
          ]}
        />
      </>
    );
  }

  if (lecture.analysis?.state === 'ready') {
    return (
      <Result
        status="success"
        title="Lecture has been successfully analyzed!"
        subTitle="The lecture is ready to be queried with GPT-3"
        extra={[
          <Button
            onClick={() => goToQuestions()}
            type="primary"
            key="btn"
            size="large"
          >
            Start asking questions
          </Button>,
        ]}
      />
    );
  }

  if (lecture.analysis?.state === 'failure') {
    return (
      <Result
        status="500"
        title="Something went wrong when analyzing the lecture!"
        subTitle="Unfortunately something must have gone wrong, click the button to try analyzing the video again. Sometimes restarting just fixes things ¯\_(ツ)_/¯"
        extra={[
          <Button
            onClick={() => restart()}
            loading={isRestarting}
            type="primary"
            key="btn"
            icon={<BulbOutlined />}
            size="large"
          >
            Restart
          </Button>,
        ]}
      />
    );
  }

  if (lecture.analysis?.frozen) {
    return (
      <Result
        status="403"
        title="The analysis seems to be stuck!"
        subTitle="Click the button to restart the analysis. Sometimes restarting just fixes things ¯\_(ツ)_/¯"
        extra={[
          <Button
            onClick={() => restart()}
            loading={isRestarting}
            type="primary"
            key="btn"
            icon={<BulbOutlined />}
            size="large"
          >
            Restart
          </Button>,
        ]}
      />
    );
  }

  return <></>;
}
