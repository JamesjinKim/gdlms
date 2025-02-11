<template>
  <div class="content-r">
    <div class="content-r__wrap">
      <!-- <div class="test-box">{{ chatMessage }}</div> -->
      <v-select
        :options="knowledgeOptions"
        label="label"
        index="value"
        v-model="knowledge"
        :searchable="false"
        :clearable="false"
        :reduce="option => option.value"
        style="width: 240px"
        class="chat-select always-open"
      />
      <div class="char-view__wrap" :class="{ reference: useReference }">
        <transition name="reference-list" mode="out-in">
          <ReferencePop :referenceId="referenceId" v-if="useReference" />
        </transition>
        <div class="chat-list">
          <div class="list-scroll" ref="scrollContainer">
            <template v-for="item in chatMessage" :key="item.id">
              <div class="question" v-if="item.type === 'question'">
                <div class="msg">{{ item.msg }}</div>
              </div>
              <div class="answer" :class="{ wide: item.msg.length > 1 }" v-else>
                <i class="icon-answer"></i>
                <div class="msg" :class="{ useSlide: item.msg.length > 1 }">
                  <swiper
                    :slides-per-view="'auto'"
                    :space-between="14"
                    :autoHeight="false"
                    :navigation="{
                      nextEl: `.swiper-button-next.slider-${item.id}`,
                      prevEl: `.swiper-button-prev.slider-${item.id}`,
                    }"
                    :simulate-touch="false"
                    :modules="modules"
                    @swiper="swiper => onSwiper(swiper, item.id)"
                    @slideChange="onSlideChange"
                  >
                    <swiper-slide
                      v-for="(answer, index) in item.msg"
                      :key="index"
                    >
                      <div class="msg-row">
                        <div
                          class="msg-box"
                          v-html="changeMarkdown(answer.md)"
                        ></div>
                        <div class="btns-link">
                          <span
                            class="btn-link copy"
                            @click="onCopy(answer.md)"
                            title="복사"
                            ><i class="icon-link"></i
                          ></span>
                          <span
                            class="btn-link reply"
                            @click="onReply(item.id)"
                            title="다시 답변하기"
                            ><i class="icon-link"></i
                          ></span>
                          <span
                            class="btn-link good"
                            :class="{
                              active: answer.evaluation === 'good',
                            }"
                            @click="onGood(item.id, index)"
                            v-if="answer.evaluation !== 'bad'"
                            title="좋아요"
                            ><i class="icon-link"></i
                          ></span>
                          <span
                            class="btn-link bad"
                            :class="{
                              active: answer.evaluation === 'bad',
                            }"
                            @click="onBad(item.id, index)"
                            v-if="answer.evaluation !== 'good'"
                            title="싫어요"
                            ><i class="icon-link"></i
                          ></span>
                          <span
                            class="btn-link reference"
                            :class="{ active: answer.id === referenceId }"
                            @click="onReference(answer.id)"
                            title="참조"
                            ><i class="icon-link"></i
                          ></span>
                        </div>
                      </div>
                    </swiper-slide>
                  </swiper>
                  <div
                    class="swiper-button-prev"
                    :class="`slider-${item.id}`"
                    v-show="item.msg.length > 1"
                  >
                    <i class="icon"></i>
                  </div>
                  <div
                    class="swiper-button-next"
                    :class="`slider-${item.id}`"
                    v-show="item.msg.length > 1"
                  >
                    <i class="icon"></i>
                  </div>
                </div>
              </div>
            </template>
            <div class="chat-loding" v-if="loaderView">
              <span class="icon-loader"></span>
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
              ref="inputQuestion"
            />
            <button
              class="btn-send"
              :disabled="questionData === ''"
              @click="questionSend"
            ></button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { marked } from 'marked';
import { reactive, ref, onMounted, watch, toRef } from 'vue';
import { Swiper, SwiperSlide } from 'swiper/vue';
import { Navigation, Pagination } from 'swiper/modules';
import { randomKey } from '@/utils/utils.js';
import { chatData1 } from '@/views/dummyData/data.js';
import ReferencePop from '@/views/knowledgeSearch/components/reference/ReferencePop.vue';

const modules = ref([Navigation, Pagination]);

const props = defineProps({
  selectId: {
    type: String,
    default: '',
  },
  chatData: {
    type: Object,
    default: () => {},
  },
});

const loaderView = ref(false);

const chatMessage = ref([]); // 채팅내용 데이터

const scrollContainer = ref(null); // 스크롤 영역 Div
const inputQuestion = ref(null); // 질문 Input

const knowledgeOptions = reactive([
  { label: '지식비서', value: 0 },
  { label: '인사 총무 업무 비서', value: 1 },
  { label: '회사생활 가이드', value: 2 },
  { label: '정보 보안 업무 비서', value: 3 },
  { label: '홍보 및 마케팅 업무 비서 ', value: 4 },
]);

const knowledge = ref(0);

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

// 동적 생성된 Swiper Instance 가져오기
const swiperInstances = reactive(new Map());
const getSwiperById = id => {
  return swiperInstances.get(id);
};
// 동적 생성된 Swiper Instance 저장
const onSwiper = (swiper, id) => {
  swiperInstances.set(id, swiper); // Swiper 인스턴스를 ID와 함께 저장
  // console.log(`Swiper initialized for ${id}:`, swiper);
};
const onSlideChange = () => {
  console.log('slide change');
};

// 질문, 답변시 스크롤 최하단으로 이동 처리
const scrollToBottom = () => {
  if (!scrollContainer.value) return;
  const element = scrollContainer.value;
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
  const answerData = `Marked - Markdown Parser
========================

1. **테스트**

|제목|내용|설명|
|------|---|---|
|테스트1|테스트2|테스트3|
|테스트1|테스트2|테스트3|
|테스트1|테스트2|테스트3|

[Marked] lets you convert [Markdown] into HTML.  Markdown is a simple text format whose goal is to be very easy to read and write, even when not converted to HTML.  This demo page will let you type anything you like and see how it gets converted.  Live.  No more waiting around.

How To Use The Demo
-------------------

1. Type in stuff on the left.
2. See the live updates on the right.

That's it.  Pretty simple.  There's also a drop-down option above to switch between various views:

- Preview:**  A live display of the generated HTML as it would render in a browser.
- HTML Source:**  The generated HTML before your browser makes it pretty.
- Lexer Data:**  What [marked] uses internally, in case you like gory stuff like this.
- Quick Reference:**  A brief run-down of how to format things using markdown.

Why Markdown?
-------------

It's easy.  It's not overly bloated, unlike HTML.  Also, as the creator of [markdown] says,

The overriding design goal for Markdown's
formatting syntax is to make it as readable
as possible. The idea is that a
Markdown-formatted document should be
publishable as-is, as plain text, without
looking like it's been marked up with tags
or formatting instructions.

Ready to start writing?  Either start changing stuff on the left or
[clear everything](/demo/?text=) with a simple click.

[Marked]: https://github.com/markedjs/marked/
[Markdown]: http://daringfireball.net/projects/markdown/
`;
  const answerText = {
    id: randomKey(),
    type: 'answer',
    msg: [{ id: randomKey(), evaluation: '', md: answerData }],
  };
  console.log('answerText=> ', answerText);
  chatMessage.value.push(answerText);

  // 스크롤 하단 이동
  setTimeout(() => {
    scrollToBottom();
  });
};

// 질문
const questionData = ref('');
const questionSend = () => {
  if (questionData.value === '') return;
  loaderView.value = true; //chat loader

  const answerText = {
    id: randomKey(),
    type: 'question',
    msg: questionData.value,
  };
  chatMessage.value.push(answerText);

  questionData.value = '';

  // 스크롤 하단 이동
  setTimeout(() => {
    scrollToBottom();
  });

  //답변 테스트
  setTimeout(() => {
    loaderView.value = false; //chat loader
    answerSend();
  }, 1000);
};

// 답변내용 마크다운 복사
const onCopy = msg => {
  const textToCopy = msg.trim();
  navigator.clipboard.writeText(textToCopy);
};

/*********************
 *  답변글 버튼 액션
 **********************/

// 다시 답변하기
const onReply = id => {
  const index = chatMessage.value.findIndex(item => item.id === id);
  const replyData = `# 테스트입니다. 반갑습니다.!!!
  ## Header 2
  ### Header 3
  #### Header 4`;
  chatMessage.value[index].msg.push({
    id: randomKey(),
    evaluation: '',
    md: replyData,
  });

  const target = getSwiperById(id);

  setTimeout(() => {
    const lastSlideIndex = chatMessage.value[index].msg.length - 1;
    target.slideTo(lastSlideIndex);
  }, 100);
};

//좋아요
const onGood = (id, index) => {
  const mainIndex = chatMessage.value.findIndex(item => item.id === id);
  if (chatMessage.value[mainIndex].msg[index].evaluation !== '') return;
  chatMessage.value[mainIndex].msg[index].evaluation = 'good';
};

//싫어요
const onBad = (id, index) => {
  const mainIndex = chatMessage.value.findIndex(item => item.id === id);
  if (chatMessage.value[mainIndex].msg[index].evaluation !== '') return;
  chatMessage.value[mainIndex].msg[index].evaluation = 'bad';
};

//참조
const useReference = ref(false);
const referenceId = ref('');
const onReference = id => {
  if (useReference.value) {
    if (referenceId.value === id) {
      referenceId.value = '';
      useReference.value = false;
    } else {
      referenceId.value = id;
      // 선택한 참조 데이터 다시 가져오기
    }
  } else {
    referenceId.value = id;
    useReference.value = true;
  }
};

// 기존 채팅내역 불러오기
const testLoadData = () => {
  chatMessage.value = [];
  knowledge.value = 0;
  setTimeout(() => {
    chatMessage.value = chatData1;

    // 스크롤 하단 이동
    setTimeout(() => {
      scrollToBottom();
    });
  }, 100);
};

//초기 실행
const init = () => {
  if (props.chatData.message.length > 0) {
    /**** 새 채팅 ****/
    //초기 질문내용
    const { selectType, message } = props.chatData;
    knowledge.value = selectType;
    chatMessage.value = message;

    loaderView.value = true; //chat loader

    //답변 테스트
    setTimeout(() => {
      loaderView.value = false; //chat loader
      answerSend();
    }, 1000);
    ``;
  } else {
    /**** 기존 채팅내역 불러오기 ****/
    testLoadData();
  }

  // 질문 input text에 포커스 이동
  if (inputQuestion.value) {
    inputQuestion.value.focus();
  }
};

watch(
  () => props.selectId,
  () => {
    //아이디 변경시마다 해당 데이터 로드 처리
    console.log('[watch] selectId=> ', props.selectId);
    testLoadData();
  },
  { immediate: false },
);

onMounted(() => {
  init();
});
</script>
