import { Outlet } from 'umi';
import { Layout } from 'antd';
import React from 'react';
import styles from './index.less';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
const queryClient = new QueryClient();

const { Content } = Layout;

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <Content className={styles.content}>
        <div>
          <Outlet />
        </div>
      </Content>
    </QueryClientProvider>
  );
};

export default App;
