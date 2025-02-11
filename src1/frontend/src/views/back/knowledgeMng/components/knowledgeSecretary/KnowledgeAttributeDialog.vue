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
            <div class="title-label">연결된 스토리지</div>
            <div class="row-content">
              회사생활 지식 (2024년 8월 17일 오전 10:29)
            </div>
          </div>
          <div class="row">
            <div class="title-label">Assistant Options</div>
            <div class="row-content non-bg">
              <ul class="assistant-options">
                <li>
                  <span class="label">Model</span>
                  <span class="value">GTP-4o</span>
                </li>
                <li>
                  <span class="label">Temperature</span>
                  <span class="value">0.6</span>
                </li>
                <li>
                  <span class="label">Maximum Tokens</span>
                  <span class="value">256</span>
                </li>
                <li>
                  <span class="label">Top P</span>
                  <span class="value">1</span>
                </li>
                <li>
                  <span class="label">Frequency Penalty</span>
                  <span class="value">0.5</span>
                </li>
              </ul>
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
