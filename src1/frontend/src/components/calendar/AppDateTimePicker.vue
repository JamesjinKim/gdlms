<template>
  <div>
    <!-- :close-on-auto-apply="false" -->
    <VueDatePicker
      v-model="dateValue"
      locale="ko"
      :format="format"
      auto-apply
      placeholder="Select Date"
      :disabled="disabled"
      :readonly="readonly"
      autocomplete="off"
      week-start="0"
      time-picker-inline
      minutes-increment="1"
      minutes-grid-increment="1"
      :is-24="is24"
      close-on-scroll
      :highlight-week-days="[0, 6]"
      :clearable="false"
    ></VueDatePicker>
  </div>
</template>

<script setup>
import VueDatePicker from '@vuepic/vue-datepicker';
import { ref, watch } from 'vue';

const props = defineProps({
  date: {
    type: Date,
    default: new Date(),
  },
  format: {
    type: String,
    default: 'yyyy-MM-dd HH:mm',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  readonly: {
    type: Boolean,
    default: false,
  },
  is24: {
    type: Boolean,
    default: true,
  },
});
const emit = defineEmits(['update:date']);

const dateValue = ref(props.date);

watch(dateValue, () => {
  emit('update:date', dateValue.value);
});
</script>

<style lang="scss" scoped></style>
