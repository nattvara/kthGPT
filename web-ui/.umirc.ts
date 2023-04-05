import { defineConfig } from 'umi';

export default defineConfig({
  routes: [
    { path: '/', component: 'index' },

    { path: '/courses', component: 'courses' },
    { path: '/courses/:courseCode', component: 'courses' },

    { path: '/lectures/add', component: 'lectures/add' },
    { path: '/lectures/:id/:language/questions', component: 'lectures/questions' },
    { path: '/lectures/:id/:language/analyse', component: 'lectures/analyse' },

    { path: '/info/queue', component: 'info/queue' },
    { path: '/info/denied', component: 'info/denied' },
    { path: '/info/failures', component: 'info/failures' },

    { path: '/about', component: 'about' },

    { path: '*', component: '404' },
  ],
  npmClient: 'pnpm',
});
