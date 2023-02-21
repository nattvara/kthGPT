import { defineConfig } from 'umi';

export default defineConfig({
  routes: [
    { path: '/', component: 'index' },
    { path: '/analyse/lectures/:id/:language', component: 'analyse' },
    { path: '/questions/lectures/:id/:language', component: 'questions' },
    { path: '/queue', component: 'queue' },

    { path: '*', component: '404' },
  ],
  npmClient: 'pnpm',
});
