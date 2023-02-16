import Frame from '@/components/main/frame';
import Selector from '@/components/selector/selector';
import { registerPageLoad } from '@/matomo';
import { useEffect } from 'react';


export default function IndexPage() {
  useEffect(() => {
    registerPageLoad();
  }, []);

  return (
    <>
      <Frame step={0}>
        <Selector></Selector>
      </Frame>
    </>
  );
}
