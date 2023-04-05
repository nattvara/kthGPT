import { defineConfig } from 'umi';

export default defineConfig({
  routes: [
    { path: '/', component: 'index' },
    { path: '/add', component: 'add' },

    { path: '/courses', component: 'courses' },
    { path: '/courses/:courseCode', component: 'courses' },

    { path: '/lectures/:id/:language/questions', component: 'questions' },

    { path: '/analyse/lectures/:id/:language', component: 'analyse' },
    { path: '/questions/lectures/:id/:language', component: 'questions' },
    { path: '/queue', component: 'queue' },
    { path: '/denied', component: 'denied' },
    { path: '/failures', component: 'failures' },
    { path: '/about', component: 'about' },

    { path: '*', component: '404' },
  ],
  npmClient: 'pnpm',
});
