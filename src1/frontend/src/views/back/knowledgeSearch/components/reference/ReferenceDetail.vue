<template>
  <div class="reference-view">
    <span class="btn-reference__close" @click="onClose"
      ><i class="icon"></i
    ></span>
    <div class="reference-l">
      <ReferenceDetailPdf ref="pdfView" />
    </div>
    <div class="reference-r">
      <ReferenceDetailChat @movePage="onMovePage" />
    </div>
  </div>
</template>

<script setup>
import ReferenceDetailPdf from '@/views/knowledgeSearch/components/reference/ReferenceDetailPdf.vue';
import ReferenceDetailChat from '@/views/knowledgeSearch/components/reference/ReferenceDetailChat.vue';
import { ref } from 'vue';

const emit = defineEmits(['close']);

const onClose = () => {
  emit('close');
};

const pdfView = ref(null);
const onMovePage = num => {
  pdfView.value.movePage(num);
};
</script>
