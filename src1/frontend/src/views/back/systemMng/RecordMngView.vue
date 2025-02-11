<template>
  <section class="contents-wrap">
    <div class="content-box">
      <div class="content-top">
        <SubTitle />
      </div>
      <div class="content-bottom">
        <div class="knowledge-secretary__wrap">
          <div class="content-area">
            <div class="grid-wrap">
              <div class="grid-top">
                <div class="top-l"></div>
                <div class="top-r">
                  <v-select
                    :options="actionOptions"
                    label="label"
                    index="value"
                    :reduce="option => option.value"
                    v-model="actionSelected"
                    :searchable="false"
                    :clearable="false"
                    style="width: 120px"
                  />
                  <v-select
                    :options="termOptions"
                    label="label"
                    index="value"
                    :reduce="option => option.value"
                    v-model="termSelected"
                    :searchable="false"
                    :clearable="false"
                    style="width: 130px"
                  />
                  <div class="start-end__date">
                    <AppDatePicker :date="sDate" style="width: 130px" />
                    <span>~</span>
                    <AppDatePicker :date="eDate" style="width: 130px" />
                  </div>
                  <v-select
                    :options="workHistoryOptions"
                    label="label"
                    index="value"
                    :reduce="option => option.value"
                    v-model="workHistorySelected"
                    :searchable="false"
                    :clearable="false"
                    style="width: 120px"
                  />
                  <AppInput
                    v-model="searchKeyword"
                    style="width: 300px"
                    placeholder="키워드를 입력하세요."
                  />
                  <button class="btn-m blue search">
                    <i class="icon"></i>검색
                  </button>
                </div>
              </div>
              <div class="grid-bottom auto">
                <AppGrid
                  :rowData="rowData"
                  :columnDefs="colDefs"
                  domLayout="autoHeight"
                  ref="agGrid"
                />
              </div>
              <div class="grid-page">
                <GridPaging />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { reactive, ref } from 'vue';
import AppGrid from '@/components/grid/AppGrid.vue';
import GridPaging from '@/components/grid/GridPaging.vue';
import AppDatePicker from '@/components/calendar/AppDatePicker.vue';

import SubTitle from '@/components/common/SubTitle.vue';

//버튼 Cell Hide
const cellHide = ref(false);

//액션
const actionOptions = reactive([
  { label: '액션', value: 0 },
  { label: '모두', value: 1 },
  { label: '로그인', value: 2 },
  { label: '로그아웃', value: 3 },
  { label: '생성(등록)', value: 4 },
  { label: '변경', value: 5 },
  { label: '삭제', value: 6 },
  { label: '이동', value: 7 },
  { label: '복제', value: 8 },
]);
const actionSelected = ref(0);

//검색기간간
const termOptions = reactive([
  { label: '검색기간', value: 0 },
  { label: '오늘', value: 1 },
  { label: '최근 1주일', value: 2 },
  { label: '최근 1개월', value: 3 },
  { label: '최근 3개월', value: 4 },
  { label: '최근 6개월', value: 5 },
  { label: '최근 1년', value: 6 },
  { label: '기간 지정', value: 7 },
]);
const termSelected = ref(0);

//작업내역
const workHistoryOptions = reactive([
  { label: '작업내역', value: 1 },
  { label: '메뉴위치', value: 2 },
]);
const workHistorySelected = ref(1);

const searchKeyword = ref('');

//그리드
const agGrid = ref(null);
const rowData = ref([]);
const colDefs = ref([
  { field: 'workHistory', headerName: '작업내역', flex: 3 },
  {
    field: 'menuLocation',
    headerName: '메뉴 위치',
    cellClass: 'grid-cell-centered',
    flex: 1,
  },
  {
    field: 'action',
    headerName: '액션',
    cellClass: 'grid-cell-centered',
    flex: 0.5,
  },
  {
    field: 'worker',
    headerName: '작업자',
    cellClass: 'grid-cell-centered',
    flex: 0.5,
  },
  {
    field: 'createDate',
    headerName: '생성일자',
    cellClass: 'grid-cell-centered',
    flex: 0.7,
  },
]);

const attachData = () => {
  const sampleData = [];
  for (let i = 0; i < 10; i++) {
    sampleData.push({
      id: i,
      workHistory: '회사생활 가이드 회사생활 지식 스토리지 연결',
      menuLocation: '지식관리 > 지식비서',
      action: '연결',
      worker: '홍길동',
      createDate: '2024.08.01 12:34',
    });
  }
  rowData.value = sampleData;
};
attachData();
</script>
