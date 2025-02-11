<template>
  <div class="pop-grid__more">
    <ul>
      <li>
        <button class="btn-pop ch-name" @click="$emit('rename')">
          <i class="icon"></i>이름 바꾸기
        </button>
      </li>
      <li>
        <button class="btn-pop ch-role" @click="$emit('chrole')">
          <i class="icon"></i>역할 바꾸기
        </button>
      </li>
      <li>
        <button class="btn-pop ch-info" @click="$emit('infoChange')">
          <i class="icon"></i>등록정보 변경
        </button>
      </li>
      <li>
        <button class="btn-pop reset-password" @click="$emit('resetPassword')">
          <i class="icon"></i>비밀번호 초기화
        </button>
      </li>
      <li>
        <button class="btn-pop attribute" @click="$emit('attribute')">
          <i class="icon"></i>속성
        </button>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
// import { onClickOutside } from '@vueuse/core';

const props = defineProps({
  tooltipId: {
    type: String,
    default: '',
  },
});
</script>

<style lang="scss" scoped></style>
