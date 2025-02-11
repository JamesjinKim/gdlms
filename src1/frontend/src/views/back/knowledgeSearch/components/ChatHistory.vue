<template>
  <div class="content-l">
    <div class="content-l__wrap">
      <div class="content-l__top">
        <span class="btn-chat" @click="onNewChat"
          ><i class="icon"></i> 새 채팅</span
        >
      </div>
      <div class="content-l__bottom" ref="scrollHistory" v-scroll="onScroll">
        <div class="chat-list">
          <div class="list-items" v-for="item in data" :key="item.id">
            <div class="item-date">{{ setToday(item.create) }}</div>
            <div class="item-titles">
              <ul>
                <li class="item-row" v-for="row in item.items" :key="row.id">
                  <div
                    class="btn-link"
                    :class="{
                      active: selectId === row.id || activeTooltipId === row.id,
                    }"
                    @click="onHistoryLink(row.id)"
                  >
                    <!--  @keyup.enter="updateTitle($event, row.id)"-->
                    <div
                      class="text"
                      :class="row.id === editId ? 'editingTitle' : null"
                      :ref="row.id === editId ? 'editingTitle' : null"
                      :contenteditable="editId === row.id"
                      @blur="updateTitle($event, row.id)"
                      @keydown="onKeydown($event, row.id)"
                    >
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
        class="pop-window__history"
        ref="infoWindow"
        v-if="activeTooltipId !== ''"
        :style="{ left: tooltipXY.x, top: tooltipXY.y }"
      >
        <ul>
          <li>
            <button class="btn-pop" @click.prevent="onShare()">공유하기</button>
          </li>
          <li>
            <button class="btn-pop" @click.prevent="onRename()">
              이름 바꾸기
            </button>
          </li>
          <li>
            <button class="btn-pop" @click.prevent="onRemove()">삭제</button>
          </li>
        </ul>
      </div>
    </div>
    <!-- 설정 -->
    <AppWindow v-model:view="shareWindowView" width="550px"
      ><ShareDialog :selectId="selectShareId">공유하기</ShareDialog></AppWindow
    >
  </div>
</template>

<script setup>
import dayjs from 'dayjs';
import { ref } from 'vue';
import { computed, nextTick } from 'vue';
import { onClickOutside } from '@vueuse/core';
import { reactive } from 'vue';
import { vScroll } from '@vueuse/components';
import ShareDialog from './ShareDialog.vue';

const now = computed(() => dayjs().format('YYYY.MM.DD'));
const props = defineProps({
  data: {
    type: Array,
    default: () => [],
  },
  selectId: {
    type: String,
    default: '',
  },
});

const activeTooltipId = ref('');

const emit = defineEmits([
  'newChat',
  'update:selectId',
  'updateTitle',
  'remove',
]);
const onNewChat = () => {
  emit('newChat');
};

const onHistoryLink = id => {
  if (editId.value !== '') return;
  emit('update:selectId', id);
};

// const updateTitle = (event, id) => {
//   emit('updateTitle', { id, title: event.target.innerText });
// };

const updateTitle = (event, id) => {
  emit('updateTitle', { id, title: event.target.innerText.trim() });
  editId.value = '';

  event.target.scrollLeft = 0;
};

const setToday = computed(() => {
  return date => {
    return now.value === date ? '오늘' : date;
  };
});

const editId = ref('');
// const editingTitle = ref(null); // Vue가 관리하는 refs 객체

// 커서를 마지막으로 이동
const focusEndMove = editingElement => {
  const range = document.createRange();
  const selection = window.getSelection();
  range.selectNodeContents(editingElement);
  range.collapse(false);
  selection.removeAllRanges();
  selection.addRange(range);

  editingElement.scrollLeft = editingElement.scrollWidth;
};

//공유하기
const shareWindowView = ref(false);
const selectShareId = ref('');
const onShare = () => {
  selectShareId.value = activeTooltipId.value;
  shareWindowView.value = true;
  activeTooltipId.value = '';
};

// 이름 바꾸기
const onRename = () => {
  editId.value = activeTooltipId.value;
  activeTooltipId.value = '';
  // DOM 업데이트 후 포커스를 설정
  nextTick(() => {
    // const editingElement = editingTitle.value[0];
    const editingElement = document.querySelector('.editingTitle');
    if (editingElement) {
      editingElement.focus();
      // 커서를 마지막으로 이동
      focusEndMove(editingElement);
    }
  });
};
//삭제
const onRemove = () => {
  const id = activeTooltipId.value;
  emit('remove', id);
  activeTooltipId.value = '';
};

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

const onKeydown = (event, id) => {
  if (event.key === 'Enter') {
    event.preventDefault(); // 기본 동작 방지
    updateTitle(event, id); // 엔터 키가 눌리면 제목 업데이트
  }
};
</script>

<style lang="scss" scoped></style>
