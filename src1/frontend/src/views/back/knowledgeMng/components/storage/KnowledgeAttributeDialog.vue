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
            <div class="row-content">회사생활 가이드</div>
          </div>
          <div class="row">
            <div class="title-label">생성자</div>
            <div class="row-content">닛시인포 (2024년 8월 17일 오전 10:29)</div>
          </div>
          <div class="row">
            <div class="title-label">마지막으로 업데이트한 사용자</div>
            <div class="row-content">닛시인포 (2024년 8월 17일 오전 10:29)</div>
          </div>
          <div class="row">
            <div class="title-label">스토리지 크기기</div>
            <div class="row-content">120 files 60GB</div>
          </div>
          <div class="row mb5">
            <div class="title-label">Assistant Options</div>
            <div class="row-content non-bg">
              <ul class="assistant-options">
                <li>
                  <span class="label">Chunk size(tokens)</span>
                  <span class="value">1024</span>
                </li>
                <li>
                  <span class="label">Chunk overlap(tokents) </span>
                  <span class="value">512</span>
                </li>
              </ul>
            </div>
          </div>
          <div class="row">
            <div class="check-area">
              <span class="checkbox-wrap">
                <input
                  type="checkbox"
                  id="checkText"
                  v-model="data.checkText"
                />
                <label for="checkText">본문요약</label>
              </span>
              <span class="checkbox-wrap ml20">
                <input
                  type="checkbox"
                  id="checkImage"
                  v-model="data.checkImage"
                />
                <label for="checkImage">이미지요약</label>
              </span>
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

const data = reactive({
  checkText: false,
  checkImage: false,
});

// 저장
const emit = defineEmits(['close']);
const onClose = () => {
  emit('close');
};
</script>

<style lang="scss" scoped></style>
