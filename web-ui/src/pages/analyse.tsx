import Frame from '@/components/main/frame';
import Selector from '@/components/selector/selector';
import { useParams } from 'umi';


export default function IndexPage() {

  const { id, language } = useParams();

  return (
    <>
      <Frame step={1}>
        <>
          <p>{ id }</p>
          <p>{ language }</p>
        </>
      </Frame>
    </>
  );
}
