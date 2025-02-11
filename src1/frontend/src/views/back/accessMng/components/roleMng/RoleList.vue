<template>
  <div class="content-l role">
    <div class="content-l__wrap">
      <div class="content-l__top">
        <AppInput v-model="searchName" placeholder="역할 이름으로 검색" />
        <button class="btn-m blue" @click="onRoleCreateView">생성</button>
      </div>
      <div class="content-l__bottom" ref="scrollHistory" v-scroll="onScroll">
        <div class="role-list">
          <div class="list-items">
            <div class="item-titles">
              <ul>
                <li class="item-row" v-for="row in data" :key="row.id">
                  <div
                    class="btn-link"
                    :class="{
                      active: selectId === row.id || activeTooltipId === row.id,
                    }"
                    @click="onRoleLink(row.id)"
                  >
                    <div class="text">
                      {{ row.title }}
                    </div>
                    <span
                      class="btn-more"
                      @click.stop.prevent="onMore($event, row.id)"
                    ></span>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
      <div
        class="pop-window__role"
        ref="infoWindow"
        v-if="activeTooltipId !== ''"
        :style="{ left: tooltipXY.x, top: tooltipXY.y }"
      >
        <ul>
          <li>
            <button class="btn-pop" @click.prevent="onRemove">삭제</button>
          </li>
          <li>
            <button class="btn-pop" @click.prevent="onRoleChange">
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

    <!-- 삭제 확인 -->
    <AppDialog
      v-model:view="removeRole.view"
      :message="removeRole.msg"
      @confirm="confirmRemoveRole"
    />

    <!-- 역할 생성 / 등록정보 변경 -->
    <AppWindow v-model:view="roleCreateWindowView" width="450px">
      <RoleCreateDialog
        :selectId="editId"
        @save="onRoleCreateSave"
        @cancel="onRoleCreateCancel"
        >{{
          editId === '' ? '역할생성' : '역할 등록정보 변경'
        }}</RoleCreateDialog
      >
    </AppWindow>

    <!-- 속성 -->
    <AppWindow v-model:view="attributeWindowView" width="480px">
      <RoleAttributeDialog @close="onAttributeClose"
        >역할 속성</RoleAttributeDialog
      >
    </AppWindow>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { onClickOutside } from '@vueuse/core';
import { reactive } from 'vue';
import { vScroll } from '@vueuse/components';
import AppDialog from '@/components/ui/AppDialog.vue';
import RoleCreateDialog from './RoleCreateDialog.vue';
import RoleAttributeDialog from './RoleAttributeDialog.vue';

const searchName = ref('');

const data = ref([]);
const attachData = () => {
  data.value = [
    {
      id: '1',
      title: 'Administrator',
    },
    {
      id: '2',
      title: 'Creator',
    },
    {
      id: '3',
      title: 'Updater',
    },
    {
      id: '4',
      title: 'Eraser',
    },
    {
      id: '5',
      title: 'Reader',
    },
    {
      id: '6',
      title: 'Browsing',
    },
  ];
};

attachData();

const selectId = ref('');
const activeTooltipId = ref('');

//리스트 클릭
const onRoleLink = id => {
  selectId.value = id;
};

/******** 
삭제
***********/
const removeId = ref('');
const removeRole = reactive({
  view: false,
  msg: '정말로 삭제하시겠습니까?',
});
const onRemove = () => {
  removeId.value = activeTooltipId.value;
  removeRole.view = true;
};
const confirmRemoveRole = () => {
  data.value = data.value.filter(item => item.id !== removeId.value);
  removeId.value = '';
};

/******** 
역할 생성
***********/
const roleCreateWindowView = ref(false);
const onRoleCreateView = () => {
  roleCreateWindowView.value = true;
};
const onRoleCreateSave = () => {
  roleCreateWindowView.value = false;
};
const onRoleCreateCancel = () => {
  roleCreateWindowView.value = false;
  editId.value = '';
};
/******** 
역할 등록정보 변경 
***********/
const editId = ref('');
const onRoleChange = () => {
  editId.value = activeTooltipId.value;
  roleCreateWindowView.value = true;
};
/******** 
속성
***********/
const attributeWindowView = ref(false);
const onAttributeView = () => {
  attributeWindowView.value = true;
};
const onAttributeClose = () => {
  attributeWindowView.value = false;
};

//

// const onReset = () => {
//   selectId.value = '';
//   activeTooltipId.value = '';
// };

//툴팁
const tooltipXY = reactive({ x: '0px', y: '0px' });
const onMore = (event, id) => {
  console.log('more', event.target, event.currentTarget, id);
  activeTooltipId.value = id;
  const tooltipHeight = 108;
  const rect = event.target.getBoundingClientRect();
  console.log(rect.x, rect.y);
  tooltipXY.x = `${rect.x + 35}px`;
  if (rect.bottom + tooltipHeight > window.innerHeight) {
    tooltipXY.y = `${rect.y - 80}px`;
  } else {
    tooltipXY.y = `${rect.y + 10}px`;
  }
};

const infoWindow = ref(null);
onClickOutside(infoWindow, event => {
  activeTooltipId.value = '';
});

//스크롤 체크
const onScroll = () => {
  if (activeTooltipId.value !== '') {
    activeTooltipId.value = '';
  }
};
</script>

<style lang="scss" scoped></style>
