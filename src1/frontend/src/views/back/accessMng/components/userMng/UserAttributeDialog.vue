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
            <div class="row-content">강감찬 부장</div>
          </div>
          <div class="row">
            <div class="title-label">부가정보</div>
            <div class="row-content">N-2302 (kang@nissinfo.com)</div>
          </div>
          <div class="row">
            <div class="title-label">조직정보보</div>
            <div class="row-content">영업1팀 팀장</div>
          </div>
          <div class="row">
            <div class="title-label">역할</div>
            <div class="row-content">Creator</div>
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
