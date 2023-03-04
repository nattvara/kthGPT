import Questions from '@/components/questions/questions';
import Frame from '@/components/main/frame';
import { useParams } from 'umi';
import { useEffect } from 'react';
import { registerPageLoad } from '@/matomo';

export default function QuestionsPage() {
  useEffect(() => {
    registerPageLoad();
  }, []);

  const { id, language } = useParams();

  return (
    <>
      <Frame step={2}>
        <Questions id={id!} language={language!}></Questions>
      </Frame>
    </>
  );
}
