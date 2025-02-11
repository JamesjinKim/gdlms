import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-balham.css';
import '@vuepic/vue-datepicker/dist/main.css';
import 'sl-vue-tree-next/sl-vue-tree-next-minimal.css';
import '@/assets/sass/main.scss';
import { createApp } from 'vue';
import App from './App.vue';

import router from '@/router';
import { createPinia } from 'pinia';
// import globalComponents from './plugins/global-components';
import VueApexCharts from 'vue3-apexcharts';
import FloatingVue from 'floating-vue';

const app = createApp(App);

app
  // .use(globalComponents)
  .use(VueApexCharts)
  .use(FloatingVue)
  // .use(dayjs)
  .use(createPinia())
  .use(router)
  .mount('#app');
