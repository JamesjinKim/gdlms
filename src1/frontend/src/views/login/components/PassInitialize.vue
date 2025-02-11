<template>
  <div class="window-wrap">
    <div class="window-top">
      <div class="title">
        <slot></slot>
      </div>
    </div>
    <div class="window-body">
      <div class="pass-initial__wrap">
        <div class="info-box">
          이메일 주소를 관리자에게 전송하면 비밀번호를 재설정할 수 있습니다.
        </div>
        <div class="row">
          <div class="title-label">사번 또는 이메일</div>
          <AppInput
            type="text"
            placeholder="사번 또는 이메일을 입력하세요."
            class="input-email"
            v-model="inputEmail"
          />
        </div>
        <div class="btns">
          <button class="btn-m" @click="onSend">전송</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
const inputEmail = ref('');

const emit = defineEmits(['send']);
const onSend = () => {
  emit('send');
};
</script>

<style lang="scss" scoped></style>
