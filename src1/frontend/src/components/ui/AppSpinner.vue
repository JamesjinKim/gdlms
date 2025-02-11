<template>
  <transition name="fade-loading" mode="out-in">
    <div class="pop-preloading" v-if="spinnerStatus" ref="preloading">
      <span class="preloader">Preloading</span>
    </div>
  </transition>
</template>

<script setup>
import { useSpinner } from '@/composables/spinner';
const { spinnerStatus } = useSpinner();
</script>

<style></style>
