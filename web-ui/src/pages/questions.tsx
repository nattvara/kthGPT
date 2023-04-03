import Questions from '@/components/questions/questions';
import Frame from '@/components/page/frame/frame';
import { useParams } from 'umi';
import { useEffect } from 'react';
import { registerPageLoad } from '@/matomo';

export default function QuestionsPage() {
  useEffect(() => {
    registerPageLoad();
  }, []);

  const { id, language } = useParams();

  if (id === null) {
    return <></>;
  }

  if (language === null) {
    return <></>;
  }

  return (
    <>
      <Frame>
        <Questions id={id} language={language}></Questions>
      </Frame>
    </>
  );
}
