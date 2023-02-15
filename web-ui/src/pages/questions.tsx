import Questions from '@/components/questions/questions';
import Frame from '@/components/main/frame';
import { useParams } from 'umi';


export default function QuestionsPage() {
  const { id, language } = useParams();

  return (
    <>
      <Frame step={2}>
        <Questions id={id!} language={language!}></Questions>
      </Frame>
    </>
  );
}
