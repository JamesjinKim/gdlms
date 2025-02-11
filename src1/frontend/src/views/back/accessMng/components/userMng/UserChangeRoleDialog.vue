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
          <div class="row mb10 flex">
            <div class="title-label required">역할</div>
            <v-select
              :options="roleOptions"
              label="label"
              index="value"
              :reduce="option => option.value"
              v-model="role"
              :searchable="false"
              :clearable="false"
              style="width: 100%"
            />
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

const props = defineProps({
  selectId: {
    type: String,
    default: '',
  },
});

const roleOptions = reactive([
  { label: 'Administrator', value: 0 },
  { label: 'Creator', value: 1 },
  { label: 'Updater', value: 2 },
  { label: 'Eraser', value: 3 },
]);
const role = ref(0);

// 저장
const emit = defineEmits(['save', 'cancel']);
const onSave = () => {
  emit('save');
};
const onCancel = () => {
  emit('cancel');
};
</script>

<style lang="scss" scoped></style>
