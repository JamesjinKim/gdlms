<template>
  <div class="window-wrap">
    <div class="window-top">
      <div class="title">
        <slot></slot>
      </div>
    </div>
    <div class="window-body">
      <div class="knowledgeSecretary-wrap">
        <div class="row mb20">
          <div class="row flex">
            <div class="title-label">이름</div>
            <div class="row-content">
              <AppInput
                type="text"
                placeholder="사용자에게 친숙한 이름을 입력해 주세요."
                v-model="data.name"
                style="width: 100%"
              />
            </div>
          </div>
        </div>
        <div class="row answer-type">
          <div class="row grid-col2">
            <div>
              <div class="row">
                <div class="row-title">
                  <div class="title-label">모델</div>
                </div>
                <div class="row-content">
                  <v-select
                    :options="modelOptions"
                    label="label"
                    index="value"
                    :reduce="option => option.value"
                    v-model="data.model"
                    :searchable="false"
                    :clearable="false"
                    style="width: 100%"
                  />
                </div>
              </div>
              <div class="row">
                <div class="row-title">
                  <div class="title-label">Temperature</div>
                  <p>
                    <AppInput
                      type="text"
                      placeholder=""
                      v-model="data.temperature"
                      style="width: 60px"
                      class="slider-input"
                    />
                  </p>
                </div>
                <div class="row-content">
                  <VueSlider
                    v-model="data.temperature"
                    tooltip="none"
                    :adsorb="true"
                    :min="0"
                    :max="1"
                    :interval="0.01"
                  />
                </div>
              </div>
              <div class="row">
                <div class="row-title">
                  <div class="title-label">Maximum Tokens</div>
                  <p>
                    <AppInput
                      type="text"
                      placeholder=""
                      v-model="data.maximumTokens"
                      style="width: 60px"
                      class="slider-input"
                    />
                  </p>
                </div>
                <div class="row-content">
                  <VueSlider
                    v-model="data.maximumTokens"
                    tooltip="none"
                    :adsorb="true"
                    :min="0"
                    :max="100"
                  />
                </div>
              </div>
              <div class="row">
                <div class="row-title">
                  <div class="title-label">Top P</div>
                  <p>
                    <AppInput
                      type="text"
                      placeholder=""
                      v-model="data.topP"
                      style="width: 60px"
                      class="slider-input"
                    />
                  </p>
                </div>
                <div class="row-content">
                  <VueSlider
                    v-model="data.topP"
                    tooltip="none"
                    :adsorb="true"
                    :min="0"
                    :max="100"
                  />
                </div>
              </div>
              <div class="row">
                <div class="row-title">
                  <div class="title-label">Frequency Penalty</div>
                  <p>
                    <AppInput
                      type="text"
                      placeholder=""
                      v-model="data.frequencyPenalty"
                      style="width: 60px"
                      class="slider-input"
                    />
                  </p>
                </div>
                <div class="row-content">
                  <VueSlider
                    v-model="data.frequencyPenalty"
                    tooltip="none"
                    :adsorb="true"
                    :min="0"
                    :max="100"
                  />
                </div>
              </div>
            </div>
            <div>
              <div class="row-title">
                <div class="title-label">System Prompt</div>
              </div>
              <textarea
                class="text-area"
                v-model="data.systemPrompt"
                maxlength="1000"
              ></textarea>
              <div class="textarea-total">
                {{ data.systemPrompt.length }}/1000
              </div>
            </div>
          </div>
        </div>
        <div class="btns">
          <button class="btn-m blue" @click="onSave">저장</button>
          <button class="btn-m" @click="onCancel">취소</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import VueSlider from 'vue-3-slider-component';

const name = ref('');
const temperature = ref(0);

const modelOptions = reactive([{ label: 'GPT-4o', value: 0 }]);

const data = reactive({
  name: '',
  model: 0,
  temperature: 0,
  maximumTokens: 0,
  topP: 0,
  frequencyPenalty: 0,
  systemPrompt: `저는 금융 카드 분야에 특화된 AI 상담 비서입니다. 고객이 궁금해하는 질문에 대해 상담원이 제시한 해결 방법을 고객의 입장에서 구어체로 간단히 요약해드립니다. 

- 고객 질문: <고객>으로 시작하는 문장 
- 상담원 답변: <상담원>으로 시작하는 문장

요약내용 작성방법은 아래 내용을 준수해서 작성합니다. 
1. 상담사의 첫인사와 끝인사를 포함하지 않습니다. 2. 상담내용 포함되지 않은 키워드를 포함시키지 않습니다. 
3. 질문답변 형식으로 대화방식으로 작성하지 않습니다.
`,
});

// 저장
const emit = defineEmits(['save', 'cancel']);
const onSave = () => {
  emit('save');
};
const onCancel = () => {
  emit('cancel');
};
</script>

<style lang="scss" scoped></style>
