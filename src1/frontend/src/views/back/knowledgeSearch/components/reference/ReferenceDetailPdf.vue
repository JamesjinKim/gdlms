<template>
  <div class="pdf-viewer">
    <div class="pdf-info">
      <div class="pdf-name">{{ fileName }}</div>
      <div class="pdf-pages__info">
        <AppInput
          type="number"
          v-model="currentPage"
          class="paging-num"
          @keyup.enter="movePage(currentPage)"
          @blur="movePage(currentPage)"
        /><span>/</span>{{ pages }}
      </div>
    </div>
    <div class="pdf-scroll" @scroll="pdfScrollView">
      <div
        v-for="(page, index) in pages"
        :key="page"
        class="pdf-page"
        :class="`page-${index + 1}`"
      >
        <div class="page-box">
          <VuePDF
            :pdf="pdf"
            :page="page"
            :text-layer="text_layer"
            :highlight-text="highlightText"
            :highlight-options="highlightOptions"
          />
        </div>
        <div class="page-num">{{ index + 1 }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { VuePDF, usePDF } from '@tato30/vue-pdf';
import { onMounted, ref } from 'vue';
import { useScroll } from '@vueuse/core';
import { computed } from 'vue';

const text_layer = ref(false);

const highlightText = ref('Lorem');
const highlightOptions = ref({
  completeWords: false,
  ignoreCase: true,
});

function onPassword(updatePassword, reason) {
  console.log(`Reason for callback: ${reason}`);
  updatePassword('password1234');
}

function onProgress({ loaded, total }) {
  let per = (loaded / total) * 100;
  if (per === 100) {
    setTimeout(() => {
      scrollObserver();
    }, 500);
  }
}

function onError(reason) {
  console.error(`PDF loading error: ${reason}`);
}

const currentPdf = ref('./pdf/sample.pdf');
const currentPage = ref(1);
const { pdf, pages, info } = usePDF(currentPdf, {
  onPassword,
  onProgress,
  onError,
});

const movePage = num => {
  let divTest = document.querySelector(`.page-${num}`);
  // divTest.scrollIntoView({ behavior: 'smooth' });
  divTest.scrollIntoView({});
  currentPage.value = num;
};

const pdfScrollView = () => {
  console.log('scroll');
};

defineExpose({ movePage });

const fileName = computed(() => currentPdf.value.split('/').at(-1));

const scrollObserver = () => {
  const boxes = document.querySelectorAll('.pdf-page');
  const observerCallback = (entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const siblings = Array.from(entry.target.parentElement.children);
        const index = siblings.indexOf(entry.target);
        currentPage.value = index + 1;
      }
    });
  };

  const observerOptions = {
    root: null, // 뷰포트를 루트로 사용
    threshold: 0.7, // 10%가 보이면 콜백 실행
  };

  // IntersectionObserver 인스턴스 생성
  const observer = new IntersectionObserver(observerCallback, observerOptions);

  // 모든 박스를 관찰
  boxes.forEach(box => observer.observe(box));
};
</script>
