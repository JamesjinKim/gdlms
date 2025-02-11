<template>
  <div class="sub-router">
    <Header />
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
    <Spinner />
  </div>
</template>

<script setup>
import Header from '@/components/header/Header.vue';
import Spinner from '@/components/ui/AppSpinner.vue';
</script>
