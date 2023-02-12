import { Outlet } from 'umi';
import { Layout } from 'antd';
import React from 'react';
import './index.less';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
const queryClient = new QueryClient();

const { Content } = Layout;

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <Content style={{ padding: '0 50px' }}>
        <div>
          <Outlet />
        </div>
      </Content>
    </QueryClientProvider>
  );
};

export default App;
