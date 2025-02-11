<template>
  <div class="window-wrap">
    <div class="window-top">
      <div class="title">
        <slot></slot>
      </div>
    </div>
    <div class="window-body">
      <div class="knowledgeSecretary-wrap">
        <div class="row mb10">
          <div class="row flex mb10">
            <div class="title-label required">이름</div>
            <div class="row-content">
              <AppInput
                type="text"
                placeholder="부서 이름을 입력해 주세요."
                v-model="name"
                style="width: 100%"
              />
            </div>
          </div>
          <div class="row flex">
            <div class="title-label">코드</div>
            <div class="row-content">
              <AppInput
                type="text"
                placeholder="부서 코드를 입력해 주세요."
                v-model="code"
                style="width: 100%"
              />
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
import { ref, reactive, toRef } from 'vue';

const props = defineProps({
  selectValue: {
    type: Object,
    default: () => {},
  },
});

const name = ref('');
const code = ref('');

const editvalue = ref({ ...props.selectValue });
if (editvalue.value.data) {
  name.value = editvalue.value.title;
  code.value = editvalue.value.data.code;
}

// 저장
const emit = defineEmits(['cancel', 'save']);
const onSave = () => {
  emit('save', { name: name.value, code: code.value });
};
const onCancel = () => {
  emit('cancel');
};
</script>
