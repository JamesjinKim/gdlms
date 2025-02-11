<template>
  <section class="contents-wrap">
    <div class="content-box">
      <div class="content-top">
        <SubTitle />
      </div>
      <div class="content-bottom">
        <div class="knowledge-storage__wrap">
          <div class="content-divide col2">
            <div class="content-area col-l">
              <div class="grid-wrap">
                <div class="grid-top">
                  <div class="top-l">
                    <button
                      class="btn-m blue add"
                      @click="onKnowledgeSecretary"
                    >
                      <i class="icon"></i>생성
                    </button>
                  </div>
                  <div class="top-r">
                    <AppInput
                      v-model="searchName"
                      style="width: 270px"
                      placeholder="스토리지 이름을 입력하세요."
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
            <div class="content-area col-r">
              <div class="grid-wrap">
                <div class="grid-top">
                  <div class="top-l"></div>
                  <div class="top-r">
                    <AppInput
                      style="width: 300px"
                      placeholder="파일 이름을 입력하세요."
                    />
                    <button class="btn-m blue search">
                      <i class="icon"></i>검색
                    </button>
                  </div>
                </div>
                <div class="grid-bottom">
                  <AppFileupload ref="fileuploadList" />
                </div>
                <div class="grid-btns">
                  <div class="btn-l">
                    <button
                      class="btn-m file-upload"
                      @click="fileuploadList.open"
                    >
                      <i class="icon"></i>파일 업로드
                    </button>
                  </div>
                  <div class="btn-l">
                    <button class="btn-m blue"><i class="icon"></i>저장</button>
                  </div>
                </div>
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
      @copybook="onCopybookRow"
      @infoChange="onKnowledgeChangeInfo"
      @attribute="onAttribute"
    />

    <!-- 스토리지 생성 -->
    <AppWindow v-model:view="secretaryWindowView" width="1200px">
      <KnowledgeSecretaryDialog
        @save="onKnowledgeSecretarySave"
        @cancel="onKnowledgeSecretaryCancel"
        >스토리지 생성</KnowledgeSecretaryDialog
      >
    </AppWindow>

    <!-- 스토리지지 이름 바꾸기 -->
    <AppWindow v-model:view="changeNameWindowView" width="450px">
      <KnowledgeChangeNameDialog
        :selectname="selectedName"
        @save="onKnowledgeChangeNameSave"
        @cancel="onKnowledgeChangeNameCancel"
        >스토리지 이름 바꾸기</KnowledgeChangeNameDialog
      >
    </AppWindow>

    <!-- 삭제 확인 -->
    <AppDialog
      v-model:view="removeRow.view"
      :message="removeRow.msg"
      @confirm="cellRemoveConfirm"
    />

    <!-- 스토리지 사본 만들기 -->
    <AppWindow v-model:view="copybookWindowView" width="450px">
      <KnowledgeCopybookDialog
        @save="onKnowledgeCopybookSave"
        @cancel="onKnowledgeCopybookCancel"
        >스토리지 사본 만들기</KnowledgeCopybookDialog
      >
    </AppWindow>

    <!-- 스토리지 등록정보 변경 -->
    <AppWindow v-model:view="changeInfoWindowView" width="450px">
      <KnowledgeChangeInfoDialog
        @save="onKnowledgeChangeInfoSave"
        @cancel="onKnowledgeChangeInfoCancel"
        >스토리지 등록정보 변경</KnowledgeChangeInfoDialog
      >
    </AppWindow>

    <!-- 스토리지지 속성 -->
    <AppWindow v-model:view="attributeWindowView" width="600px">
      <KnowledgeAttributeDialog @close="onKnowledgeAttributeClose"
        >스토리지지 속성</KnowledgeAttributeDialog
      >
    </AppWindow>
  </section>
</template>

<script setup>
import { onMounted, onUnmounted, reactive, ref } from 'vue';
import AppGrid from '@/components/grid/AppGrid.vue';
import BtnStorageCellRenderer from '@/components/grid/renderer/BtnStorageCellRenderer.vue';
import BtnMoreCellRenderer from '@/components/grid/renderer/BtnMoreCellRenderer.vue';
import SubTitle from '@/components/common/SubTitle.vue';
import KnowledgeSecretaryDialog from './components/storage/KnowledgeSecretaryDialog.vue';
import KnowledgeCopybookDialog from './components/storage/KnowledgeCopybookDialog.vue';
import KnowledgeChangeNameDialog from './components/knowledgeSecretary/KnowledgeChangeNameDialog.vue';
import KnowledgeAttributeDialog from './components/storage/KnowledgeAttributeDialog.vue';
import KnowledgeChangeInfoDialog from './components/storage/KnowledgeChangeInfoDialog.vue';
import AppFileupload from '@/components/ui/AppFileupload.vue';

import GridTooltip from './components/storage/GridTooltip.vue';
import { onClickOutside } from '@vueuse/core';

//버튼 Cell Hide
const cellHide = ref(false);

//검색
const searchName = ref('');

//그리드
const agGrid = ref(null);
const rowData = ref([]);
const colDefs = ref([
  { field: 'name', headerName: '이름', flex: 1.3 },
  {
    field: 'keyword',
    headerName: '주요 키워드',
    flex: 2,
  },
  {
    field: 'btn',
    headerName: '',
    cellClass: 'grid-cell-centered',
    cellRenderer: BtnStorageCellRenderer,
    cellRendererParams: {
      onRenameClick: value => onRenameRow(value),
      onCopyClick: value => onCopyRow(value),
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
      keyword: '사규,보안규정,시간관리',
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
스토리지지 생성
***********/
const secretaryWindowView = ref(false);
const onKnowledgeSecretary = () => {
  secretaryWindowView.value = true;
  activeTooltipId.value = '';
};
//스토리지지 생성 저장
const onKnowledgeSecretarySave = () => {
  secretaryWindowView.value = false;
  console.log('저장');
};
//스토리지지 생성 취소
const onKnowledgeSecretaryCancel = () => {
  secretaryWindowView.value = false;
  console.log('취소');
};

/******** 
스토리지지 이름 바꾸기
***********/
const selectedName = ref('');
const changeNameWindowView = ref(false);
const onRenameRow = id => {
  selectedId.value = id;
  selectedName.value = rowData.value.find(item => item.id === id)?.name;
  changeNameWindowView.value = true;
  activeTooltipId.value = '';
};
//스토리지지 이름 바꾸기 저장
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
//스토리지지 이름 바꾸기 취소
const onKnowledgeChangeNameCancel = () => {
  changeNameWindowView.value = false;
  selectedName.value = '';
  selectedId.value = '';
  console.log('취소');
};

/******** 
스토리지지 사본 만들기
***********/
const copybookWindowView = ref(false);
const onCopyRow = id => {
  selectedId.value = id;
  copybookWindowView.value = true;
  activeTooltipId.value = '';
};
const onCopybookRow = () => {
  onCopyRow(activeTooltipId.value);
};
//스토리지지 이름 바꾸기 저장
const onKnowledgeCopybookSave = () => {
  copybookWindowView.value = false;
  selectedId.value = '';
  console.log('저장');
};
//스토리지지 이름 바꾸기 취소
const onKnowledgeCopybookCancel = () => {
  copybookWindowView.value = false;
  selectedId.value = '';
  console.log('취소');
};

/******** 
스토리지 등록정보 변경
***********/
const changeInfoWindowView = ref(false);
const onKnowledgeChangeInfo = () => {
  selectedId.value = activeTooltipId.value;
  changeInfoWindowView.value = true;
  activeTooltipId.value = '';
};
// 저장장
const onKnowledgeChangeInfoSave = () => {
  changeInfoWindowView.value = false;
  selectedId.value = '';
};
// 닫기기
const onKnowledgeChangeInfoCancel = () => {
  changeInfoWindowView.value = false;
  selectedId.value = '';
};

/******** 
속성
***********/
const attributeWindowView = ref(false);
const onKnowledgeAttribute = id => {
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
  tooltipXY.x = `${rect.x - 140}px`;
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
  console.log('resize', window.innerWidth);
  if (window.innerWidth < 1600) {
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

const onAttribute = () => {
  onKnowledgeAttribute(activeTooltipId.value);
};

const fileuploadList = ref(null);

onMounted(() => {
  window.addEventListener('resize', handleResize);
  handleResize();
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
});
</script>
