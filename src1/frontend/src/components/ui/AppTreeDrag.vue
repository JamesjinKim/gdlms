<template>
  <div class="tree-drag__bottom">
    <div class="tree-scroll" v-scroll="onScroll">
      <sl-vue-tree-next
        :modelValue="modelValue"
        :activatable="false"
        @update:modelValue="updateTreeData"
      >
        <template #toggle="{ node }">
          <span v-if="!node.isLeaf && node.children.length > 0">
            <i v-if="node.isExpanded" class="icon-down"></i>
            <i v-if="!node.isExpanded" class="icon-right"></i>
          </span>
          <span class="btn-blank" v-else></span>
          <!-- <span v-if="!node.isLeaf" v-show="node.children.length > 0">
              <i v-if="node.isExpanded" class="icon-down"></i>
              <i v-if="!node.isExpanded" class="icon-right"></i>
            </span> -->
        </template>
        <template #title="{ node }">
          <div
            class="node-row"
            :class="{ inActive: !node.isSelectable }"
            @click="$event => onNodeclick($event, node)"
          >
            <span class="item-icon">
              <i
                :class="[
                  `icon-${node.data.icon}`,
                  { open: node.children.length > 0 && node.isExpanded },
                ]"
              ></i>
              <!-- <i class="fa-solid fa-file" v-if="node.isLeaf"></i>
              <i class="fa-solid fa-folder" v-if="!node.isLeaf"></i> -->
            </span>

            {{ node.title }}
          </div>
        </template>

        <template #sidebar="{ node }">
          <span
            class="more-icon"
            :class="{ inActive: !node.isSelectable }"
            @click.stop.prevent="$event => onMore($event, node)"
            v-if="useMore"
          >
          </span>
        </template>
      </sl-vue-tree-next>
    </div>
  </div>
</template>

<script setup>
import { SlVueTreeNext } from 'sl-vue-tree-next';
import { vScroll } from '@vueuse/components';

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => [],
  },
  useMore: {
    type: Boolean,
    default: true,
  },
});

// const { treeData } = toRefs(props);

const onNodeclick = (event, node) => {
  if (!node.isSelectable) return;
  console.log('[onNodeclick]', event, node);
  const treeNodes = document.querySelectorAll('.sl-vue-tree-next-node-item');
  treeNodes.forEach(node => {
    node.classList.remove('active');
  });
  const target = event.currentTarget;
  target.closest('.sl-vue-tree-next-node-item').classList.add('active');
  emit('selectNode', node);
};

//툴팁
const onMore = (event, node) => {
  let tooltip = { id: node.data.id, x: '0px', y: '0px' };
  const tooltipHeight = 168;
  const rect = event.target.getBoundingClientRect();
  tooltip.x = `${rect.x + 35}px`;
  if (rect.bottom + tooltipHeight > window.innerHeight) {
    tooltip.y = `${rect.y - 100}px`;
  } else {
    tooltip.y = `${rect.y}px`;
  }
  console.log(tooltip);
  emit('more', tooltip);
};

//스크롤 체크
const onScroll = () => {
  emit('scroll');
};

const updateTreeData = newTreeData => {
  emit('update:modelValue', newTreeData); // 부모로 변경된 값 전달
};

const emit = defineEmits(['update:modelValue', 'selectNode', 'scroll', 'more']);
</script>

<style lang="scss" scoped></style>
