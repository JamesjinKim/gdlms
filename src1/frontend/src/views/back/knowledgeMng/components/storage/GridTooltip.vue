<template>
  <div class="pop-grid__more">
    <ul>
      <li>
        <button class="btn-pop ch-name" @click="$emit('rename')">
          <i class="icon"></i>이름 바꾸기
        </button>
      </li>
      <li>
        <button class="btn-pop remove" @click="$emit('remove')">
          <i class="icon"></i>삭제하기
        </button>
      </li>
      <li>
        <button class="btn-pop copybook" @click="$emit('copybook')">
          <i class="icon"></i>사본 만들기
        </button>
      </li>
      <li>
        <button class="btn-pop ch-info" @click="$emit('infoChange')">
          <i class="icon"></i>등록정보 변경
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
