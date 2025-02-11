import {
  createRouter,
  createWebHashHistory,
  createWebHistory,
} from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useSpinner } from '@/composables/spinner';
import { useAlert } from '@/composables/alert';

export const getRoutes = [
  {
    path: '/',
    redirect: '/login',
    meta: { auth: false, navi: false },
  },
  {
    path: '/login',
    component: () => import('@/views/login/LoginView.vue'),
    name: 'login',
    meta: { auth: false, navi: false },
  },
  {
    path: '/main',
    component: () => import('@/views/SubRouterView.vue'),
    redirect: '/main',
    name: 'main',
    meta: {
      auth: true,
      navi: true,
      title: 'MAIN',
      permission: ['USER-00', 'USER-01'],
    },
    children: [
      {
        path: '/main',
        component: () => import('@/views/main/MainView.vue'),
        name: 'Main',
        meta: {
          auth: true,
          navi: true,
          title: 'MAIN',
          permission: ['USER-00', 'USER-01'],
        },
      },
    ],
  },
  {
    path: '/report',
    component: () => import('@/views/SubRouterView.vue'),
    redirect: '/report',
    name: 'report',
    meta: {
      auth: true,
      navi: true,
      title: 'REPORT',
      permission: ['USER-00', 'USER-01'],
    },
    children: [
      {
        path: '/report',
        component: () => import('@/views/report/ReportView.vue'),
        name: 'Report',
        meta: {
          auth: true,
          navi: true,
          title: 'REPORT',
          permission: ['USER-00', 'USER-01'],
        },
      },
    ],
  },
  {
    path: '/trend',
    component: () => import('@/views/SubRouterView.vue'),
    redirect: '/trend',
    name: 'trend',
    meta: {
      auth: true,
      navi: true,
      title: 'TREND',
      permission: ['USER-00', 'USER-01'],
    },
    children: [
      {
        path: '/trend',
        component: () => import('@/views/trend/TrendView.vue'),
        name: 'Trend',
        meta: {
          auth: true,
          navi: true,
          title: 'TREND',
          permission: ['USER-00', 'USER-01'],
        },
      },
    ],
  },
  {
    path: '/alarm',
    component: () => import('@/views/SubRouterView.vue'),
    redirect: '/alarm',
    name: 'alarm',
    meta: {
      auth: true,
      navi: true,
      title: 'Alarm Summary',
      permission: ['USER-00', 'USER-01'],
    },
    children: [
      {
        path: '/alarm',
        component: () => import('@/views/alarm/AlarmSummaryView.vue'),
        name: 'Alarm',
        meta: {
          auth: true,
          navi: true,
          title: 'Alarm Summary',
          permission: ['USER-00', 'USER-01'],
        },
      },
    ],
  },
  {
    path: '/command',
    component: () => import('@/views/SubRouterView.vue'),
    redirect: '/command',
    name: 'command',
    meta: {
      auth: true,
      navi: true,
      title: 'COMMAND',
      permission: ['USER-00', 'USER-01'],
    },
    children: [
      {
        path: '/command',
        component: () => import('@/views/command/CommandView.vue'),
        name: 'Command',
        meta: {
          auth: true,
          navi: true,
          title: 'COMMAND',
          permission: ['USER-00', 'USER-01'],
        },
      },
    ],
  },
  {
    path: '/setup',
    component: () => import('@/views/SubRouterView.vue'),
    redirect: '/setup',
    name: 'setup',
    meta: {
      auth: true,
      navi: true,
      title: 'SET-UP',
      permission: ['USER-00', 'USER-01'],
    },
    children: [
      {
        path: '/setup',
        component: () => import('@/views/setup/SetupView.vue'),
        name: 'Setup',
        meta: {
          auth: true,
          navi: true,
          title: 'SET-UP',
          permission: ['USER-00', 'USER-01'],
        },
      },
    ],
  },
  // {
  //   path: '/knowledgeSearch',
  //   component: () => import('@/views/SubRouterView.vue'),
  //   redirect: '/knowledgeSearch',
  //   name: 'knowledgeSearch',
  //   meta: {
  //     auth: true,
  //     navi: true,
  //     title: '지식검색',  //
  //     eng: 'Knowledge Search',
  //     permission: ['USER-00', 'USER-01'],
  //   },
  //   children: [
  //     {
  //       path: '/knowledgeSearch',
  //       component: () =>
  //         import('@/views/knowledgeSearch/KnowledgeSearchView.vue'),
  //       name: '지식검색',
  //       meta: {
  //         auth: true,
  //         navi: true,
  //         title: '지식검색',
  //         permission: ['USER-00', 'USER-01'],
  //       },
  //     },
  //   ],
  // },
  {
    path: '/404',
    component: () => import('@/views/NotFoundView.vue'),
    meta: { auth: false, navi: false },
  },
  {
    path: '/:pathMatch(.*)*',
    component: () => import('@/views/NotFoundView.vue'),
    redirect: '/404',
    meta: { auth: false, navi: false },
  },
];

const router = createRouter({
  // history: createWebHistory('/'),
  history: createWebHashHistory(),
  routes: getRoutes,
  scrollBehavior() {
    return { top: 0, left: 0 };
  },
});

router.beforeEach((to, from, next) => {
  //인증
  const authStore = useAuthStore();
  const { isLoggedIn } = authStore;
  //메뉴 유무

  //Spinner
  const { setSpinnerStatus } = useSpinner();
  //Alert
  const { setAlertStatus } = useAlert();

  console.log(to.name);
  console.log({ to });

  //인증 체크
  if (to.meta.auth && !isLoggedIn) {
    router.push('/');
  } else {
    setSpinnerStatus(false);
    setAlertStatus({ view: false, message: '' });

    next();
  }
});

export default router;
