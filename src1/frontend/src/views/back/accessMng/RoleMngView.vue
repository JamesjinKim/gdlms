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
              <RoleList />
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
                      placeholder="메뉴 이름을 입력하세요."
                    />
                    <button class="btn-m blue search">
                      <i class="icon"></i>검색
                    </button>
                    <button class="btn-m dark-blue ml0">권한 저장</button>
                  </div>
                </div>
                <div class="grid-bottom">
                  <AppGrid
                    :rowData="rowData"
                    :columnDefs="colDefs"
                    @cell-value-changed="onCellValueChanged"
                    ref="agGrid"
                  />
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
import { onMounted, onUnmounted, reactive, ref } from 'vue';
import AppGrid from '@/components/grid/AppGrid.vue';
import CustomHeader from '@/components/grid/renderer/CustomHeader.vue';
import SubTitle from '@/components/common/SubTitle.vue';
import RoleList from './components/roleMng/RoleList.vue';

/********
 * 그리드
 *********/
//검색
const searchOptions = reactive([
  { label: '전체', value: 0 },
  { label: '관리자', value: 1 },
  { label: '삭제', value: 2 },
  { label: '변경', value: 3 },
  { label: '쓰기', value: 4 },
  { label: '읽기', value: 5 },
  { label: '접근불가', value: 6 },
]);
const searchSelect = ref(0);
const searchName = ref('');

//그리드
const agGrid = ref(null);
const rowData = ref([]);

const adminChecked = ref(false);
const deleteChecked = ref(false);
const changeChecked = ref(false);
const writeChecked = ref(false);
const readChecked = ref(false);
const noChangeChecked = ref(false);

const colDefs = ref([
  {
    field: 'mainMenu',
    headerName: '대메뉴',
    flex: 2,
    cellClass: 'grid-cell-centered',
  },
  {
    field: 'submenu',
    headerName: '소메뉴',
    flex: 2,
    cellClass: 'grid-cell-centered',
  },
  {
    field: 'admin',
    headerName: '관리자',
    editable: true,
    headerComponent: CustomHeader,
    headerComponentParams: {
      headCheck: adminChecked, // title을 전달
      onHeaderClick: value => callHeaderInfo(value), // 부모 메서드 전달
    },
    flex: 1,
    cellClass: 'grid-cell-centered',
  },
  {
    field: 'delete',
    headerName: '삭제',
    editable: true,
    headerComponent: CustomHeader,
    headerComponentParams: {
      headCheck: deleteChecked, // title을 전달
      onHeaderClick: value => callHeaderInfo(value), // 부모 메서드 전달
    },
    flex: 1,
    cellClass: 'grid-cell-centered',
  },
  {
    field: 'change',
    headerName: '변경',
    editable: true,
    headerComponent: CustomHeader,
    headerComponentParams: {
      headCheck: changeChecked, // title을 전달
      onHeaderClick: value => callHeaderInfo(value), // 부모 메서드 전달
    },
    flex: 1,
    cellClass: 'grid-cell-centered',
  },
  {
    field: 'write',
    headerName: '쓰기',
    editable: true,
    headerComponent: CustomHeader,
    headerComponentParams: {
      headCheck: writeChecked, // title을 전달
      onHeaderClick: value => callHeaderInfo(value), // 부모 메서드 전달
    },
    flex: 1,
    cellClass: 'grid-cell-centered',
  },
  {
    field: 'read',
    headerName: '읽기',
    editable: true,
    headerComponent: CustomHeader,
    headerComponentParams: {
      headCheck: readChecked, // title을 전달
      onHeaderClick: value => callHeaderInfo(value), // 부모 메서드 전달
    },
    flex: 1,
    cellClass: 'grid-cell-centered',
  },
  {
    field: 'noChange',
    headerName: '변경불가',
    editable: true,
    headerComponent: CustomHeader,
    headerComponentParams: {
      headCheck: noChangeChecked, // title을 전달
      onHeaderClick: value => callHeaderInfo(value), // 부모 메서드 전달
    },
    flex: 1.2,
    cellClass: 'grid-cell-centered',
  },
]);

const callHeaderInfo = params => {
  console.log(params);
  if (params.column.colId === 'admin') {
    adminChecked.value = !adminChecked.value;
    if (adminChecked.value) {
      rowData.value.forEach(data => {
        data.admin = true;
      });
    } else {
      rowData.value.forEach(data => {
        data.admin = false;
      });
    }
  }

  if (params.column.colId === 'delete') {
    deleteChecked.value = !deleteChecked.value;
    if (deleteChecked.value) {
      rowData.value.forEach(data => {
        data.delete = true;
      });
    } else {
      rowData.value.forEach(data => {
        data.delete = false;
      });
    }
  }

  if (params.column.colId === 'change') {
    changeChecked.value = !changeChecked.value;
    if (changeChecked.value) {
      rowData.value.forEach(data => {
        data.change = true;
      });
    } else {
      rowData.value.forEach(data => {
        data.change = false;
      });
    }
  }

  if (params.column.colId === 'write') {
    writeChecked.value = !writeChecked.value;
    if (writeChecked.value) {
      rowData.value.forEach(data => {
        data.write = true;
      });
    } else {
      rowData.value.forEach(data => {
        data.write = false;
      });
    }
  }

  if (params.column.colId === 'read') {
    readChecked.value = !readChecked.value;
    if (readChecked.value) {
      rowData.value.forEach(data => {
        data.read = true;
      });
    } else {
      rowData.value.forEach(data => {
        data.read = false;
      });
    }
  }

  if (params.column.colId === 'noChange') {
    noChangeChecked.value = !noChangeChecked.value;
    if (noChangeChecked.value) {
      rowData.value.forEach(data => {
        data.noChange = true;
      });
    } else {
      rowData.value.forEach(data => {
        data.noChange = false;
      });
    }
  }
};

const onCellValueChanged = params => {
  if (params.column.colId === 'admin') {
    console.log('Changed value admin:', params.newValue);
    const allAdminChecked = rowData.value.every(item => item.admin);
    adminChecked.value = allAdminChecked;
    console.log('allAdminChecked=', allAdminChecked);
  }
  if (params.column.colId === 'delete') {
    console.log('Changed value delete:', params.newValue);
    const allDeleteChecked = rowData.value.every(item => item.delete);
    deleteChecked.value = allDeleteChecked;
    console.log('allDeleteChecked=', allDeleteChecked);
  }

  if (params.column.colId === 'change') {
    console.log('Changed value delete:', params.newValue);
    const allChangeChecked = rowData.value.every(item => item.change);
    changeChecked.value = allChangeChecked;
    console.log('allChangeChecked=', allChangeChecked);
  }
  if (params.column.colId === 'write') {
    console.log('Changed value delete:', params.newValue);
    const allWriteChecked = rowData.value.every(item => item.write);
    writeChecked.value = allWriteChecked;
    console.log('allWriteChecked=', allWriteChecked);
  }
  if (params.column.colId === 'read') {
    console.log('Changed value delete:', params.newValue);
    const allReadChecked = rowData.value.every(item => item.read);
    readChecked.value = allReadChecked;
    console.log('allReadChecked=', allReadChecked);
  }
  if (params.column.colId === 'noChange') {
    console.log('Changed value delete:', params.newValue);
    const allNoChangeChecked = rowData.value.every(item => item.noChange);
    noChangeChecked.value = allNoChangeChecked;
    console.log('allNoChangeChecked=', allNoChangeChecked);
  }
};

const attachData = () => {
  let sampleData = [];
  for (let i = 0; i < 10; i++) {
    sampleData.push({
      id: i,
      mainMenu: '지식관리',
      submenu: '지식비서',
      admin: false,
      delete: false,
      change: false,
      write: false,
      read: false,
      noChange: false,
    });
  }
  rowData.value = sampleData;
};
attachData();
</script>
