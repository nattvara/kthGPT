import { defineConfig } from 'umi';

export default defineConfig({
  routes: [
    { path: '/', component: 'index' },
    { path: '/analyse/lectures/:id/:language', component: 'analyse' },
  ],
  npmClient: 'pnpm',
});
