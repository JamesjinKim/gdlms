div
<template>
  <div class="window-wrap">
    <div class="window-top">
      <div class="title">
        <slot></slot>
      </div>
    </div>
    <div class="window-body">
      <div class="share-wrap">
        <div class="share-info">
          공유 링크에는 사용자의 이름이나 개인정보가 포함되지 않습니다.<br />
          링크 정보를 알고 있는 사용자라면 누구나 공유 링크에서 대화 메시지를 볼
          수 있습니다.
        </div>
        <div class="share-input">
          <AppInput v-model="copyUrl" />
          <button
            class="btn-link"
            :disabled="btnName === '복사됨'"
            @click="onLink"
          >
            {{ btnName }}
          </button>
        </div>
        <div class="info-link">
          이 채팅의 이전 버전이 이미 공유되었습니다.
          <span class="link-text">설정</span>에서 이전에 공유된 채팅을
          관리하세요.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({
  selectId: {
    type: String,
    default: '',
  },
});

const btnName = ref('링크 업데이트');

const copyUrl = ref('');
copyUrl.value = 'https://test.com/share/674f325d-7a58-800d-8658-34899b2409cd';

const onLink = () => {
  btnName.value = '복사됨';
  const textToCopy = copyUrl.value.trim();
  navigator.clipboard.writeText(textToCopy);

  setTimeout(() => {
    btnName.value = '링크 복사';
  }, 1000);
};
</script>

<style lang="scss" scoped></style>
