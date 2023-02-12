import Analyser from '@/components/analyser/analyser';
import Frame from '@/components/main/frame';
import { useParams } from 'umi';


export default function AnalysePage() {
  const { id, language } = useParams();

  return (
    <>
      <Frame step={1}>
        <Analyser id={id!} language={language!}></Analyser>
      </Frame>
    </>
  );
}
