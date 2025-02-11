<template>
  <div class="reference-wrap">
    <div class="reference-scroll">
      <div class="reference-list">
        <div
          class="item-thum"
          v-for="item in referenceData"
          :key="item.id"
          @click="onSelect(item.id)"
        >
          <img :src="item.imgUrl" />
        </div>
      </div>
    </div>
    <transition name="reference-detail" mode="out-in">
      <Teleport to=".content-area">
        <ReferenceDetail v-if="referenceWindowView" @close="onCloseReference" />
      </Teleport>
    </transition>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import ReferenceDetail from '@/views/knowledgeSearch/components/reference/ReferenceDetail.vue';

const props = defineProps({
  referenceId: {
    type: String,
    default: '',
  },
});

const referenceData = ref([]);
const attachData = () => {
  let sampleData = [];
  for (let i = 0; i < Math.floor(Math.random() * 10) + 1; i++) {
    sampleData.push({ id: i, imgUrl: './images/sample_thum.png' });
  }
  referenceData.value = sampleData;
};

attachData();

const referenceWindowView = ref(false);
const onCloseReference = () => {
  referenceWindowView.value = false;
};

const onSelect = id => {
  console.log(id);
  referenceWindowView.value = true;
};

watch(
  () => props.referenceId,
  () => {
    console.log('Reference~~~');
    attachData();
  },
);
</script>
