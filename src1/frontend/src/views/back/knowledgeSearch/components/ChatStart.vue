<template>
  <div class="content-r">
    <div class="content-r__wrap">
      <div class="chat-start__wrap">
        <div class="chat-start">
          <div class="title">선택 지식비서에게 무엇이든 물어보세요.</div>
          <div class="inputs">
            <div class="inputs-t">
              <!-- :reduce="option => option.value" -->
              <v-select
                :options="knowledgeOptions"
                label="label"
                index="value"
                v-model="knowledge"
                :reduce="option => option.value"
                :searchable="false"
                :clearable="false"
                style="width: 100%"
                class="chat-start__select"
              />
            </div>
            <div class="inputs-b">
              <div class="input-question">
                <input
                  type="text"
                  v-model="questionData"
                  placeholder="궁금한 점을 물어보세요."
                  @keyup.enter="onSend"
                />
                <button
                  class="btn-send"
                  :disabled="questionData === ''"
                  @click="onSend"
                ></button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { reactive } from 'vue';

const knowledgeOptions = reactive([
  { label: '지식비서', value: 0 },
  { label: '인사 총무 업무 비서', value: 1 },
  { label: '회사생활 가이드', value: 2 },
  { label: '정보 보안 업무 비서', value: 3 },
  { label: '홍보 및 마케팅 업무 비서 ', value: 4 },
]);
const knowledge = ref(0);

const questionData = ref('');

const emit = defineEmits(['question']);
const onSend = () => {
  if (questionData.value === '') return;
  emit('question', { type: knowledge.value, msg: questionData.value });
};
</script>

<style lang="scss" scoped></style>
