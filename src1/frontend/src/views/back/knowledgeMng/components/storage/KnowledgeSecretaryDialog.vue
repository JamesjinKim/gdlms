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
          <div class="row grid-col2 storage">
            <div>
              <div class="row">
                <div class="row-title">
                  <div class="title-label">주요 키워드</div>
                </div>
                <div class="row-content">
                  <div class="keyword-list__wrap">
                    <div class="list-scroll">
                      <div class="keyword-btns">
                        <div
                          class="btn-key"
                          v-for="(item, index) in data.keywords"
                          :key="item.id"
                        >
                          {{ item.label
                          }}<span
                            class="btn-remove"
                            @click="onRemoveKeyword(index)"
                            ><i class="icon"></i
                          ></span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div class="row">
                <div class="title-label title-m">Advanced Options</div>
              </div>
              <div class="row">
                <div class="row-title">
                  <div class="title-label">Chunk size(tokens)</div>
                  <p>{{ data.chunkSize }}</p>
                </div>
                <div class="row-content">
                  <VueSlider
                    v-model="data.chunkSize"
                    tooltip="none"
                    :adsorb="true"
                    :min="0"
                    :max="100"
                  />
                </div>
              </div>
              <div class="row">
                <div class="row-title">
                  <div class="title-label">Chunk overlap(tokents)</div>
                  <p>{{ data.chunkOverlap }}</p>
                </div>
                <div class="row-content">
                  <VueSlider
                    v-model="data.chunkOverlap"
                    tooltip="none"
                    :adsorb="true"
                    :min="0"
                    :max="100"
                  />
                </div>
              </div>
              <div class="row">
                <div class="check-area">
                  <span class="checkbox-wrap">
                    <input
                      type="checkbox"
                      id="checkText"
                      v-model="data.checkText"
                    />
                    <label for="checkText">본문요약</label>
                  </span>
                  <span class="checkbox-wrap ml20">
                    <input
                      type="checkbox"
                      id="checkImage"
                      v-model="data.checkImage"
                    />
                    <label for="checkImage">이미지요약</label>
                  </span>
                </div>
              </div>
            </div>
            <div>
              <div class="row-title">
                <div class="title-label">벡터 스토어</div>
              </div>
              <div class="fileupload-wrap" style="height: 355px">
                <AppFileupload ref="fileuploadList" />
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
import AppFileupload from '@/components/ui/AppFileupload.vue';

const data = reactive({
  name: '',
  keywords: [],
  chunkSize: 0,
  chunkOverlap: 0,
  checkText: false,
  checkImage: false,
});

const attachData = () => {
  const keywords = [];
  for (let i = 0; i < 30; i++) {
    keywords.push({ id: i, label: '키워드' + i });
  }
  data.keywords = keywords;
};

attachData();

const onRemoveKeyword = index => {
  data.keywords.splice(index, 1);
};

// 저장
const emit = defineEmits(['save', 'cancel']);
const onSave = () => {
  emit('save');
};
const onCancel = () => {
  emit('cancel');
};

const fileuploadList = ref(null);
</script>

<style lang="scss" scoped></style>
