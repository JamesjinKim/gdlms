<template>
  <section class="contents-wrap">
    <div class="content-box">
      <div class="content-top">
        <SubTitle />
      </div>
      <div class="content-bottom">
        <div class="knowledge-secretary__wrap role-mng">
          <div class="content-divide col2">
            <div class="content-area col-l">
              <TreeList @selectNode="onSelectNode" />
            </div>
            <div class="content-area col-r">
              <div class="grid-wrap">
                <div class="grid-top">
                  <div class="top-l"></div>
                  <div class="top-r">
                    <v-select
                      :options="searchOptions"
                      label="label"
                      index="value"
                      :reduce="option => option.value"
                      v-model="searchSelect"
                      :searchable="false"
                      :clearable="false"
                      style="width: 120px"
                    />
                    <AppInput
                      v-model="searchName"
                      style="width: 350px"
                      placeholder="검색어를 입력하세요."
                    />
                    <button class="btn-m blue search">
                      <i class="icon"></i>검색
                    </button>
                  </div>
                </div>
                <div class="grid-bottom">
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
      </div>
    </div>

    <!-- 상태 변경 확인 -->
    <AppDialog
      v-model:view="changeState.view"
      :message="changeState.msg"
      @confirm="changeStateConfirm"
    />
  </section>
</template>

<script setup>
import { reactive, ref } from 'vue';
import AppGrid from '@/components/grid/AppGrid.vue';
import GridPaging from '@/components/grid/GridPaging.vue';
import SubTitle from '@/components/common/SubTitle.vue';
import SlideCheckRenderer from '@/components/grid/renderer/SlideCheckRenderer.vue';
import TreeList from './components/oraganization/TreeList.vue';

const onSelectNode = value => {
  console.log(value);
};

/********
 * 그리드
 *********/
//검색
const searchOptions = reactive([
  { label: '전체', value: 0 },
  { label: '이름', value: 1 },
]);
const searchSelect = ref(0);
const searchName = ref('');

const agGrid = ref(null);
const rowData = ref([]);
const colDefs = ref([
  {
    field: 'name',
    headerName: '이름',
    cellClass: 'grid-cell-centered',
    flex: 1,
  },
  {
    field: 'spot',
    headerName: '직위',
    cellClass: 'grid-cell-centered',
    flex: 1,
  },
  {
    field: 'job',
    headerName: '직무',
    cellClass: 'grid-cell-centered',
    flex: 1,
  },
  {
    field: 'createDate',
    headerName: '생성일자',
    cellClass: 'grid-cell-centered',
    flex: 1,
  },
  {
    field: 'state',
    headerName: '상태',
    cellClass: 'grid-cell-centered',
    cellRenderer: SlideCheckRenderer,
    cellRendererParams: {
      onClick: value => onState(value),
    },
    flex: 0.5,
  },
]);

const selectedGridId = ref('');
const selectedState = ref(false);
/******** 
  상태 변경
***********/
const changeState = reactive({
  view: false,
  msg: '',
});

const onState = value => {
  const { id, state } = value;
  selectedGridId.value = id;
  selectedState.value = state;
  changeState.msg = selectedState.value
    ? '사용으로 변경하시겠어요?'
    : '사용중지로 변경하시겠어요?';
  changeState.view = true;
};

const changeStateConfirm = () => {
  const updatedData = rowData.value.map(item =>
    item.id === selectedGridId.value
      ? { ...item, state: !selectedState.value }
      : item,
  );
  rowData.value = updatedData;
};

const attachData = () => {
  const sampleData = [];
  for (let i = 0; i < 10; i++) {
    sampleData.push({
      id: i,
      name: '김유신',
      spot: '부장',
      job: '팀장',
      createDate: '2024.08.17',
      state: false,
    });
  }
  rowData.value = sampleData;
};
attachData();
</script>
