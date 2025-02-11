<template>
  <div class="contents-wrap main">
    <div class="main-top">
      <div class="main-row">
        <SubTitle class="non-border" />
        <button class="btn-allShutDown">All ShutDown</button>
      </div>
    </div>

    <div class="contents">
      <div class="main-wrap">
        <div class="side">
          <AlimComp :data="alimData" />
          <StockerComp
            :data="stockerData"
            :agvData="agvData"
            @stockView="onStockerView"
          />
        </div>
        <div class="content">
          <CabinetComp :data="cabinetData" :agvData="agvData" />
          <div class="agv-area">
            <div
              class="agv-wrap start"
              :class="`state${agvData.state}`"
              v-if="agvData.position === 'start'"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Stocker 상세보기 -->
    <AppWindow v-model:view="stockerView" width="1145px">
      <StockerDialog @close="onStockerClose">Stocker 상세보기</StockerDialog>
    </AppWindow>
  </div>
</template>

<script setup>
import SubTitle from '@/components/common/SubTitle.vue';
import StockerComp from './components/StockerComp.vue';
import CabinetComp from './components/CabinetComp.vue';
import AlimComp from './components/AlimComp.vue';
import AppWindow from '@/components/ui/AppWindow.vue';
import StockerDialog from './components/StockerDialog.vue';
import { onUnmounted, reactive, ref } from 'vue';

// Stocker 상세보기
const stockerView = ref(false);
const onStockerView = () => {
  stockerView.value = true;
};
const onStockerClose = () => {
  stockerView.value = false;
};

//발생 알림
const alimData = ref([]);
const getAlimData = () => {
  let sampleData = [];
  for (let i = 0; i < 50; i++) {
    sampleData.push({
      id: i,
      title: '알림 발생 메세지' + (i + 1),
      date: '25.01.10 12:00',
    });
  }
  alimData.value = sampleData;
};

// Stocker
const stockerData = ref({
  id: '',
  a: {
    state: 0,
    wf6: 0,
    able: 0,
    reserved1: 0,
    reserved2: 0,
  },
  b: {
    state: 0,
    cfo: 0,
    unable: 0,
    reserved1: 0,
    reserved2: 0,
  },
});
const getStockerData = () => {
  let sampleData = {
    id: 1,
    a: {
      state: Math.floor(Math.random() * 3) + 1,
      wf6: Math.floor(Math.random() * 500),
      able: Math.floor(Math.random() * 500),
      reserved1: Math.floor(Math.random() * 500),
      reserved2: Math.floor(Math.random() * 500),
    },
    b: {
      state: Math.floor(Math.random() * 3) + 1,
      cfo: Math.floor(Math.random() * 500),
      unable: Math.floor(Math.random() * 500),
      reserved1: Math.floor(Math.random() * 500),
      reserved2: Math.floor(Math.random() * 500),
    },
  };
  stockerData.value = sampleData;
};

// 캐비넷
const total = 100;

const cabinetData = ref([]);
const getCabinetData = () => {
  let sampleData = [];
  for (let i = 0; i < total; i++) {
    sampleData.push({
      id: i + 1,
      type: 'WF6',
      a: {
        state: Math.floor(Math.random() * 3) + 1,
        pt2a: Math.floor(Math.random() * 100),
        pt1a: Math.floor(Math.random() * 100),
        wa: Math.floor(Math.random() * 100),
        lineHeater: Math.floor(Math.random() * 100),
        jacket: Math.floor(Math.random() * 100),
        heater: Math.floor(Math.random() * 100),
        reserved: Math.floor(Math.random() * 100),
      },
      b: {
        state: Math.floor(Math.random() * 3) + 1,
        pt2b: Math.floor(Math.random() * 100),
        pt1b: Math.floor(Math.random() * 100),
        wb: Math.floor(Math.random() * 100),
        lineHeater: Math.floor(Math.random() * 100),
        jacket: Math.floor(Math.random() * 100),
        heater: Math.floor(Math.random() * 100),
        reserved: Math.floor(Math.random() * 100),
      },
    });
  }
  cabinetData.value = sampleData;
};

// position: start, cabinet, stocker
// state: 컬러 상태값 1~4 (green, yellow, blue, red)
// cabinetId : cabinet id
// port: cabinet/stocker port
const agvData = reactive({
  position: 'start',
  state: 1,
  cabinetId: '',
  cabinetPort: '',
  stockerPort: '',
});

const getAgvData = () => {
  const position = ['start', 'cabinet', 'stocker'];
  const port = ['a', 'b'];
  agvData.position = position[Math.floor(Math.random() * 3)];
  // agvData.position = position[0];
  agvData.cabinetId = Math.floor(Math.random() * total) + 1;
  agvData.cabinetPort = port[Math.floor(Math.random() * 2)];
  agvData.stockerPort = port[Math.floor(Math.random() * 2)];
  agvData.state = Math.floor(Math.random() * 4) + 1;

  checkScrollMove();
  console.log('agv=', agvData);
  console.log('interval 실행');
};
const checkScrollMove = () => {
  if (agvData.position === 'cabinet') {
    setTimeout(() => {
      document
        .querySelector(`.cabinet${agvData.cabinetId}`)
        .scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 100);
  }
};

const attachData = () => {
  //발생 알림
  getAlimData();
  // Stocker
  getStockerData();
  // 캐비넷
  getCabinetData();
  // AGV
  getAgvData();
};

let interval = null;
let agvInterval = null;
const startInterval = () => {
  interval = setInterval(() => {
    // Stocker
    getStockerData();
    // 캐비넷
    getCabinetData();
    console.log('interval');
  }, 3000);
  agvInterval = setInterval(() => {
    // AGV
    getAgvData();
    console.log('agvInterval');
  }, 5000);
};

attachData();
startInterval();

onUnmounted(() => {
  clearInterval(interval);
  clearInterval(agvInterval);
});
</script>
