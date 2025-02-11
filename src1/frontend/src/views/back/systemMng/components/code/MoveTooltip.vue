<template>
  <div class="pop-grid__more">
    <ul>
      <li>
        <button class="btn-pop ch-name" @click="$emit('first')">
          처음으로 이동하기
        </button>
      </li>
      <li>
        <button class="btn-pop ch-role" @click="$emit('up')">
          위로 이동하기
        </button>
      </li>
      <li>
        <button class="btn-pop ch-info" @click="$emit('down')">
          아래로 이동하기
        </button>
      </li>
      <li>
        <button class="btn-pop reset-password" @click="$emit('end')">
          끝으로 이동하기
        </button>
      </li>
    </ul>
  </div>
</template>

<script setup></script>

<style lang="scss" scoped></style>
