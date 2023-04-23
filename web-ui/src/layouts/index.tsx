import { Outlet } from 'umi';
import { ConfigProvider, Layout } from 'antd';
import React from 'react';
import styles from './index.less';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
const queryClient = new QueryClient();

const { Content } = Layout;

const App: React.FC = () => {
  return (
    <ConfigProvider
      theme={{
        token: {
          fontFamily:
            'Lato, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, Noto Sans, sans-serif, Apple Color Emoji, Segoe UI Emoji, Segoe UI Symbol, Noto Color Emoji',
          colorPrimary: '#1751a6',
        },
      }}
    >
      <QueryClientProvider client={queryClient}>
        <Content className={styles.content}>
          <div>
            <Outlet />
          </div>
        </Content>
      </QueryClientProvider>
    </ConfigProvider>
  );
};

export default App;
