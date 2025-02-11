<template>
  <transition name="fade-view">
    <div class="dialog-wrapper window" v-if="view">
      <div class="dialog-box" :style="{ width: width }">
        <span class="btn-close" @click="onClose">닫기</span>
        <div class="dialog-body" :style="{ height: height }">
          <slot></slot>
        </div>
        <div class="dialog-footer" v-if="useFooter">
          <slot name="footer"></slot>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
defineProps({
  view: {
    type: Boolean,
    default: false,
    required: true,
  },
  height: {
    type: String,
    default: 'auto',
  },
  width: {
    type: String,
    default: '400px',
  },
  useFooter: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['update:view']);
const onClose = () => {
  emit('update:view', false);
};
</script>
