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
      :enable-time-picker="false"
      week-start="0"
      close-on-scroll
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
    default: 'yyyy-MM-dd', //'yyyy-MM-dd HH:mm'
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
