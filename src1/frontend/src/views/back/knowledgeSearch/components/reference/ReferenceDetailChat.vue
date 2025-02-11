<template>
  <div class="char-view__wrap reference-chat">
    <div class="chat-list">
      <div class="list-scroll" ref="scrollReferenceContainer">
        <div class="row-chat" v-for="data in chatData" :key="data.id">
          <div class="chat-date">
            <span class="date-text">{{ data.create }}</span>
          </div>
          <template v-for="item in data.items" :key="item.id">
            <div class="question" v-if="item.type === 'question'">
              <div class="msg">{{ item.msg }}</div>
            </div>
            <div class="answer" v-else>
              <i class="icon-answer"></i>
              <div class="msg">
                <div class="msg-row">
                  <div class="msg-box">
                    <div
                      class="msg-text"
                      v-html="changeMarkdown(item.msg)"
                    ></div>
                    <div class="btn-links" v-if="item.paging.length > 0">
                      <span
                        class="btn-num"
                        v-for="(num, index) in item.paging"
                        :key="index"
                        @click="onPaging(num)"
                        >{{ num }}</span
                      >
                    </div>
                    <span class="btn-reference__copy" @click="onCopy(item.msg)">
                      <i class="icon"></i>
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>

    <div class="input-chat_message">
      <div class="input-question">
        <input
          type="text"
          v-model="questionData"
          placeholder="궁금한 점을 물어보세요."
          @keyup.enter="questionSend"
          ref="inputReferenceQuestion"
        />
        <button
          class="btn-send"
          :disabled="questionData === ''"
          @click="questionSend"
        ></button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { marked } from 'marked';
import { reactive, ref, onMounted, watch, toRef } from 'vue';
import { randomKey } from '@/utils/utils.js';
import dayjs from 'dayjs';

const props = defineProps({
  selectId: {
    type: String,
    default: '',
  },
});

const chatData = ref([]);

const scrollReferenceContainer = ref(null); // 스크롤 영역 Div
const inputReferenceQuestion = ref(null); // 질문 Input

// 마크다운 변환
marked.setOptions({
  gfm: true, // GitHub Flavored Markdown 지원
  breaks: true, // 줄바꿈을 <br>로 처리
  sanitize: false, // HTML 태그 허용
  smartLists: true, // 스마트 리스트 지원
  smartypants: false, // 구두점 변환
});
const changeMarkdown = mdText => {
  const html = marked.parse(mdText);
  return html;
};

// 질문, 답변시 스크롤 최하단으로 이동 처리
const scrollToBottom = () => {
  if (!scrollReferenceContainer.value) return;
  const element = scrollReferenceContainer.value;
  const start = element.scrollTop;
  const end = element.scrollHeight - element.clientHeight;
  const duration = 300;
  const startTime = performance.now();

  const scrollStep = timestamp => {
    const elapsed = timestamp - startTime;
    const progress = Math.min(elapsed / duration, 1);

    element.scrollTop = start + (end - start) * progress;

    if (progress < 1) {
      requestAnimationFrame(scrollStep);
    }
  };
  requestAnimationFrame(scrollStep);
};

// 질문시 답변 샘플
const answerSend = () => {
  const answerData = `경복궁 재건은 1865년(고종 2)에 가서야 고종의 아버지, 흥선대원군의 주도로 시작되어 1868년에 완성되었다. 경복궁은 270여 년 만에 정궁의 자리를 되찾았지만, 이후 경복궁의 역사는 순탄치 못했다. 중건된 경복궁의 많은 건물은 여러 차례의 화재로 소실되고 복구되기를 반복하였다.`;
  const answerText = {
    id: randomKey(),
    type: 'answer',
    msg: answerData,
    paging: [],
  };
  const index = chatData.value.length - 1;
  chatData.value[index].items.push(answerText);
  // // 스크롤 하단 이동
  setTimeout(() => {
    scrollToBottom();
  });
};

// 질문
const questionData = ref('');
const questionSend = () => {
  if (questionData.value === '') return;

  const now = dayjs().format('YYYY.MM.DD');
  const findIndex = chatData.value.findIndex(data => data.create === now);

  console.log('findIndex=', findIndex);

  if (findIndex > -1) {
    findIndex;
    chatData.value[findIndex].items.push({
      id: randomKey(),
      type: 'question',
      msg: questionData.value,
    });
  } else {
    chatData.value.push({
      id: randomKey(),
      create: now,
      items: [
        {
          id: randomKey(),
          type: 'question',
          msg: questionData.value,
        },
      ],
    });
  }

  questionData.value = '';

  // 스크롤 하단 이동
  setTimeout(() => {
    scrollToBottom();
  });

  setTimeout(() => {
    answerSend();
  }, 1000);
};

// 답변내용 마크다운 복사
const onCopy = msg => {
  const textToCopy = msg.trim();
  navigator.clipboard.writeText(textToCopy);
};

const attachData = () => {
  const smapleData = [
    {
      id: 'id1',
      create: '2024.12.06',
      items: [
        { id: 'Cru8e', type: 'question', msg: 'AI는 무엇인가요?' },
        {
          id: 'w0NCf',
          type: 'answer',
          msg: `### AI의 실제 활용 사례
- **의료**: 질병 진단, 신약 개발, 환자 모니터링.
- **금융**: 사기 탐지, 시장 분석, 투자 전략 최적화.
- **제조**: 로봇 공정 자동화, 품질 관리.
- **교통**: 자율주행, 교통 관리.
- **소비자 서비스**: 가상 비서, 고객 서비스 챗봇.
`,
          paging: [],
        },
        { id: 'agc563', type: 'question', msg: '질문합니다.' },
        {
          id: 'w034NCf',
          type: 'answer',
          msg: `- 데이터를 통해 학습하고 예측이나 결정을 내리는 AI 기술입니다.  
   - 알고리즘이 스스로 데이터를 분석하고 패턴을 찾아 행동을 개선합니다.  
   - 예: 스팸 이메일 필터링, 추천 시스템(Netflix, YouTube).
`,
          paging: [2],
        },
      ],
    },
    {
      id: 'id2',
      create: '2024.12.07',
      items: [
        { id: 'agc5632', type: 'question', msg: '질문합니다.' },
        {
          id: 'w034NCf2',
          type: 'answer',
          msg: `- 데이터를 통해 학습하고 예측이나 결정을 내리는 AI 기술입니다.  
   - 알고리즘이 스스로 데이터를 분석하고 패턴을 찾아 행동을 개선합니다.  
   - 예: 스팸 이메일 필터링, 추천 시스템(Netflix, YouTube).
`,
          paging: [1, 2, 3],
        },
      ],
    },
  ];
  chatData.value = smapleData;
};
attachData();

const emit = defineEmits(['movePage']);
const onPaging = num => {
  emit('movePage', num);
};

//초기 실행
const init = () => {
  setTimeout(() => {
    // 스크롤 하단 이동
    scrollToBottom();
  });
  // 질문 input text에 포커스 이동
  setTimeout(() => {
    if (inputReferenceQuestion.value) {
      inputReferenceQuestion.value.focus();
    }
  }, 500);
};

onMounted(() => {
  init();
});
</script>
