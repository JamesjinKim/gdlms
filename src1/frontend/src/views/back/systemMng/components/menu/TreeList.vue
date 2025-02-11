<template>
  <div class="content-l role">
    <div class="content-l__wrap">
      <div class="tree-drag__wrap">
        <div class="tree-drag__top">
          <AppInput
            v-model="filterText"
            placeholder="메뉴 이름 검색"
            style="width: 100%"
          />
        </div>

        <AppTreeDrag
          v-model="treeData"
          @selectNode="onSelectNode"
          @scroll="onScroll"
          @more="onMore"
        />
        <div
          class="pop-window__role"
          ref="infoWindow"
          v-if="activeTooltipId !== ''"
          :style="{ left: tooltipXY.x, top: tooltipXY.y }"
        >
          <ul>
            <li>
              <button class="btn-pop" @click.prevent="onCreate">
                하위로 부서생성
              </button>
            </li>
            <li>
              <button class="btn-pop" @click.prevent="onRemove">
                삭제하기
              </button>
            </li>
            <li>
              <button class="btn-pop" @click.prevent="onDepartmentChange">
                등록정보 변경
              </button>
            </li>
            <li>
              <button class="btn-pop" @click.prevent="onAttributeView">
                속성
              </button>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- 삭제 확인 -->
    <AppDialog
      v-model:view="removeDepartment.view"
      :message="removeDepartment.msg"
      @confirm="confirmRemoveDepartment"
    />

    <!-- 역할 생성 / 등록정보 변경 -->
    <AppWindow v-model:view="departmentCreateWindowView" width="450px">
      <DepartmentCreateDialog
        :selectValue="editValue"
        @save="ondepartmentCreateSave"
        @cancel="onRoleCreateCancel"
        >{{
          editValue.data ? '부서 등록정보 변경' : '부서 생성'
        }}</DepartmentCreateDialog
      >
    </AppWindow>

    <!-- 속성 -->
    <AppWindow v-model:view="attributeWindowView" width="480px">
      <DepartmentAttributeDialog @close="onAttributeClose"
        >역할 속성</DepartmentAttributeDialog
      >
    </AppWindow>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { reactive } from 'vue';
import AppDialog from '@/components/ui/AppDialog.vue';
import DepartmentCreateDialog from './DepartmentCreateDialog.vue';
import DepartmentAttributeDialog from './DepartmentAttributeDialog.vue';
import AppTreeDrag from '@/components/ui/AppTreeDrag.vue';
import { onClickOutside } from '@vueuse/core';
import { randomKey } from '@/utils/utils.js';

const filterText = ref('');

const treeData = ref([]);

const attachData = () => {
  treeData.value = [
    {
      data: {
        id: '1',
        code: '1',
        icon: 'folder',
      },
      title: 'PARAMOS',
      isLeaf: false,
      isDraggable: true,
      isSelectable: true,
      children: [
        {
          data: {
            id: '2',
            code: '2',
            icon: 'file',
          },
          title: '홈',
          isLeaf: false,
          isDraggable: true,
          isSelectable: true,
        },
        {
          data: {
            id: '3',
            code: '3',
            icon: 'file',
          },
          title: '지식검색',
          isLeaf: false,
          isDraggable: true,
          isSelectable: true,
        },
        {
          data: {
            id: '4',
            code: '4',
            icon: 'folder',
          },
          title: '지식관리',
          isLeaf: false,
          isDraggable: true,
          isSelectable: true,
          children: [
            {
              data: {
                id: '4-1',
                code: '4-1',
                icon: 'file',
              },
              title: '대시보드',
              isLeaf: false,
              isDraggable: true,
              isSelectable: true,
            },
            {
              data: {
                id: '4-2',
                code: '4-2',
                icon: 'file',
              },
              title: '지식비서',
              isLeaf: false,
              isDraggable: true,
              isSelectable: true,
            },
            {
              data: {
                id: '4-2',
                code: '4-2',
                icon: 'file',
              },
              title: '스토리지',
              isLeaf: false,
              isDraggable: true,
              isSelectable: true,
            },
          ],
        },
        {
          data: {
            id: '5',
            code: '5',
            icon: 'folder',
          },
          title: '접근관리',
          isLeaf: false,
          isDraggable: true,
          isSelectable: true,
          children: [
            {
              data: {
                id: '5-1',
                code: '5-1',
                icon: 'file',
              },
              title: '사용자관리',
              isLeaf: false,
              isDraggable: true,
              isSelectable: true,
            },
            {
              data: {
                id: '5-2',
                code: '5-2',
                icon: 'file',
              },
              title: '역할관리',
              isLeaf: false,
              isDraggable: true,
              isSelectable: true,
            },
          ],
        },
      ],
    },
  ];
};

attachData();

const selectId = ref('');
const activeTooltipId = ref('');

const emit = defineEmits(['selectNode']);

const onSelectNode = value => {
  emit('selectNode', value);
};

/******** 
하위부서 생성
***********/
const departmentCreateWindowView = ref(false);
const onCreate = () => {
  selectId.value = activeTooltipId.value;
  departmentCreateWindowView.value = true;
  activeTooltipId.value = '';
};
const ondepartmentCreateSave = value => {
  const { name, code } = value;

  if (editValue.value.data) {
    //수정
    updateNodeTitleCode(treeData.value, selectId.value, name, code);
  } else {
    //신규 생성
    const addData = {
      data: {
        id: randomKey(),
        code: code,
      },
      title: name,
      isLeaf: false,
      isDraggable: true,
      isSelectable: true,
    };
    addChildToSelectedId(treeData.value, selectId.value, addData);
  }

  // Reset
  editValue.value = {};
  selectId.value = '';
  activeTooltipId.value = '';
  departmentCreateWindowView.value = false;
};
const onRoleCreateCancel = () => {
  departmentCreateWindowView.value = false;
  editValue.value = {};
  selectId.value = '';
  activeTooltipId.value = '';
};

/******** 
이동하기기
***********/
const onMove = () => {
  selectId.value = activeTooltipId.value;
  activeTooltipId.value = '';
};

/******** 
역할 등록정보 변경 
***********/
const editValue = ref({});
const onDepartmentChange = () => {
  selectId.value = activeTooltipId.value;
  editValue.value = findNodeById(treeData.value, selectId.value);
  departmentCreateWindowView.value = true;
  activeTooltipId.value = '';
};

// 신규 부서 생성
const addChildToSelectedId = (data, selectId, newData) => {
  for (let item of data) {
    if (item.data.id === selectId) {
      if (!item.children) {
        item.children = [];
      }
      item.children.push(newData);
      return true;
    }

    if (
      item.children &&
      addChildToSelectedId(item.children, selectId, newData)
    ) {
      return true;
    }
  }
  return false;
};

// 변경 부서 데이터 가져오기기
const findNodeById = (tree, id) => {
  for (const node of tree) {
    if (node.data.id === id) {
      return node;
    }
    if (node.children) {
      const found = findNodeById(node.children, id);
      if (found) {
        return found;
      }
    }
  }
  return null;
};

//변경 부서 데이터 수정
const updateNodeTitleCode = (tree, selectId, newText, newCode) => {
  for (const node of tree) {
    if (node.data.id === selectId) {
      node.title = newText;
      node.data.code = newCode;
      return true;
    }

    if (node.children) {
      const updated = updateNodeTitleCode(
        node.children,
        selectId,
        newText,
        newCode,
      );
      if (updated) {
        return true;
      }
    }
  }
  return false;
};

/******** 
삭제
***********/
// const removeId = ref('');
const removeDepartment = reactive({
  view: false,
  msg: '정말로 삭제하시겠습니까?',
});
const onRemove = () => {
  selectId.value = activeTooltipId.value;
  removeDepartment.view = true;
};
const deleteNodeById = (tree, id) => {
  return tree.filter(node => {
    if (node.children) {
      node.children = deleteNodeById(node.children, id);
    }
    return node.data.id !== id;
  });
};
const confirmRemoveDepartment = () => {
  treeData.value = deleteNodeById(treeData.value, selectId.value);
  selectId.value = '';
};

/******** 
속성
***********/
const attributeWindowView = ref(false);
const onAttributeView = () => {
  attributeWindowView.value = true;
  activeTooltipId.value = '';
};
const onAttributeClose = () => {
  attributeWindowView.value = false;
};

// //툴팁
const tooltipXY = reactive({ x: '0px', y: '0px' });
const onMore = value => {
  const { id, x, y } = value;
  activeTooltipId.value = id;
  tooltipXY.x = x;
  tooltipXY.y = y;
};

const infoWindow = ref(null);
onClickOutside(infoWindow, event => {
  activeTooltipId.value = '';
});

//스크롤 체크
const onScroll = () => {
  console.log('scroll~~~');
  if (activeTooltipId.value !== '') {
    activeTooltipId.value = '';
  }
};

const updateTreeIcons = tree => {
  tree.forEach(node => {
    if (node.children && node.children.length > 0) {
      node.data.icon = 'folder';
      updateTreeIcons(node.children);
    } else {
      node.data.icon = 'file';
    }
  });
};

watch(
  () => treeData.value,
  () => {
    console.log('tree데이터변경');
    updateTreeIcons(treeData.value);
  },
);
</script>

<style lang="scss" scoped></style>
