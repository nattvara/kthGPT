import { Outlet } from 'umi';
import { Layout } from 'antd';
import React from 'react';
import './index.less';

const { Content } = Layout;

const App: React.FC = () => {
  return (
    <Content style={{ padding: '0 50px' }}>
      <div>
        <Outlet />
      </div>
    </Content>
  );
};

export default App;
