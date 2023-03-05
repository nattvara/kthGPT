import Frame from '@/components/main/frame';
import { registerPageLoad } from '@/matomo';
import { LeftOutlined } from '@ant-design/icons';
import { Row, Col, Typography, Button } from 'antd';
import { useEffect } from 'react';
import styles from './about.less';

const { Paragraph, Title, Link } = Typography;

export default function AboutPage() {
  useEffect(() => {
    registerPageLoad();
  }, []);

  return (
    <>
      <Frame>
        <div className={styles.page}>
          <Row justify="center">
            <Col sm={24} md={15}>
              <Link href="/">
                <Button type="primary">
                  <LeftOutlined /> Back
                </Button>
              </Link>
            </Col>
          </Row>
          <Row justify="center">
            <Col sm={24} md={15}>
              <Title>About kthGPT</Title>
              <Paragraph>
                kthGPT is a free and open source tool that can watch a lecture
                for you. It allows students to ask questions about any lecture
                using the GPT-3 model.
              </Paragraph>
              <Paragraph>
                <blockquote>
                  This project <strong>is not</strong> affiliated with KTH. It's
                  just a tool that's meant to be useful for KTH students.
                </blockquote>
              </Paragraph>

              <Title>How to use it</Title>
              <Title level={3}>1. Select lecture</Title>
              <Paragraph>
                Select a lecture that's already been watched or add a new one!
                kthGPT can watch lectures hosted on
                <span> </span>
                <Link href="https://play.kth.se/" target="_blank">
                  KTH Play
                </Link>
                <span> </span>
                or
                <span> </span>
                <Link href="https://youtube.com" target="_blank">
                  YouTube
                </Link>
                .
              </Paragraph>
              <Paragraph>
                It can't watch any video on YouTube. Due to limited capacity
                kthGPT will only watch "relevant videos". Relevant videos are
                such that it thinks are <code>Recorded Lectures</code>. kthGPT
                uses a sample of the video to do this assessment.
              </Paragraph>

              <Title level={3}>2. Wait for kthGPT to "watch" the lecture</Title>
              <Paragraph>
                If the video has not been watched by kthGPT before, it will
                start watching the video and try to produce a summary. It will
                only listen to the audio, so nothing been shown or written in
                the lecture will be included in the summary.
              </Paragraph>
              <Paragraph>
                This process is very resource intensive and usually takes
                between 20-60 minutes. This will be slower if many videos have
                been queued.
              </Paragraph>
              <Paragraph>
                If the audio quality in the video is bad, the quality of the
                summary will be worse. kthGPT is generally best at understanding
                English. However, if the audio quality is good, Swedish should
                be just fine as well.
              </Paragraph>

              <Title level={3}>3. Ask questions about the lecture</Title>
              <Paragraph>
                The lecture is ready. kthGPT can now use GPT-3 to answer
                questions about the lecture. Some useful queries:
              </Paragraph>

              <Title level={5}>
                <blockquote>
                  Summarize the lecture for me into 10 bullets
                </blockquote>
              </Title>
              <Paragraph>
                This query obviously useful to get a brief overview about what's
                covered in the lecture
              </Paragraph>

              <Title level={5}>
                <blockquote>
                  Tell me the core concepts covered in the lecture and give some
                  explanations for each
                </blockquote>
              </Title>
              <Paragraph>
                This usually produce very good results. Answers seem to be less
                inclined to summarise the audio transcript and focus more on the
                topics. Which seem to produce more accurate results.
              </Paragraph>

              <Title level={5}>
                <blockquote>
                  At which point in the lecture is X covered?
                </blockquote>
              </Title>
              <Paragraph>
                Pretty self explanatory, useful to quickly now where to look in
                a lecture.
              </Paragraph>

              <Title level={5}>
                <blockquote></blockquote>
              </Title>
              <Paragraph></Paragraph>

              <Title level={5}>
                <blockquote>
                  Where in the course book "X" can i read more about the topics
                  from this lecture?
                </blockquote>
              </Title>
              <Paragraph>
                Very useful to find more reading instructions.
              </Paragraph>
              <Paragraph>
                In
                <span> </span>
                <Link href="/questions/lectures/0_xkulq3st/en" target="_blank">
                  this lecture
                </Link>
                <span> </span>
                the following question:
              </Paragraph>
              <Paragraph>
                <span>- </span>
                <em>
                  Where in the course book "Hans Peters, Game Theory: A
                  Multi-Leveled Approach, Springer 2008" can i read more about
                  the topics from this lecture?
                </em>
              </Paragraph>
              <Paragraph>Produce the following results:</Paragraph>
              <Paragraph>
                <em>
                  - Hans Peters, Game Theory: A Multi-Leveled Approach, Springer
                  2008 (Chapter 6) provides a deep exploration of the topics
                  discussed in this lecture. It includes discussion on
                  transferable utility and the core, super-aditivity, and
                  finding efficient outcomes in non-zero sum games, as well as
                  balancing games and linear programming.
                </em>
              </Paragraph>
            </Col>
          </Row>
        </div>
      </Frame>
    </>
  );
}
