<template>
  <nav>
    <ul class="depth1">
      <li v-for="navi in naviData" :key="navi.link" class="lv1">
        <router-link
          :to="`${navi.path}`"
          class="btn-route"
          :class="{ useSub: navi.lv2.length > 1 }"
          >{{ navi.title }}</router-link
        >
        <ul class="depth2" v-if="navi.lv2.length > 1">
          <li v-for="lv2 in navi.lv2" :key="lv2.link">
            <router-link :to="`${lv2.link}`" class="btn-route">{{
              lv2.title
            }}</router-link>
          </li>
        </ul>
      </li>
    </ul>
  </nav>
</template>

<script setup>
import { isReactive, isRef, onMounted, reactive, ref } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();

const props = defineProps({
  navis: {
    type: Array,
    default: () => [],
  },
});

const naviData = reactive(props.navis);

onMounted(() => {
  // console.log('[route.matched] ', route, route.path, route.fullPath);
});
</script>

<style lang="scss" scoped></style>
