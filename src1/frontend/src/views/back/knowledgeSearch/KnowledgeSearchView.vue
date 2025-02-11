<template>
  <section class="contents-wrap">
    <div class="content-box">
      <div class="content-top"><SubTitle /></div>
      <div class="content-bottom">
        <div class="knowledge-search__wrap">
          <div class="content-area">
            <ChatHistory
              @newChat="onNewChat"
              @updateTitle="onUpdateTitle"
              @remove="onRemoveHistory"
              v-model:data="chatHistoryData"
              v-model:selectId="selectId"
            />
            <ChatView
              v-model:chatData="chatViewData"
              :selectId="selectId"
              v-if="selectId !== ''"
            />
            <ChatStart @question="onStartQuestion" v-else />
          </div>
        </div>
      </div>
    </div>

    <!-- 삭제 확인 -->
    <AppDialog
      v-model:view="removeHistory.view"
      :message="removeHistory.msg"
      @confirm="confirmRemoveHistory"
    />
  </section>
</template>

<script setup>
import SubTitle from '@/components/common/SubTitle.vue';
import ChatHistory from './components/ChatHistory.vue';
import ChatStart from './components/ChatStart.vue';
import ChatView from './components/ChatView.vue';
import { randomKey } from '@/utils/utils.js';
import dayjs from 'dayjs';
import { ref } from 'vue';
import AppDialog from '../../components/ui/AppDialog.vue';
import { reactive } from 'vue';

const chatHistoryData = ref([]);
const chatViewData = ref({ selectType: 0, message: [] });

const attachData = () => {
  chatHistoryData.value = [
    {
      id: randomKey(),
      create: '2024.12.01',
      items: [
        {
          id: 'testId1',
          title:
            '내가 알고 싶은 2024년 회사 경쟁제품 전시회 회사 경쟁제품 전시회',
          type: { label: '회사생활 가이드', value: 2 },
        },
        {
          id: 'testId2',
          title: 'AI란 무엇인가요?',
          type: { label: '인사 총무 업무 비서', value: 1 },
        },
      ],
    },
  ];
};

attachData();

// 선택 지식비서에게 무엇이든 물어보세요.
const onNewChat = () => {
  onReset();
};

const onReset = () => {
  chatViewData.value = { selectType: 0, message: [] };
  selectId.value = '';
};

const selectType = ref(0);
const selectId = ref('');
// 새 채팅
const onStartQuestion = value => {
  const { type, msg } = value;
  selectType.value = type;
  // const now = dayjs().format('YYYY-MM-DD HH:mm:ss');
  const now = dayjs().format('YYYY.MM.DD');
  const findIndex = chatHistoryData.value.findIndex(
    data => data.create === now,
  );
  const id = randomKey();
  selectId.value = id;
  //히스토리 생성
  if (findIndex > -1) {
    chatHistoryData.value[findIndex].items.unshift({
      id: id,
      title: msg,
      type: type,
    });
  } else {
    chatHistoryData.value.unshift({
      id: randomKey(),
      create: now,
      items: [
        {
          id: id,
          title: msg,
          type: type,
        },
      ],
    });
  }

  //챗 시작
  const questionText = { id: randomKey(), type: 'question', msg: msg };
  chatViewData.value.selectType = selectType.value;
  chatViewData.value.message.push(questionText);
};

//타이틀 수정
const onUpdateTitle = data => {
  const { id, title } = data;
  let position = {};
  chatHistoryData.value.some((chat, chatIndex) => {
    const itemIndex = chat.items.findIndex(item => item.id === id);
    if (itemIndex !== -1) {
      position = { chatIndex, itemIndex };
      return true;
    }
    return false;
  });
  console.log(position);
  chatHistoryData.value[position.chatIndex].items[position.itemIndex].title =
    title;
};

//히스토리 삭제
const removeHistory = reactive({
  view: false,
  msg: '정말로 삭제하시겠습니까?',
});
const removeId = ref('');
const onRemoveHistory = id => {
  removeId.value = id;
  removeHistory.view = true;
};
const confirmRemoveHistory = () => {
  console.log(removeId.value, selectId.value, chatHistoryData.value);
  chatHistoryData.value.forEach(history => {
    history.items = history.items.filter(item => item.id !== removeId.value);
  });
  const updatedChatHistoryData = chatHistoryData.value.filter(
    history => history.items.length > 0,
  );
  chatHistoryData.value = updatedChatHistoryData;
  if (removeId.value === selectId.value) {
    onReset();
  }
};
</script>
