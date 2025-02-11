<template>
  <div class="nav-wrap">
    <div class="nav-box">
      <h1 class="logo" @click="onMain"></h1>
      <Navigation :navis="naviData" />
      <div class="util">
        <ul>
          <li>
            <div class="btn logout" @click="onLogout" title="로그아웃">
              <i class="logout-icon"></i>
            </div>
          </li>
        </ul>
      </div>
    </div>
    <AppDialog
      v-model:view="confirmState.view"
      :title="confirmState.title"
      :message="confirmState.message"
      @confirm="goLogout"
    />
  </div>
</template>

<script setup>
import { defineAsyncComponent, reactive } from 'vue';
const AppDialog = defineAsyncComponent(() =>
  import('@/components/ui/AppDialog.vue'),
);
import Navigation from '@/components/header/Navigation.vue';

import { getRoutes } from '@/router/index';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
const { logout } = authStore;
const confirmState = reactive({
  view: false,
  message: '로그아웃 하시겠습니까?',
});
const router = useRouter();
const onLogout = () => {
  confirmState.view = true;
};
const goLogout = () => {
  logout();
  router.push('/');
};

const generateNavis = () => {
  let menus = [];
  getRoutes.forEach(route => {
    if (route.meta && route.meta.navi) {
      const menu = {
        title: route.meta.title,
        path: route.path.replace(':id?', ''),
        lv2: [],
      };

      route.meta.navi &&
        route.children &&
        route.children.forEach(sub1 => {
          if (sub1.meta.navi) {
            const lv2Menu = {
              title: sub1.meta.title,
              link: sub1.path.replace(':id?', ''),
            };
            menu.lv2.push(lv2Menu);
          }
        });
      menus.push(menu);
    }
  });

  // console.log('menus=', menus);
  return menus;
};

const naviData = reactive(generateNavis());
console.log('naviData=', naviData);
const onMain = () => {
  router.push('/main');
};
</script>
