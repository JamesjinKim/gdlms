<template>
  <div class="tabs">
    <div class="tabs-list">
      <div class="tab-item" v-for="(tab, index) in tabList" :key="index">
        <input
          :id="`app${index}`"
          type="radio"
          :name="`app-tab`"
          :value="index + 1"
          :checked="index + 1 === modelValue ? true : false"
          @input="$emit('update:modelValue', Number($event.target.value))"
        />
        <label class="tab-label" :for="`app${index}`" v-text="tab" />
      </div>
    </div>

    <template v-for="(tab, index) in tabList">
      <template v-if="mode === 'if'">
        <div
          class="tab-content"
          :key="index"
          v-if="index + 1 === modelValue ? true : false"
        >
          <slot :name="`tabPanel-${index + 1}`" />
        </div>
      </template>
      <template v-else>
        <div
          class="tab-content"
          :key="index"
          v-show="index + 1 === modelValue ? true : false"
        >
          <slot :name="`tabPanel-${index + 1}`" />
        </div>
      </template>
    </template>
  </div>
</template>

<script setup>
defineProps({
  tabList: {
    type: Array,
    required: true,
  },
  modelValue: {
    type: Number,
    default: 1,
  },
  mode: {
    type: String,
    default: 'if',
  },
});

defineEmits(['update:modelValue']);
</script>
