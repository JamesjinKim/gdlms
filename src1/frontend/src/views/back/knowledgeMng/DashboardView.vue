<template>
  <section class="contents-wrap">
    <div class="content-box">
      <div class="content-top">
        <SubTitle />
      </div>
      <div class="content-bottom">
        <div class="knowledge-dashbord__wrap">
          <div class="row-top">
            <div class="row-content">
              <div class="title-s">단계별 지식학습</div>
              <div class="content-area">
                <div class="step-count load">
                  <span class="symbol">
                    <i class="icon"></i>
                  </span>
                  <div class="count-info">
                    <div class="info-title">LOAD</div>
                    <div class="counter">
                      <span class="num">
                        <NumberAnimation
                          ref="number1"
                          :from="0"
                          :to="data.load"
                          :duration="0.8"
                          autoplay
                          easing="linear"
                          :format="Math.round"
                        />
                      </span>
                      <span class="txt">건</span>
                    </div>
                  </div>
                </div>
                <div class="step-count split">
                  <span class="symbol">
                    <i class="icon"></i>
                  </span>
                  <div class="count-info">
                    <div class="info-title">SPLIT</div>
                    <div class="counter">
                      <span class="num">
                        <NumberAnimation
                          ref="number1"
                          :from="0"
                          :to="data.split"
                          :duration="0.8"
                          autoplay
                          easing="linear"
                          :format="Math.round"
                        />
                      </span>
                      <span class="txt">건</span>
                    </div>
                  </div>
                </div>
                <div class="step-count embed">
                  <span class="symbol">
                    <i class="icon"></i>
                  </span>
                  <div class="count-info">
                    <div class="info-title">EMBED</div>
                    <div class="counter">
                      <span class="num">
                        <NumberAnimation
                          ref="number1"
                          :from="0"
                          :to="data.embed"
                          :duration="0.8"
                          autoplay
                          easing="linear"
                          :format="Math.round"
                        />
                      </span>
                      <span class="txt">건</span>
                    </div>
                  </div>
                </div>
                <div class="step-count store">
                  <span class="symbol">
                    <i class="icon"></i>
                  </span>
                  <div class="count-info">
                    <div class="info-title">STORE</div>
                    <div class="counter">
                      <span class="num">
                        <NumberAnimation
                          ref="number1"
                          :from="0"
                          :to="data.store"
                          :duration="0.8"
                          autoplay
                          easing="linear"
                          :format="Math.round"
                        />
                      </span>
                      <span class="txt">건</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="row-bottom">
            <div class="row-content">
              <div class="title-s">지식 관리 현황</div>
              <div class="row">
                <div class="content-l">
                  <div class="content-area secretary">
                    <div class="info-area">
                      <div class="info-title">지식비서</div>
                      <div class="counter">
                        <span class="num">
                          <NumberAnimation
                            ref="number1"
                            :from="0"
                            :to="data.knowledge"
                            :duration="0.8"
                            autoplay
                            easing="linear"
                            :format="Math.round"
                          />
                        </span>
                        <span class="txt">건</span>
                      </div>
                    </div>
                  </div>
                  <div class="content-area storage">
                    <div class="info-area">
                      <div class="info-title">스토리지</div>
                      <div class="counter">
                        <span class="num">
                          <NumberAnimation
                            ref="number1"
                            :from="0"
                            :to="data.storage"
                            :duration="0.8"
                            autoplay
                            easing="linear"
                            :format="Math.round"
                          />
                        </span>
                        <span class="txt">건</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="content-r">
                  <div class="content-area">
                    <v-select
                      :options="knowledgeOptions"
                      label="label"
                      index="value"
                      v-model="knowledge"
                      :searchable="false"
                      :clearable="false"
                      :reduce="option => option.value"
                      style="width: 160px"
                      class="knowledge-select"
                    />
                    <AppChart
                      type="bar"
                      :series="data.chart.series"
                      :categories="data.chart.categories"
                      :chartColor="chartColor"
                      height="100%"
                      ref="chartRef"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue';
import SubTitle from '@/components/common/SubTitle.vue';
import AppChart from '@/components/chart/AppChart.vue';
import NumberAnimation from 'vue-number-animation';

const chartRef = ref(null);

const generateRandomData = () => {
  return Array.from({ length: 6 }, () => Math.floor(Math.random() * 100));
};

//단계별 지식학습
const data = ref({
  load: 0,
  split: 0,
  embed: 0,
  store: 0,
  knowledge: 0,
  storage: 0,
  chart: {
    categories: [],
    series: [
      {
        name: '파일건수',
        data: [0, 0, 0, 0, 0, 0],
      },
      {
        name: '벡터건수',
        data: [0, 0, 0, 0, 0, 0],
      },
    ],
  },
});

//지식 관리 현황 챠트
const knowledgeOptions = reactive([
  { label: '전체', value: 0 },
  { label: '최근 1개월', value: 1 },
  { label: '최근 3개월', value: 2 },
  { label: '최근 6개월', value: 3 },
  { label: '최근 1년', value: 4 },
]);

const knowledge = ref(0);

const chartColor = ref(['#4E8FE3', '#FEB019']);

// 챠트 데이터
data.value.chart.categories = [
  '총무업무 지식',
  '회사생활 지식',
  '정보보안 지식',
  '마케팅 지식',
  '법무팀 지식',
  '감사업무 지식',
];

const attachChartData = () => {
  data.value.chart.series = [
    {
      name: '파일건수',
      data: generateRandomData(),
    },
    {
      name: '벡터건수',
      data: generateRandomData(),
    },
  ];
};

const attachCountData = () => {
  data.value.load = 30;
  data.value.split = 120;
  data.value.embed = 25;
  data.value.store = 10;
  data.value.knowledge = 23;
  data.value.storage = 40;
};

const attachData = () => {
  attachCountData();
  attachChartData();
};

onMounted(() => {
  setTimeout(() => {
    attachData();
  }, 500);
});

watch(
  () => knowledge.value,
  () => {
    attachChartData();
  },
);
</script>
