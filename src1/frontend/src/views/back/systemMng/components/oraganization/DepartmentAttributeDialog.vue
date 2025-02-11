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
            <div class="row-content">{{ data.name }}</div>
          </div>
          <div class="row">
            <div class="title-label">코드</div>
            <div class="row-content">{{ data.code }}</div>
          </div>
          <div class="row">
            <div class="title-label">조직코드 유형</div>
            <div class="row-content">{{ data.groupCode }}</div>
          </div>
          <div class="row">
            <div class="title-label">상위부서</div>
            <div class="row-content">{{ data.upperDepartment }}</div>
          </div>
          <div class="row">
            <div class="title-label">상태</div>
            <div class="row-content">
              {{ data.situation.date }}
              <span class="icon-text">{{ data.situation.state }}</span>
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
  name: '마케팅부',
  code: 'dept_01201',
  groupCode: '부서코드',
  upperDepartment: '부서코드 > 마케팅부',
  situation: { date: '2023년 8월10일', state: '등록됨' },
});

// 저장
const emit = defineEmits(['close']);
const onClose = () => {
  emit('close');
};
</script>
