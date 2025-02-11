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
                  <button class="btn-m blue add" @click="onUserCreate">
                    <i class="icon"></i>생성
                  </button>
                </div>
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
                    placeholder="이름 또는 사번을 입력하세요."
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
    <!-- 그리드 툴팁 -->
    <GridTooltip
      ref="infoWindow"
      v-if="activeTooltipId !== ''"
      :style="{ left: tooltipXY.x, top: tooltipXY.y }"
      @rename="onRename"
      @chrole="onChrole"
      @infoChange="onInfoChange"
      @resetPassword="onResetPassword"
      @attribute="onAttribute"
    />

    <!-- 상태 변경 확인인 -->
    <AppDialog
      v-model:view="changeState.view"
      :message="changeState.msg"
      @confirm="changeStateConfirm"
    />

    <!-- 사용자 생성 : 사용자 등록정보 변경 -->
    <AppWindow v-model:view="userCreateWindowView" width="810px">
      <UserCreateDialog @save="onUserCreateSave" @cancel="onUserCreateCancel">{{
        editMode ? '사용자 등록정보 변경' : '사용자 생성'
      }}</UserCreateDialog>
    </AppWindow>

    <!-- 사용자 이름 바꾸기 -->
    <AppWindow v-model:view="changeNameWindowView" width="450px">
      <UserChangeNameDialog
        :selectname="selectedName"
        @save="onKnowledgeChangeNameSave"
        @cancel="onKnowledgeChangeNameCancel"
        >사용자 이름 바꾸기</UserChangeNameDialog
      >
    </AppWindow>

    <!-- 사용자 역할 바꾸기 -->
    <AppWindow v-model:view="changeRoleWindowView" width="350px">
      <UserChangeRoleDialog
        :selectId="selectedId"
        @save="onUserRoleChangeSave"
        @cancel="onUserRoleChangeCancel"
        >사용자 역할 바꾸기</UserChangeRoleDialog
      >
    </AppWindow>

    <!-- 비밀번호 초기화 -->
    <AppDialog
      v-model:view="passwordReset.view"
      :message="passwordReset.msg"
      @confirm="passwordResetConfirm"
    />

    <!-- 사용자 속성 -->
    <AppWindow v-model:view="attributeWindowView" width="480px">
      <UserAttributeDialog @close="onUserAttributeClose"
        >사용자 속성</UserAttributeDialog
      >
    </AppWindow>
  </section>
</template>

<script setup>
import { onMounted, onUnmounted, reactive, ref } from 'vue';
import AppGrid from '@/components/grid/AppGrid.vue';
import GridPaging from '@/components/grid/GridPaging.vue';
import BtnUserCellRenderer from '@/components/grid/renderer/BtnUserCellRenderer.vue';
import BtnMoreCellRenderer from '@/components/grid/renderer/BtnMoreCellRenderer.vue';
import SlideCheckRenderer from '@/components/grid/renderer/SlideCheckRenderer.vue';

import SubTitle from '@/components/common/SubTitle.vue';
import UserCreateDialog from './components/userMng/UserCreateDialog.vue';
import UserChangeNameDialog from './components/userMng/UserChangeNameDialog.vue';
import UserAttributeDialog from './components/userMng/UserAttributeDialog.vue';
import UserChangeRoleDialog from './components/userMng/UserChangeRoleDialog.vue';

import GridTooltip from './components/userMng/GridTooltip.vue';
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
  { field: 'name', headerName: '이름 (사번)', flex: 2 },
  {
    field: 'organizationInformation',
    headerName: '조직정보 (직위, 직무)',
    cellClass: 'grid-cell-centered',
    flex: 1.4,
  },
  {
    field: 'rolePermissions',
    headerName: '역할 권한',
    cellClass: 'grid-cell-centered',
    flex: 0.7,
  },
  {
    field: 'createDate',
    headerName: '생성일자',
    cellClass: 'grid-cell-centered',
    flex: 0.7,
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
  {
    field: 'btn',
    headerName: '',
    cellClass: 'grid-cell-centered',
    cellRenderer: BtnUserCellRenderer,
    cellRendererParams: {
      onRenameClick: value => onRenameRow(value),
      onChangeInfoClick: value => onChangeInfoRow(value),
      onRoleChangeClick: value => onUserRoleChange(value),
    },
    flex: 0.5,
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
  for (let i = 0; i < 10; i++) {
    sampleData.push({
      id: i,
      name: '김유신 (NI-2301) kim@nissinfo.com',
      organizationInformation: '부장, 영업1팀 팀장',
      rolePermissions: 'Creator',
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
사용자 생성, 사용자 등록정보 변경
***********/
const userCreateWindowView = ref(false);
const onChangeInfoRow = id => {
  console.log(id);
  editMode.value = true;
  onUserCreate();
};
const onUserCreate = () => {
  userCreateWindowView.value = true;
  activeTooltipId.value = '';
};
//지식비서 생성 저장
const onUserCreateSave = () => {
  userCreateWindowView.value = false;
  editMode.value = false;
  console.log('저장');
};
//지식비서 생성 취소
const onUserCreateCancel = () => {
  userCreateWindowView.value = false;
  editMode.value = false;
  console.log('취소');
};

/******** 
사용자 역할 바꾸기
***********/
const changeRoleWindowView = ref(false);
const onUserRoleChange = id => {
  selectedId.value = id;
  changeRoleWindowView.value = true;
  activeTooltipId.value = '';
};
//지식비서 이름 바꾸기 저장
const onUserRoleChangeSave = title => {
  changeRoleWindowView.value = false;
  selectedId.value = '';
};
//지식비서 이름 바꾸기 취소
const onUserRoleChangeCancel = () => {
  changeRoleWindowView.value = false;
  selectedId.value = '';
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

//역할 바꾸기
const onChrole = () => {
  onUserRoleChange(activeTooltipId.value);
};

//등록정보 변경
const editMode = ref(false);
const onInfoChange = () => {
  editMode.value = true;
  onUserCreate();
};

//비밀번호 초기화
const passwordReset = reactive({
  view: false,
  msg: '비밀번호를 초기화 하시겠습니까?',
});
const onResetPassword = () => {
  passwordReset.view = true;
};
const passwordResetConfirm = () => {
  console.log('비밀번호 초기화');
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
