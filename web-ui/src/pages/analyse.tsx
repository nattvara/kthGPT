import Analyser from '@/components/analyser/analyser';
import Frame from '@/components/page/frame/frame';
import { registerPageLoad } from '@/matomo';
import { useEffect } from 'react';
import { useParams } from 'umi';

export default function AnalysePage() {
  const { id, language } = useParams();

  useEffect(() => {
    registerPageLoad();
  }, []);

  if (id === null) {
    return <></>;
  }

  if (language === null) {
    return <></>;
  }

  return (
    <>
      <Frame>
        <Analyser id={id} language={language}></Analyser>
      </Frame>
    </>
  );
}
