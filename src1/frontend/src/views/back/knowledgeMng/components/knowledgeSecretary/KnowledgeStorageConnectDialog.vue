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
          <div class="row flex">
            <div class="title-label" style="flex: 0 0 115px">스토리지 선택</div>
            <div class="row-content">
              <v-select
                :options="knowledgeOptions"
                label="label"
                index="value"
                :reduce="option => option.value"
                v-model="knowledge"
                :searchable="false"
                :clearable="false"
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

const knowledgeOptions = reactive([
  { label: '지식비서', value: 0 },
  { label: '인사 총무 업무 비서', value: 1 },
  { label: '회사생활 가이드', value: 2 },
  { label: '정보 보안 업무 비서', value: 3 },
  { label: '홍보 및 마케팅 업무 비서 ', value: 4 },
]);

const knowledge = ref(0);

// 저장
const emit = defineEmits(['save', 'cancel']);
const onSave = () => {
  emit('save');
};
const onCancel = () => {
  emit('cancel');
};
</script>

<style lang="scss" scoped></style>
