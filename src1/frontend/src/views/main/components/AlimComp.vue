<template>
  <div class="alim-warp">
    <div class="content-box">
      <div class="alim-top">
        <span class="title">발생 알림</span>
      </div>
      <div class="alim-body">
        <div class="alim-list">
          <ul class="list">
            <li v-for="item in alimData" :key="item.id">
              <div class="alim-title">{{ item.title }}</div>
              <div class="alim-date">{{ item.date }}</div>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { toRefs } from 'vue';

const props = defineProps({
  data: {
    type: Object,
    default: () => ({}),
  },
});

const { data: alimData } = toRefs(props);
</script>
