<template>
  <section class="contents-wrap">
    <div class="content-box">
      <div class="content-top"><SubTitle /></div>
      <div class="content-bottom">
        <div class="knowledge-secretary__wrap role-mng">
          <div class="content-divide col2">
            <div class="content-area col-l">
              <CodeList />
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
                      style="width: 400px"
                      placeholder="코드 이름을 입력하세요."
                    />
                    <button class="btn-m blue search">
                      <i class="icon"></i>검색
                    </button>
                  </div>
                </div>
                <div class="grid-bottom">
                  <AppGrid
                    :rowData="rowData"
                    :columnDefs="colDefs"
                    ref="agGrid"
                    @bodyScroll="onGridScroll"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 그리드 이동 툴팁 -->
    <MoveTooltip
      ref="infoMoveWindow"
      v-if="activeTooltipMoveId !== ''"
      :style="{ left: tooltipXY.x, top: tooltipXY.y }"
      @first="onMoveToTop"
      @up="onMoveUp"
      @down="onMoveDown"
      @end="onMoveToBottom"
    />

    <!-- 그리드 툴팁 -->
    <GridTooltip
      ref="infoWindow"
      v-if="activeTooltipId !== ''"
      :style="{ left: tooltipXY.x, top: tooltipXY.y }"
      @reName="onRename"
      @reCode="onRecode"
      @infoChange="onInfoChange"
      @attribute="onAttribute"
      @first="onFirstMove"
      @up="onUpMove"
      @down="onDownMove"
      @end="onEndMove"
    />

    <!-- 상태 변경 확인 -->
    <AppDialog
      v-model:view="changeState.view"
      :message="changeState.msg"
      @confirm="changeStateConfirm"
    />

    <!-- 이름 바꾸기 -->
    <AppWindow v-model:view="changeNameWindowView" width="450px">
      <CodeChangeNameDialog
        :selectname="selectedName"
        @save="onKnowledgeChangeNameSave"
        @cancel="onKnowledgeChangeNameCancel"
        >이름름 바꾸기</CodeChangeNameDialog
      >
    </AppWindow>

    <!-- 코드 바꾸기 -->
    <AppWindow v-model:view="changeCodeWindowView" width="450px">
      <CodeChangeCodeDialog
        :selectCode="selectedCode"
        @save="onChangeCodeSave"
        @cancel="onChangeCodeCancel"
        >코드 바꾸기</CodeChangeCodeDialog
      >
    </AppWindow>

    <!-- 코드 등록정보 변경 -->
    <AppWindow v-model:view="codeInfoWindowView" width="450px">
      <CodeInfoDialog
        :selectCode="selectedCode"
        @save="onCodeInfoSave"
        @cancel="onCodeInfoCancel"
        >코드 등록정보 변경</CodeInfoDialog
      >
    </AppWindow>

    <!-- 속성 -->
    <AppWindow v-model:view="attributeWindowView" width="480px">
      <CodeAttributeDialog @close="onUserAttributeClose"
        >코드 속성</CodeAttributeDialog
      >
    </AppWindow>
  </section>
</template>

<script setup>
import { onMounted, onUnmounted, reactive, ref } from 'vue';
import AppGrid from '@/components/grid/AppGrid.vue';
import BtnRenameMoveCellRenderer from '@/components/grid/renderer/BtnRenameMoveCellRenderer.vue';
import BtnMoreCellRenderer from '@/components/grid/renderer/BtnMoreCellRenderer.vue';
import SlideCheckRenderer from '@/components/grid/renderer/SlideCheckRenderer.vue';

import SubTitle from '@/components/common/SubTitle.vue';
import CodeChangeNameDialog from '@/views/systemMng/components/code/CodeChangeNameDialog.vue';
import CodeChangeCodeDialog from '@/views/systemMng/components/code/CodeChangeCodeDialog.vue';
import CodeInfoDialog from '@/views/systemMng/components/code/CodeInfoDialog.vue';
import CodeAttributeDialog from '@/views/systemMng/components/code/CodeAttributeDialog.vue';

import GridTooltip from '@/views/systemMng/components/code/GridTooltip.vue';
import MoveTooltip from '@/views/systemMng/components/code/MoveTooltip.vue';

import CodeList from '@/views/systemMng/components/code/CodeList.vue';

import { onClickOutside } from '@vueuse/core';

//버튼 Cell Hide
const cellHide = ref(false);

//검색
const searchOptions = reactive([
  { label: '전체', value: 0 },
  { label: '사용중', value: 1 },
  { label: '사용중지', value: 2 },
]);
const searchSelect = ref(0);
const searchName = ref('');

//그리드
const agGrid = ref(null);
const rowData = ref([]);
const colDefs = ref([
  { field: 'name', headerName: '이름', flex: 2 },
  {
    field: 'code',
    headerName: '코드',
    cellClass: 'grid-cell-centered',
    flex: 2,
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
    flex: 0.7,
  },
  {
    field: 'btn',
    headerName: '',
    cellClass: 'grid-cell-centered',
    cellRenderer: BtnRenameMoveCellRenderer,
    cellRendererParams: {
      onRenameClick: value => onRenameRow(value),
      onMoveRowClick: value => onMoveRow(value),
    },
    flex: 0.7,
    hide: cellHide,
  },
  {
    field: 'link',
    headerName: '',
    cellClass: 'grid-cell-centered',
    cellRenderer: BtnMoreCellRenderer,
    cellRendererParams: {
      onMoreClick: value => callMore(value),
    },
    flex: 0.3,
  },
]);

const attachData = () => {
  const sampleData = [];
  for (let i = 0; i < 50; i++) {
    sampleData.push({
      id: i,
      name: 'GPT-4o' + i,
      code: 'openai_gpt4' + i,
      createDate: '2024.08.17',
      state: false,
      btn: i,
      link: i,
    });
  }
  rowData.value = sampleData;
};
attachData();

const selectedId = ref('');
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
  selectedId.value = id;
  selectedState.value = state;
  changeState.msg = selectedState.value
    ? '사용으로 변경하시겠어요?'
    : '사용중지로 변경하시겠어요?';
  changeState.view = true;
};

const changeStateConfirm = () => {
  const updatedData = rowData.value.map(item =>
    item.id === selectedId.value
      ? { ...item, state: !selectedState.value }
      : item,
  );
  rowData.value = updatedData;
};

/******** 
사용자 이름 바꾸기
***********/
const selectedName = ref('');
const changeNameWindowView = ref(false);
const onRenameRow = id => {
  selectedId.value = id;
  selectedName.value = rowData.value.find(item => item.id === id)?.name;
  changeNameWindowView.value = true;
  activeTooltipId.value = '';
};
//사용자 이름 바꾸기 저장
const onKnowledgeChangeNameSave = title => {
  changeNameWindowView.value = false;
  const updatedData = rowData.value.map(item =>
    item.id === selectedId.value ? { ...item, name: title } : item,
  );
  rowData.value = updatedData;
  selectedName.value = '';
  selectedId.value = '';
  console.log('저장');
};
//사용자 이름 바꾸기 취소
const onKnowledgeChangeNameCancel = () => {
  changeNameWindowView.value = false;
  selectedName.value = '';
  selectedId.value = '';
  console.log('취소');
};

/******** 
코드 바꾸기
***********/
const selectedCode = ref('');
const changeCodeWindowView = ref(false);
const onRecode = () => {
  selectedId.value = activeTooltipId.value;
  selectedCode.value = rowData.value.find(
    item => item.id === selectedId.value,
  )?.code;
  changeCodeWindowView.value = true;
  activeTooltipId.value = '';
};
//사용자 이름 바꾸기 저장
const onChangeCodeSave = code => {
  changeCodeWindowView.value = false;
  const updatedData = rowData.value.map(item =>
    item.id === selectedId.value ? { ...item, code: code } : item,
  );
  rowData.value = updatedData;
  selectedCode.value = '';
  selectedId.value = '';
  console.log('저장');
};
//사용자 이름 바꾸기 취소
const onChangeCodeCancel = () => {
  changeCodeWindowView.value = false;
  selectedCode.value = '';
  selectedId.value = '';
  console.log('취소');
};

/******** 
툴팁에서 위치이동
***********/
const onFirstMove = () => {
  activeTooltipMoveId.value = activeTooltipId.value;
  onMoveToTop();
  activeTooltipMoveId.value = '';
  activeTooltipId.value = '';
};
const onUpMove = () => {
  activeTooltipMoveId.value = activeTooltipId.value;
  onMoveUp();
  activeTooltipMoveId.value = '';
  activeTooltipId.value = '';
};
const onDownMove = () => {
  activeTooltipMoveId.value = activeTooltipId.value;
  onMoveDown();
  activeTooltipMoveId.value = '';
  activeTooltipId.value = '';
};
const onEndMove = () => {
  activeTooltipMoveId.value = activeTooltipId.value;
  onMoveToBottom();
  activeTooltipMoveId.value = '';
  activeTooltipId.value = '';
};

/******** 
Row 위치 이동
***********/
const activeTooltipMoveId = ref('');
const infoMoveWindow = ref(null);
const onMoveRow = values => {
  const { rect, id } = values;
  console.log('------> ', activeTooltipMoveId.value, ' / ', id);
  if (activeTooltipMoveId.value === id) {
    activeTooltipMoveId.value = '';
    return;
  }
  activeTooltipMoveId.value = id;
  const tooltipHeight = 138;
  tooltipXY.x = `${rect.x - 145}px`;
  if (rect.y + tooltipHeight > window.innerHeight) {
    tooltipXY.y = `${rect.y - 120}px`;
  } else {
    tooltipXY.y = `${rect.y}px`;
  }
};
// 맨 위로 이동
const onMoveToTop = () => {
  const index = rowData.value.findIndex(
    item => item.id === activeTooltipMoveId.value,
  );
  if (index !== -1) {
    const [item] = rowData.value.splice(index, 1);
    rowData.value.unshift(item);
    rowData.value = [...rowData.value];
    activeTooltipMoveId.value = '';
  }
};

// 맨 아래로 이동
const onMoveToBottom = () => {
  const index = rowData.value.findIndex(
    item => item.id === activeTooltipMoveId.value,
  );
  if (index !== -1) {
    const [item] = rowData.value.splice(index, 1);
    rowData.value.push(item);
    rowData.value = [...rowData.value];
    activeTooltipMoveId.value = '';
  }
};

// 한 칸 위로 이동
const onMoveUp = () => {
  const index = rowData.value.findIndex(
    item => item.id === activeTooltipMoveId.value,
  );
  if (index > 0) {
    // 첫 번째 요소가 아니면 이동
    const temp = rowData.value[index];
    rowData.value[index] = rowData.value[index - 1];
    rowData.value[index - 1] = temp;
    rowData.value = [...rowData.value];
    activeTooltipMoveId.value = '';
  }
};

// 한 칸 아래로 이동
const onMoveDown = () => {
  const index = rowData.value.findIndex(
    item => item.id === activeTooltipMoveId.value,
  );
  if (index !== -1 && index < rowData.value.length - 1) {
    // 마지막 요소가 아니면 이동
    const temp = rowData.value[index];
    rowData.value[index] = rowData.value[index + 1];
    rowData.value[index + 1] = temp;
    rowData.value = [...rowData.value];
    activeTooltipMoveId.value = '';
  }
};

onClickOutside(infoMoveWindow, event => {
  activeTooltipMoveId.value = '';
});

/******** 
코드 등록정보 변경
***********/
const codeInfoWindowView = ref(false);
const onCodeInfo = () => {
  codeInfoWindowView.value = true;
  activeTooltipId.value = '';
};
const onCodeInfoSave = () => {
  codeInfoWindowView.value = false;
  console.log('저장');
};
const onCodeInfoCancel = () => {
  codeInfoWindowView.value = false;
  console.log('취소');
};

/******** 
속성
***********/
const attributeWindowView = ref(false);
const onUserAttribute = id => {
  selectedId.value = id;
  attributeWindowView.value = true;
  activeTooltipId.value = '';
};
// 속성 닫기
const onUserAttributeClose = () => {
  attributeWindowView.value = false;
  selectedId.value = '';
};

// //그리드 상세툴팁
const activeTooltipId = ref('');
const infoWindow = ref(null);
const tooltipXY = reactive({ x: '0px', y: '0px' });
const callMore = values => {
  const { rect, id } = values;
  activeTooltipId.value = id;
  const tooltipHeight = 198;
  tooltipXY.x = `${rect.x - 155}px`;
  if (rect.y + tooltipHeight > window.innerHeight) {
    tooltipXY.y = `${rect.y - 130}px`;
  } else {
    tooltipXY.y = `${rect.y}px`;
  }
};
onClickOutside(infoWindow, event => {
  activeTooltipId.value = '';
});

// //스크롤 체크
const onGridScroll = () => {
  if (activeTooltipId.value !== '') {
    activeTooltipId.value = '';
  }
  if (activeTooltipMoveId.value !== '') {
    activeTooltipMoveId.value = '';
  }
};

// //스크롤 체크
// const onGridScroll = () => {
//   if (activeTooltipId.value !== '') {
//     activeTooltipId.value = '';
//   }
// };

const handleResize = () => {
  console.log('resize', window.innerWidth);
  if (window.innerWidth < 1500) {
    cellHide.value = true;
  } else {
    cellHide.value = false;
  }
};

//이름 바꾸기
const onRename = () => {
  onRenameRow(activeTooltipId.value);
};

//등록정보 변경
const editMode = ref(false);
const onInfoChange = () => {
  editMode.value = true;
  onCodeInfo();
};

//속성
const onAttribute = () => {
  onUserAttribute(activeTooltipId.value);
};

onMounted(() => {
  window.addEventListener('resize', handleResize);
  handleResize();
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
});
</script>
