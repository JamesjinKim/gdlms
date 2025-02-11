<template>
  <div class="window-wrap">
    <div class="window-top">
      <div class="title">
        <slot></slot>
      </div>
    </div>
    <div class="window-body">
      <div class="knowledgeSecretary-wrap code-info">
        <div class="row mb10">
          <div class="row flex">
            <div class="title-label required">이름</div>
            <div class="row-content">
              <AppInput
                type="text"
                placeholder="이름을 입력해 주세요."
                v-model="name"
                style="width: 100%"
              />
            </div>
          </div>
        </div>
        <div class="row mb20">
          <div class="row flex">
            <div class="title-label">코드</div>
            <div class="row-content">
              <AppInput
                type="text"
                placeholder="코드를 입력해 주세요."
                v-model="code"
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
  selectCode: {
    type: String,
    default: '',
  },
});

const name = ref('');
const code = ref('');

// 저장
const emit = defineEmits(['save', 'cancel']);
const onSave = () => {
  emit('save', code.value);
};
const onCancel = () => {
  emit('cancel');
};
</script>

<style lang="scss" scoped></style>
