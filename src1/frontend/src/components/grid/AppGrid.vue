<template>
  <ag-grid-vue
    class="ag-theme-balham"
    style="height: 100%"
    :gridOptions="gridOptions"
    :columnDefs="columnDefs"
    :rowData="rowData"
    :defaultColDef="defaultColDef"
    :rowSelection="rowSelection"
    :suppressRowClickSelection="rowSelectDisabled"
    animateRows="true"
    :overlayLoadingTemplate="overlayLoadingTemplate"
    @cell-clicked="cellWasClicked"
    @rowClicked="onRowClicked"
    @selection-changed="onSelectionChanged"
    @grid-ready="onGridReady"
    :rowDragManaged="true"
  >
  </ag-grid-vue>
</template>

<script setup>
import { ModuleRegistry } from 'ag-grid-community';
import { ClientSideRowModelModule } from 'ag-grid-community';
import { AgGridVue } from 'ag-grid-vue3';
import { ref } from 'vue';

ModuleRegistry.registerModules([ClientSideRowModelModule]);

const props = defineProps({
  columnDefs: {
    type: Array,
    required: true,
    default: () => [],
  },
  rowData: {
    type: Array,
    required: true,
    default: () => [],
  },
  domLayout: {
    type: String,
    default: 'normal',
  },
  rowSelection: {
    type: String,
    default: 'single',
  },
  rowSelectDisabled: {
    type: Boolean,
    default: false,
  },
});

const gridApi = ref(null);

const emit = defineEmits(['bodyScroll', 'rowClicked']);

const onGridReady = params => {
  gridApi.value = params.api;
  // setTimeout(sizeToFit, 100);
};

const defaultColDef = {
  suppressMovable: true,
  sortable: false,
  filter: false,
  // flex: 1,
  resizable: true,
};

const gridOptions = {
  pagination: false,
  paginationAutoPageSize: false,
  domLayout: props.domLayout,
  headerHeight: 41,
  rowHeight: 38,
  localeText: { noRowsToShow: '데이터가 없습니다.' },
  onBodyScroll: event => {
    emit('bodyScroll', event);
  },
};

const overlayLoadingTemplate =
  '<span class="ag-overlay-loading-center"><div class="loader">Loading...</div></span>';

// Row선택 비활성화
const deselectRows = event => {
  gridApi.value.deselectAll();
};

// Cell 클릭
const cellWasClicked = event => {
  // console.log('cell was clicked', event);
};

// Row 클릭(항상 실행)
const onRowClicked = () => {
  const selectedRows = gridApi.value.getSelectedRows();
  console.log('[onRowClicked] = ', selectedRows[0]);
  // this.$emit('rowClicked', selectedRows[0]);
};

// Row 클릭(선택 Row가 변경시에만 실행)
const onSelectionChanged = () => {
  var selectedRows = gridApi.value.getSelectedRows();
  // console.log('[onSelectionChanged] = ', selectedRows[0]);
  // this.$emit('selectionChanged', selectedRows[0]);
};

/* const sizeToFit = () => {
  console.log('gridApi.value=', gridApi.value);
  gridApi.value.sizeColumnsToFit();
  console.log('resize~~~');
}; */

defineExpose({ gridApi });
</script>

<style lang="scss" scoped></style>
