<template>
  <div class="window-wrap">
    <div class="window-top">
      <div class="title">
        <slot></slot>
      </div>
    </div>
    <div class="window-body">
      <div class="knowledgeSecretary-wrap">
        <div class="row mb10">
          <div class="row flex mb10">
            <div class="title-label required">이름</div>
            <div class="row-content">
              <AppInput
                type="text"
                placeholder="역할 이름을 입력해 주세요."
                v-model="name"
                style="width: 100%"
              />
            </div>
          </div>
          <div class="row flex">
            <div class="title-label">설명</div>
            <div class="row-content">
              <AppInput
                type="text"
                placeholder="역할 설명을 입력해 주세요."
                v-model="explain"
                style="width: 100%"
              />
            </div>
          </div>
        </div>

        <div class="btns">
          <button class="btn-m blue" @click="onSave">저장</button>
          <button class="btn-m" @click="onCancel">취소</button>
        </div>
      </div>
    </div>
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
const explain = ref('');

// 저장
const emit = defineEmits(['cancel']);
const onSave = () => {
  console.log('저장 실행');
  emit('cancel');
};
const onCancel = () => {
  emit('cancel');
};
</script>
