<template>
  <div class="title-row">
    <div class="title-text">
      <ul>
        <li v-for="(item, index) in titles" :key="index">
          {{ item }}
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const titles = ref([]);

const checkTitle = () => {
  let metaTitles = [];
  route.matched.map(match => {
    metaTitles.push(match.meta.title);
  });
  const sameCheck = metaTitles
    .slice(0, 2)
    .every((val, _, arr) => val === arr[0]);
  return sameCheck ? [metaTitles[0]] : metaTitles;
};

titles.value = checkTitle();
</script>
