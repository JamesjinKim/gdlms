<template>
  <div class="content-l role">
    <div class="content-l__wrap">
      <div class="content-l__top">
        <button class="btn-m dark-blue" @click="onCodeTypeCreate">
          코드유형 생성
        </button>
        <button class="btn-m blue ml0" @click="onCodeCreate">코드 등록</button>
      </div>
      <div class="content-l__bottom" ref="scrollHistory">
        <div class="role-list">
          <div class="list-items">
            <div class="item-titles">
              <ul>
                <li class="item-row" v-for="row in data" :key="row.id">
                  <div
                    class="btn-link"
                    :class="{
                      active: selectId === row.id,
                    }"
                    @click="onCodeLink(row.id)"
                  >
                    <div class="text">
                      {{ row.title }}
                    </div>
                    <span
                      class="btn-more edit"
                      @click.stop.prevent="onCodeTypeChange(row.id)"
                    ></span>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 코드 등록정보 변경 -->
    <AppWindow v-model:view="codeInfoWindowView" width="450px">
      <CodeInfoDialog @save="onCodeInfoSave" @cancel="onCodeInfoCancel"
        >코드 등록</CodeInfoDialog
      >
    </AppWindow>

    <!-- 역할 생성 / 등록정보 변경 -->
    <AppWindow v-model:view="codeTypeCreateWindowView" width="450px">
      <CodeTypeDialog
        :selectId="editId"
        @save="onRoleCreateSave"
        @cancel="onRoleCreateCancel"
        >{{ editId === '' ? '코드유형 생성' : '코드유형 변경' }}</CodeTypeDialog
      >
    </AppWindow>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import CodeInfoDialog from '@/views/systemMng/components/code/CodeInfoDialog.vue';
import CodeTypeDialog from '@/views/systemMng/components/code/CodeTypeDialog.vue';

const data = ref([]);
const attachData = () => {
  data.value = [
    {
      id: '1',
      title: 'LLM',
      code: '1',
    },
    {
      id: '2',
      title: 'sLM',
      code: '2',
    },
    {
      id: '3',
      title: 'Vector DB',
      code: '3',
    },
    {
      id: '4',
      title: 'Embedder',
      code: '4',
    },
    {
      id: '5',
      title: 'Retriever',
      code: '5',
    },
    {
      id: '6',
      title: 'Position',
      code: '6',
    },
  ];
};

attachData();

const selectId = ref('');

//리스트 클릭
const onCodeLink = id => {
  selectId.value = id;
};

/******** 
코드유형 생성
***********/
const codeTypeCreateWindowView = ref(false);
const onCodeTypeCreate = () => {
  codeTypeCreateWindowView.value = true;
};
const onRoleCreateSave = () => {
  codeTypeCreateWindowView.value = false;
  editId.value = '';
};
const onRoleCreateCancel = () => {
  codeTypeCreateWindowView.value = false;
  editId.value = '';
};
/******** 
코드유형 변경 
***********/
const editId = ref('');
const onCodeTypeChange = id => {
  editId.value = id;
  codeTypeCreateWindowView.value = true;
};
/******** 
코드 등록
***********/
const codeInfoWindowView = ref(false);
const onCodeCreate = () => {
  codeInfoWindowView.value = true;
};
const onCodeInfoSave = () => {
  codeInfoWindowView.value = false;
  console.log('저장');
};
const onCodeInfoCancel = () => {
  codeInfoWindowView.value = false;
  console.log('취소');
};
</script>

<style lang="scss" scoped></style>
