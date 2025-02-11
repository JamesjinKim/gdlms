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
            <!-- <VTooltip>
              <a>Sponsor me</a>

              <template #popper>
                <strong>Help me fund my Open Source work!</strong>
              </template>
            </VTooltip> -->
            <div class="title-label">설명</div>
            <div class="row-content">{{ data.explain }}</div>
          </div>
          <div class="row">
            <div class="title-label">접근 사용자</div>
            <div class="row-content non-bg non-br">
              <div class="access-user__list">
                <VTooltip v-for="(user, index) in data.users" :key="index">
                  <span class="access-name">{{ user.name }}</span>
                  <template #popper>
                    <div class="tooltip-userinfo__list">
                      <div class="list-row">
                        {{ user.name }} {{ user.rank }}
                      </div>
                      <div class="list-row">{{ user.group }}</div>
                      <div class="list-row">{{ user.cleanup }}</div>
                      <div class="list-row">{{ user.email }}</div>
                    </div>
                  </template>
                </VTooltip>
              </div>
            </div>
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
  name: '홍길동',
  explain: '메뉴 접근 관리자 역할',
  users: [
    {
      name: '김유신',
      rank: '부장',
      group: '영업1팀 팀장',
      cleanup: 'NI-2302',
      email: 'kang@nissinfo.com',
    },
    {
      name: '강감찬',
      rank: '과장',
      group: '영업2팀 과장장',
      cleanup: 'NI-1234',
      email: 'mng@nissinfo.com',
    },
  ],
  situation: { date: '2023년 8월10일', state: '등록됨' },
});

// 저장
const emit = defineEmits(['close']);
const onClose = () => {
  emit('close');
};
</script>
