<template>
  <div class="window-wrap">
    <div class="window-top">
      <div class="title">
        <slot></slot>
      </div>
    </div>
    <div class="window-body">
      <div class="stocker-detail detail-infos">
        <div class="stocker-body">
          <div class="stocker-marker">
            <div class="marker-view">
              <img src="/images/img_stocker.png" alt="stocker" />
              <div
                class="marker-pointer marker-1 activePoint"
                v-if="markerData == 1"
              >
                <i class="icon"></i>
              </div>
              <div
                class="marker-pointer marker-2 activePoint"
                v-if="markerData == 2"
              >
                <i class="icon"></i>
              </div>
              <div
                class="marker-pointer marker-3 activePoint"
                v-if="markerData == 3"
              >
                <i class="icon"></i>
              </div>
              <div
                class="marker-pointer marker-4 activePoint"
                v-if="markerData == 4"
              >
                <i class="icon"></i>
              </div>
              <div
                class="marker-pointer marker-5 activePoint"
                v-if="markerData == 5"
              >
                <i class="icon"></i>
              </div>
            </div>
          </div>
          <div class="gas-list">
            <div class="list-box">
              <div class="list-top">A Gas</div>
              <div class="list-body">
                <div class="list-scroll">
                  <ul>
                    <li v-for="item in listData.a" :key="item.id">
                      <div class="row-title">{{ item.title }}</div>
                      <div class="row-num">{{ item.num }}</div>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
            <div class="list-box">
              <div class="list-top">B Gas</div>
              <div class="list-body">
                <div class="list-scroll">
                  <ul>
                    <li v-for="item in listData.b" :key="item.id">
                      <div class="row-title">{{ item.title }}</div>
                      <div class="row-num">{{ item.num }}</div>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const markerData = ref('');
const listData = ref({});
const attachData = () => {
  markerData.value = Math.floor(Math.random() * 5) + 1;
  //리스트
  let sampleListData = {
    a: [],
    b: [],
  };
  for (let i = 0; i < 100; i++) {
    sampleListData.a.push({
      id: i,
      title: '교환전 1차 배관청소',
      num: Math.floor(Math.random() * 100),
    });
    sampleListData.b.push({
      id: i,
      title: '교환전 1차 배관청소',
      num: Math.floor(Math.random() * 100),
    });
  }
  listData.value = sampleListData;
};
attachData();
</script>
