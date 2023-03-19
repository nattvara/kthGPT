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
      <Frame>
        <Selector></Selector>
      </Frame>
    </>
  );
}
