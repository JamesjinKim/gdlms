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
                <div class="top-l">
                  <button class="btn-m blue add" @click="onKnowledgeSecretary">
                    <i class="icon"></i>생성
                  </button>
                </div>
                <div class="top-r">
                  <AppInput
                    v-model="searchName"
                    style="width: 400px"
                    placeholder="지식비서 이름을 입력하세요."
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
    <!-- 그리드 툴팁 -->
    <GridTooltip
      ref="infoWindow"
      v-if="activeTooltipId !== ''"
      :style="{ left: tooltipXY.x, top: tooltipXY.y }"
      @rename="onRename"
      @remove="onRemove"
      @share="onShare"
      @infoChange="onInfoChange"
      @storageConnect="onStorageConnect"
      @attribute="onAttribute"
    />

    <!-- 지식비서 이름 바꾸기 -->
    <AppWindow v-model:view="changeNameWindowView" width="450px">
      <KnowledgeChangeNameDialog
        :selectname="selectedName"
        @save="onKnowledgeChangeNameSave"
        @cancel="onKnowledgeChangeNameCancel"
        >지식비서 이름 바꾸기</KnowledgeChangeNameDialog
      >
    </AppWindow>

    <!-- 삭제 확인 -->
    <AppDialog
      v-model:view="removeRow.view"
      :message="removeRow.msg"
      @confirm="cellRemoveConfirm"
    />

    <!-- 지식비서 공유하기 -->
    <AppWindow v-model:view="shareWindowView" width="500px">
      <KnowledgeShareDialog
        :selectId="selectedId"
        @save="onKnowledgeShareSave"
        @cancel="onKnowledgeShareCancel"
        >지식비서 공유하기</KnowledgeShareDialog
      >
    </AppWindow>

    <!-- 지식비서 생성 : 지식비서 등록정보 변경 -->
    <AppWindow v-model:view="secretaryWindowView" width="810px">
      <KnowledgeSecretaryDialog
        @save="onKnowledgeSecretarySave"
        @cancel="onKnowledgeSecretaryCancel"
        >{{
          editMode ? '지식비서 등록정보 변경' : '지식비서 생성'
        }}</KnowledgeSecretaryDialog
      >
    </AppWindow>

    <!-- 스토리지 연결하기 -->
    <AppWindow v-model:view="storageConnectWindowView" width="450px">
      <KnowledgeStorageConnectDialog
        @save="onKnowledgeStorageConnectSave"
        @cancel="onKnowledgeStorageConnectCancel"
        >스토리지 연결하기</KnowledgeStorageConnectDialog
      >
    </AppWindow>

    <!-- 지식비서 속성 -->
    <AppWindow v-model:view="attributeWindowView" width="480px">
      <KnowledgeAttributeDialog @close="onKnowledgeAttributeClose"
        >지식비서 속성</KnowledgeAttributeDialog
      >
    </AppWindow>
  </section>
</template>

<script setup>
import { onMounted, onUnmounted, reactive, ref } from 'vue';
import AppGrid from '@/components/grid/AppGrid.vue';
// import BtnRenameRemoveCellRenderer from '@/components/grid/renderer/BtnRenameRemoveCellRenderer.vue';
import BtnKnowledgeSecretaryCellRenderer from '@/components/grid/renderer/BtnKnowledgeSecretaryCellRenderer.vue';
import BtnMoreCellRenderer from '@/components/grid/renderer/BtnMoreCellRenderer.vue';
import SubTitle from '@/components/common/SubTitle.vue';
import KnowledgeSecretaryDialog from './components/knowledgeSecretary/KnowledgeSecretaryDialog.vue';
import KnowledgeChangeNameDialog from './components/knowledgeSecretary/KnowledgeChangeNameDialog.vue';
import KnowledgeStorageConnectDialog from './components/knowledgeSecretary/KnowledgeStorageConnectDialog.vue';
import KnowledgeAttributeDialog from './components/knowledgeSecretary/KnowledgeAttributeDialog.vue';
import KnowledgeShareDialog from './components/knowledgeSecretary/KnowledgeShareDialog.vue';

import GridTooltip from './components/knowledgeSecretary/GridTooltip.vue';
import { onClickOutside } from '@vueuse/core';

//버튼 Cell Hide
const cellHide = ref(false);

//검색
const searchName = ref('');

//그리드
const agGrid = ref(null);
const rowData = ref([]);
const colDefs = ref([
  { field: 'name', headerName: '이름', flex: 2 },
  {
    field: 'model',
    headerName: '모델',
    cellClass: 'grid-cell-centered',
    flex: 1,
  },
  {
    field: 'author',
    headerName: '작성자',
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
    field: 'storage',
    headerName: '스토리지',
    cellClass: 'grid-cell-centered',
    flex: 1,
  },
  {
    field: 'btn',
    headerName: '',
    cellClass: 'grid-cell-centered',
    cellRenderer: BtnKnowledgeSecretaryCellRenderer,
    cellRendererParams: {
      onRenameClick: value => onRenameRow(value),
      onConnectClick: value => onConnectRow(value),
      onRemoveClick: value => onRemoveRow(value),
    },
    flex: 0.8,
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
  for (let i = 0; i < 100; i++) {
    sampleData.push({
      id: i,
      name: '인사 총무 업무 비서' + (i + 1),
      model: 'GPT-4o',
      author: '닛시인포',
      createDate: '2024.08.17',
      storage: '총무업무 지식',
      btn: i,
      link: i,
    });
  }
  rowData.value = sampleData;
};
attachData();

// callDetailInfo 메소드 정의
const cellRemoveConfirm = () => {
  const updatedData = rowData.value.filter(
    item => item.id !== selectedId.value,
  );
  rowData.value = updatedData;
  selectedId.value = '';
};

/******** 
지식비서 생성
***********/
const secretaryWindowView = ref(false);
const onKnowledgeSecretary = () => {
  secretaryWindowView.value = true;
  activeTooltipId.value = '';
};
//지식비서 생성 저장
const onKnowledgeSecretarySave = () => {
  secretaryWindowView.value = false;
  console.log('저장');
};
//지식비서 생성 취소
const onKnowledgeSecretaryCancel = () => {
  secretaryWindowView.value = false;
  console.log('취소');
};

/******** 
지식비서 공유하기
***********/
const shareWindowView = ref(false);
const onKnowledgeShare = id => {
  selectedId.value = id;
  shareWindowView.value = true;
  activeTooltipId.value = '';
};
//지식비서 이름 바꾸기 저장
const onKnowledgeShareSave = title => {
  shareWindowView.value = false;
  selectedId.value = '';
};
//지식비서 이름 바꾸기 취소
const onKnowledgeShareCancel = () => {
  shareWindowView.value = false;
  selectedId.value = '';
};

/******** 
지식비서 이름 바꾸기
***********/
const selectedName = ref('');
const changeNameWindowView = ref(false);
const onRenameRow = id => {
  selectedId.value = id;
  selectedName.value = rowData.value.find(item => item.id === id)?.name;
  changeNameWindowView.value = true;
  activeTooltipId.value = '';
};
//지식비서 이름 바꾸기 저장
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
//지식비서 이름 바꾸기 취소
const onKnowledgeChangeNameCancel = () => {
  changeNameWindowView.value = false;
  selectedName.value = '';
  selectedId.value = '';
  console.log('취소');
};

/******** 
스토리지 연결하기
***********/
const onConnectRow = id => {
  onKnowledgeStorageStorageConnect(id);
};
const storageConnectWindowView = ref(false);
const onKnowledgeStorageStorageConnect = id => {
  selectedId.value = id;
  storageConnectWindowView.value = true;
  activeTooltipId.value = '';
};
//지식비서 이름 바꾸기 저장
const onKnowledgeStorageConnectSave = title => {
  storageConnectWindowView.value = false;
  selectedId.value = '';
};
//지식비서 이름 바꾸기 취소
const onKnowledgeStorageConnectCancel = () => {
  storageConnectWindowView.value = false;
  selectedId.value = '';
};

/******** 
속성
***********/
const attributeWindowView = ref(false);
const onKnowledgeAttributeConnect = id => {
  selectedId.value = id;
  attributeWindowView.value = true;
  activeTooltipId.value = '';
};
// 속성 닫기
const onKnowledgeAttributeClose = () => {
  attributeWindowView.value = false;
  selectedId.value = '';
};

/******** 
삭제하기
***********/
const removeRow = reactive({
  view: false,
  msg: '정말로 삭제하시겠습니까?',
});
const selectedId = ref('');
const onRemoveRow = id => {
  selectedId.value = id;
  removeRow.view = true;
  activeTooltipId.value = '';
};

// //그리드 상세툴팁
const activeTooltipId = ref('');
const infoWindow = ref(null);
const tooltipXY = reactive({ x: '0px', y: '0px' });
const callMore = values => {
  const { rect, id } = values;
  activeTooltipId.value = id;
  const tooltipHeight = 202;
  tooltipXY.x = `${rect.x - 165}px`;
  if (rect.y + tooltipHeight > window.innerHeight) {
    tooltipXY.y = `${rect.y - 120}px`;
  } else {
    tooltipXY.y = `${rect.y + 10}px`;
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
};

const handleResize = () => {
  if (window.innerWidth < 1500) {
    cellHide.value = true;
  } else {
    cellHide.value = false;
  }
};

const onRename = () => {
  onRenameRow(activeTooltipId.value);
};
const onRemove = () => {
  onRemoveRow(activeTooltipId.value);
};
const onShare = () => {
  onKnowledgeShare(activeTooltipId.value);
};
const editMode = ref(false);
const onInfoChange = () => {
  editMode.value = true;
  onKnowledgeSecretary();
};
const onStorageConnect = () => {
  onKnowledgeStorageStorageConnect(activeTooltipId.value);
};
const onAttribute = () => {
  onKnowledgeAttributeConnect(activeTooltipId.value);
};

onMounted(() => {
  window.addEventListener('resize', handleResize);
  handleResize();
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
});
</script>
