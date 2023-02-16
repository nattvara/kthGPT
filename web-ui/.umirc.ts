import { defineConfig } from 'umi';

export default defineConfig({
  routes: [
    { path: '/', component: 'index' },
    { path: '/404', component: '404' },
    { path: '/analyse/lectures/:id/:language', component: 'analyse' },
    { path: '/questions/lectures/:id/:language', component: 'questions' },
  ],
  npmClient: 'pnpm',
});
