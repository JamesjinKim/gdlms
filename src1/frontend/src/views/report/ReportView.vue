<template>
  <div class="contents-wrap">
    <SubTitle />
    <div class="contents">
      <div class="grid-wrap">
        <div class="grid-top">
          <div class="top-l"></div>
          <div class="top-r">
            <span class="search-label">기간</span>
            <div class="start-end__date">
              <AppDateTimePicker :date="sDate" style="width: 160px" />
              <span class="divide-date">~</span>
              <AppDateTimePicker :date="eDate" style="width: 160px" />
            </div>
            <span class="search-label">호기</span>
            <v-select
              :options="titleOptions"
              label="label"
              index="value"
              :reduce="option => option.value"
              v-model="titleSelected"
              :searchable="false"
              :clearable="false"
              style="width: 150px"
            />
            <span class="search-label">항목</span>
            <v-select
              :options="itemOptions"
              label="label"
              index="value"
              :reduce="option => option.value"
              v-model="itemSelected"
              :searchable="false"
              :clearable="false"
              style="width: 150px"
            />

            <button class="btn-m blue search"><i class="icon"></i>검색</button>
          </div>
        </div>
        <div class="grid-bottom">
          <AppGrid :rowData="rowData" :columnDefs="colDefs" ref="agGrid" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import SubTitle from '@/components/common/SubTitle.vue';
import AppGrid from '@/components/grid/AppGrid.vue';
import AppDateTimePicker from '@/components/calendar/AppDateTimePicker.vue';
import vSelect from 'vue-select';
import { ref, reactive } from 'vue';

const sDate = ref(new Date());
const eDate = ref(new Date());

// 호기
const titleOptions = reactive([
  { label: '전체', value: 0 },
  { label: '1호기', value: 1 },
  { label: '2호기', value: 2 },
  { label: '3호기', value: 3 },
]);
const titleSelected = ref(0);

// 항목
const itemOptions = reactive([
  { label: '전체', value: 0 },
  { label: '항목1', value: 1 },
  { label: '항목2', value: 2 },
  { label: '항목3', value: 3 },
]);
const itemSelected = ref(0);

const rowData = ref([]);
const colDefs = ref([
  {
    field: 'no',
    headerName: 'No',
    cellClass: 'grid-cell-centered',
    flex: 0.3,
  },
  {
    field: 'title',
    headerName: '제목',
    flex: 4,
  },
  {
    field: 'writer',
    headerName: '등록자',
    cellClass: 'grid-cell-centered',
    flex: 0.7,
  },
  {
    field: 'createDate',
    headerName: '등록일자',
    cellClass: 'grid-cell-centered',
    flex: 0.7,
  },
]);

const attachData = () => {
  const sampleData = [];
  for (let i = 0; i < 100; i++) {
    sampleData.push({
      id: i,
      no: i + 1,
      title: '제목입니다' + i,
      writer: '관리자',
      createDate: '2024.08.17',
    });
  }
  rowData.value = sampleData;
};
attachData();
</script>
