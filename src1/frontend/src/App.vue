<template>
  <div class="wrap">
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
    <Alert />
  </div>
</template>

<script setup="setup">
import { defineAsyncComponent } from 'vue';
const Alert = defineAsyncComponent(() =>
  import('@/components/ui/AppAlert.vue'),
);
</script>

<style lang="scss"></style>
