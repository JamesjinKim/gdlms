<template>
  <div class="window-wrap">
    <div class="window-top">
      <div class="title">
        <slot></slot>
      </div>
    </div>
    <div class="window-body">
      <div class="userCreate-wrap">
        <div class="row answer-type">
          <div class="row grid-col2">
            <div class="col-l">
              <div class="row flex">
                <div class="title-label">조직정보</div>
                <div class="row-content">
                  <AppInput
                    type="text"
                    placeholder="조직정보를 입력해 주세요."
                    v-model="data.organizationInfo"
                    style="width: 100%"
                  />
                </div>
              </div>
              <div class="row mt10">
                <AppTreeDrag
                  v-model="treeData"
                  :useMore="false"
                  @selectNode="onSelectNode"
                  style="height: 350px"
                />
                <!-- <AppTree :treeData="treeData" style="height: 350px" /> -->
              </div>
            </div>
            <div class="col-r">
              <div class="row grid-col2">
                <div class="row">
                  <div class="row-title">
                    <div class="title-label">직위</div>
                  </div>
                  <div class="row-content">
                    <v-select
                      :options="spotOptions"
                      label="label"
                      index="value"
                      :reduce="option => option.value"
                      v-model="data.spot"
                      :searchable="false"
                      :clearable="false"
                      style="width: 100%"
                    />
                  </div>
                </div>
                <div class="row">
                  <div class="row-title">
                    <div class="title-label">직무</div>
                  </div>
                  <div class="row-content">
                    <v-select
                      :options="jobOptions"
                      label="label"
                      index="value"
                      :reduce="option => option.value"
                      v-model="data.job"
                      :searchable="false"
                      :clearable="false"
                      style="width: 100%"
                    />
                  </div>
                </div>
              </div>
              <div class="row">
                <div class="row-title">
                  <div class="title-label">역할</div>
                </div>
                <div class="row-content">
                  <v-select
                    :options="roleOptions"
                    label="label"
                    index="value"
                    :reduce="option => option.value"
                    v-model="data.role"
                    :searchable="false"
                    :clearable="false"
                    style="width: 100%"
                  />
                </div>
              </div>
              <div class="row">
                <div class="row-title">
                  <div class="title-label required">이름</div>
                </div>
                <div class="row-content">
                  <AppInput
                    type="text"
                    placeholder="사용자 이름을 입력해주세요."
                    v-model="data.name"
                    style="width: 100%"
                  />
                </div>
              </div>
              <div class="row">
                <div class="row-title">
                  <div class="title-label required">사번</div>
                </div>
                <div class="row-content">
                  <AppInput
                    type="text"
                    placeholder="사번을 입력해주세요."
                    v-model="data.cleanup"
                    style="width: 100%"
                  />
                </div>
              </div>
              <div class="row">
                <div class="row-title">
                  <div class="title-label">연락처</div>
                </div>
                <div class="row-content flex">
                  <AppInput
                    type="text"
                    placeholder="사용자 메일주소를 입력해주세요."
                    v-model="data.email"
                    style="width: 100%"
                  />
                  <button class="btn-m gray">메일 검증</button>
                </div>
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
import AppTree from '@/components/ui/AppTree.vue';
import AppTreeDrag from '@/components/ui/AppTreeDrag.vue';

const spotOptions = reactive([{ label: '대표이사', value: 0 }]);
const jobOptions = reactive([{ label: '대표이사', value: 0 }]);
const roleOptions = reactive([{ label: '역할', value: 0 }]);

const treeData = ref([
  {
    data: {
      id: '1',
      code: '1',
      icon: 'folder',
    },
    title: 'PARAMOS',
    isLeaf: false,
    isDraggable: false,
    isSelectable: true,
    children: [
      {
        data: {
          id: '2',
          code: '2',
          icon: 'file',
        },
        title: '감사팀',
        isLeaf: false,
        isDraggable: false,
        isSelectable: true,
      },
      {
        data: {
          id: '3',
          code: '3',
          icon: 'file',
        },
        title: '마케팅',
        isLeaf: false,
        isDraggable: false,
        isSelectable: true,
      },
      {
        data: {
          id: '4',
          code: '4',
          icon: 'folder',
        },
        title: '영업부',
        isLeaf: false,
        isDraggable: false,
        isSelectable: true,
        children: [
          {
            data: {
              id: '4-1',
              code: '4-1',
              icon: 'file',
            },
            title: '영업부1',
            isLeaf: false,
            isDraggable: false,
            isSelectable: true,
          },
          {
            data: {
              id: '4-2',
              code: '4-2',
              icon: 'file',
            },
            title: '영업부2',
            isLeaf: false,
            isDraggable: false,
            isSelectable: true,
          },
          {
            data: {
              id: '4-2',
              code: '4-2',
              icon: 'file',
            },
            title: '영업부3',
            isLeaf: false,
            isDraggable: false,
            isSelectable: true,
          },
        ],
      },
    ],
  },
]);

const data = reactive({
  organizationInfo: '',
  spot: 0,
  job: 0,
  role: 0,
  name: '',
  cleanup: '',
  email: '',
});

// 저장
const emit = defineEmits(['save', 'cancel']);
const onSave = () => {
  emit('save');
};
const onCancel = () => {
  emit('cancel');
};

const onSelectNode = value => {
  console.log(value);
};
</script>

<style lang="scss" scoped></style>
