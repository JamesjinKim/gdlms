<template>
  <div class="pop-grid__more">
    <ul>
      <li>
        <button class="btn-pop ch-name" @click="$emit('reName')">
          <i class="icon"></i>이름 바꾸기
        </button>
      </li>
      <li>
        <button class="btn-pop ch-code" @click="$emit('reCode')">
          <i class="icon"></i>코드 바꾸기
        </button>
      </li>
      <li class="more-li">
        <button class="btn-pop ch-codeorder" @click="$emit('resetPassword')">
          <i class="icon"></i>코드순서 바꾸기
        </button>
        <MoveTooltip
          @first="$emit('first')"
          @up="$emit('up')"
          @down="$emit('down')"
          @end="$emit('end')"
        />
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
import MoveTooltip from '@/views/systemMng/components/code/MoveTooltip.vue';
import { reactive, ref } from 'vue';

const props = defineProps({
  tooltipId: {
    type: String,
    default: '',
  },
});
</script>

<style lang="scss" scoped></style>
