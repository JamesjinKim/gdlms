<template>
  <div class="window-wrap">
    <div class="window-top">
      <div class="title">
        <slot></slot>
      </div>
    </div>
    <div class="window-body">
      <div class="knowledgeSecretary-wrap attribute">
        <div class="row mb20">
          <div class="row">
            <div class="title-label">이름</div>
            <div class="row-content">GPT-4</div>
          </div>
          <div class="row">
            <div class="title-label">코드</div>
            <div class="row-content">openai_gpt4</div>
          </div>
          <div class="row">
            <div class="title-label">코드 유형</div>
            <div class="row-content">LLM</div>
          </div>
          <div class="row">
            <div class="title-label">상태</div>
            <div class="row-content">
              2023년 8월 12일 <span class="icon-text">등록됨</span>
            </div>
          </div>
        </div>

        <div class="btns">
          <button class="btn-m" @click="onClose">닫기</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, toRef } from 'vue';

const props = defineProps({
  selectname: {
    type: String,
    default: '',
  },
});

const name = toRef(props.selectname);

// 저장
const emit = defineEmits(['close']);
const onClose = () => {
  emit('close');
};
</script>

<style lang="scss" scoped></style>
