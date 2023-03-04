import Analyser from '@/components/analyser/analyser';
import Frame from '@/components/main/frame';
import { registerPageLoad } from '@/matomo';
import { useEffect } from 'react';
import { useParams } from 'umi';

export default function AnalysePage() {
  const { id, language } = useParams();

  useEffect(() => {
    registerPageLoad();
  }, []);

  return (
    <>
      <Frame step={1}>
        <Analyser id={id!} language={language!}></Analyser>
      </Frame>
    </>
  );
}
