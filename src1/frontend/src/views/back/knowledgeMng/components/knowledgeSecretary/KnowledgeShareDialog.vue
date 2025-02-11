<template>
  <div class="window-wrap">
    <div class="window-top">
      <div class="title">
        <slot></slot>
      </div>
    </div>
    <div class="window-body">
      <div class="knowledgeSecretary-wrap">
        <div class="row mb20">
          <div class="row mb20">
            <div class="row-content">
              <AppInput
                type="text"
                placeholder="사용자 또는 부서 이름으로 추가"
                v-model="name"
                style="width: 100%"
              />
            </div>
          </div>
          <div class="row">
            <div class="title-label mb5">액세스 권한이 있는 사용자</div>
            <div class="row-content share">
              <ul class="share-options">
                <li v-for="item in authorityData" :key="item.id">
                  <span class="label">{{ item.label }}</span>
                  <div class="share-r">
                    <span class="info">{{ item.auth }}</span>
                    <span
                      class="btn-remove"
                      @click="onRemoveRow(item.id)"
                      title="삭제"
                      ><i class="icon"></i
                    ></span>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <div class="btns">
          <button class="btn-m blue" @click="onSave">저장</button>
          <button class="btn-m" @click="onCancel">취소</button>
        </div>
      </div>
    </div>
    <!-- 삭제 확인 -->
    <AppDialog
      v-model:view="removeRow.view"
      :message="removeRow.msg"
      @confirm="cellRemoveConfirm"
    />
  </div>
</template>

<script setup>
import { ref, reactive, toRef } from 'vue';

const props = defineProps({
  selectId: {
    type: String,
    default: '',
  },
});

const name = ref('');
const authorityData = ref([]);
const attachData = () => {
  const testData = [];
  for (let i = 0; i < 20; i++) {
    testData.push({ id: i, label: '영업팀' + (i + 1), auth: '접근자' });
  }
  authorityData.value = testData;
};
attachData();

// 저장
const emit = defineEmits(['save', 'cancel']);
const onSave = () => {
  emit('save');
};
const onCancel = () => {
  emit('cancel');
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
};
// callDetailInfo 메소드 정의
const cellRemoveConfirm = () => {
  const updatedData = authorityData.value.filter(
    item => item.id !== selectedId.value,
  );
  authorityData.value = updatedData;
  selectedId.value = '';
};
</script>

<style lang="scss" scoped></style>
