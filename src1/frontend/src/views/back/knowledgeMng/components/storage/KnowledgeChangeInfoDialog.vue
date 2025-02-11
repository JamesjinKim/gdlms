<template>
  <div class="window-wrap">
    <div class="window-top">
      <div class="title">
        <slot></slot>
      </div>
    </div>
    <div class="window-body">
      <div class="knowledgeSecretary-wrap">
        <div class="row mb20">
          <div class="row flex">
            <div class="title-label">이름</div>
            <div class="row-content">
              <AppInput
                type="text"
                placeholder="사용자에게 친숙한 이름을 입력해 주세요."
                v-model="data.name"
                style="width: 100%"
                @keyup.enter="keywordSend"
              />
            </div>
          </div>
        </div>
        <div class="row answer-type">
          <div class="row storage">
            <div>
              <div class="row">
                <div class="row-title">
                  <div class="title-label">주요 키워드</div>
                </div>
                <div class="row-content">
                  <div class="keyword-list__wrap">
                    <div class="list-scroll">
                      <div class="keyword-btns">
                        <div
                          class="btn-key"
                          v-for="(item, index) in data.keywords"
                          :key="item.id"
                        >
                          {{ item.label
                          }}<span
                            class="btn-remove"
                            @click="onRemoveKeyword(index)"
                            ><i class="icon"></i
                          ></span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="btns">
          <button class="btn-m blue" @click="onSave">저장</button>
          <button class="btn-m" @click="onCancel">취소</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { randomKey } from '@/utils/utils.js';

const data = reactive({
  name: '',
  keywords: [],
});

const onRemoveKeyword = index => {
  data.keywords.splice(index, 1);
};

const keywordSend = () => {
  if (data.name === '') return;
  const answerText = {
    id: randomKey(),
    label: data.name,
  };
  data.keywords.push(answerText);

  data.name = '';
};

// 저장
const emit = defineEmits(['save', 'cancel']);
const onSave = () => {
  emit('save');
};
const onCancel = () => {
  emit('cancel');
};

const fileuploadList = ref(null);
</script>

<style lang="scss" scoped></style>
