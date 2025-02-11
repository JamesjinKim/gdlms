<template>
  <div class="tree-wrap">
    <!-- <input
          type="text"
          v-model="filterText"
          placeholder="Filter nodes..."
          class="mtl-mb"
        />
        Checked: {{ checked }} -->
    <div class="tree-scroll">
      <BaseTree
        v-model="filteredTreeData"
        ref="tree"
        @check:node="onCheckNode"
        :indent="15"
      >
        <template #default="{ node, stat }">
          <OpenIcon
            v-if="stat.children.length"
            :open="stat.open"
            class="mtl-mr"
            @click="toggleOpen(stat)"
          />
          <div class="tree-node__row" @click="onNodeClick($event, node)">
            <span class="mtl-ml"
              ><i class="icon" :class="node.icon"></i>{{ node.text }}</span
            >
          </div>
        </template>
      </BaseTree>
    </div>
  </div>
</template>

<script setup>
import { BaseTree, OpenIcon } from '@he-tree/vue';
import '@he-tree/vue/style/default.css';
import '@he-tree/vue/style/material-design.css';
import { ref, computed } from 'vue';

const props = defineProps({
  treeData: {
    type: Array,
    default: () => [],
  },
});
// const treeData = ref([
//   {
//     text: 'Projects',
//     children: [
//       {
//         text: 'Frontend',
//         children: [{ text: 'Vue' }, { text: 'React' }, { text: 'Angular' }],
//       },
//       {
//         text: 'Backend',
//       },
//     ],
//   },
//   { text: 'Photos' },
//   { text: 'Videos' },
// ]);

const filterText = ref('');
const tree = ref(null);
const checked = ref([]);

const filteredTreeData = computed(() => {
  const filterData = nodes => {
    return nodes
      .map(node => {
        const isMatch = node.text
          .toLowerCase()
          .includes(filterText.value.toLowerCase());

        const filteredChildren = node.children ? filterData(node.children) : [];

        if (isMatch || filteredChildren.length > 0) {
          return {
            ...node,
            children: filteredChildren,
            open: isMatch || node.open,
          };
        }
        return null;
      })
      .filter(node => node !== null);
  };

  return filterData(props.treeData);
});

const toggleOpen = stat => {
  stat.open = !stat.open;
};

const onCheckNode = () => {
  checked.value = tree.value.getChecked().map(v => v.data.text);
};

const onNodeClick = (event, node) => {
  const target = event.currentTarget;
  console.log(node);

  const treeNodes = document.querySelectorAll('.vtlist-inner .tree-node');
  treeNodes.forEach(node => {
    node.classList.remove('active');
  });
  console.log(treeNodes);
  target.closest('.tree-node').classList.add('active');
};

const onDrop = (dragNode, dropNode, dropType) => {
  console.log(dragNode, dropNode, dropType);
};
</script>
