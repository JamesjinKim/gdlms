<template>
  <div>
    <VueDatePicker
      v-model="dateValue"
      locale="ko"
      :format="format"
      year-picker
      auto-apply
      placeholder="Select Year"
      :disabled="disabled"
      :readonly="readonly"
      autocomplete="off"
      week-start="0"
      close-on-scroll
      :clearable="false"
    ></VueDatePicker>
    <div>{{ date }}</div>
  </div>
</template>

<script setup>
import VueDatePicker from '@vuepic/vue-datepicker';
import { ref, watch } from 'vue';

const props = defineProps({
  date: {
    type: Number,
    default: new Date().getFullYear(),
  },
  format: {
    type: String,
    default: 'yyyy', //'yyyy-MM-dd HH:mm'
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  readonly: {
    type: Boolean,
    default: false,
  },
});
const emit = defineEmits(['update:date']);

const dateValue = ref(props.date);

watch(dateValue, () => {
  emit('update:date', dateValue.value);
});
</script>

<style lang="scss" scoped></style>
