import { defineConfig } from 'umi';

export default defineConfig({
  routes: [
    { path: '/', component: 'index' },

    { path: '/courses', component: 'courses/index' },
    { path: '/courses/:courseCode', component: 'courses/index' },

    { path: '/lectures/add', component: 'lectures/add' },
    { path: '/lectures/:id/:language/questions', component: 'lectures/questions' },
    { path: '/lectures/:id/:language/watch', component: 'lectures/watch' },

    { path: '/assignments/:id', component: 'assignments/index' },

    { path: '/info/queue', component: 'info/queue' },
    { path: '/info/denied', component: 'info/denied' },
    { path: '/info/failures', component: 'info/failures' },

    { path: '/about', component: 'about' },

    { path: '*', component: '404' },
  ],
  npmClient: 'pnpm',
});
