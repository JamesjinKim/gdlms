<template>
  <div class="window-wrap">
    <div class="window-top">
      <div class="title">
        <slot></slot>
      </div>
    </div>
    <div class="window-body">
      <div class="pass-initial__wrap">
        <div class="row">
          <div class="title-label">사번 또는 이메일</div>
          <AppInput type="text" />
        </div>
        <div class="row mt15">
          <div class="title-label">비밀번호</div>
          <AppInput type="text" />
        </div>
        <div class="row mt15">
          <div class="title-label">비밀번호 확인</div>
          <AppInput type="text" />
        </div>
        <div class="pass-info">
          8자 이상 대문자, 소문자, 숫자, 특수문자 중 3가지 이상을 사용해 주세요.
        </div>
        <div class="btns">
          <button class="btn-m" @click="onSend">전송</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const emit = defineEmits(['send']);
const onSend = () => {
  emit('send');
};
</script>

<style lang="scss" scoped></style>
