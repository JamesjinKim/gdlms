<template>
  <div class="wrap-404">
    <div class="error-box">
      <div class="icon"></div>
      <div class="error-title"><strong>404</strong> Not Found</div>
      <div class="text-muted">요청한 페이지를 찾을 수 없습니다!</div>
      <div class="mt-4">
        <button class="btn-m black" @click="onHistoryBack">돌아가기</button>
      </div>
    </div>
  </div>
</template>

<script setup>
const onHistoryBack = () => {
  history.back();
};
</script>

<style lang="scss" scoped></style>
