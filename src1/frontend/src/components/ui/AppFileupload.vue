<template>
  <div class="file-upload__wrap">
    <div class="upload-top">
      <span class="label file">파일명</span>
      <span class="label size">크기</span>
      <span class="label status">상태</span>
      <span class="label remove"></span>
    </div>
    <div class="upload-bottom">
      <div class="upload-scroll">
        <ul>
          <li v-for="file in uploadedFiles" :key="file.id">
            <span class="col file">{{ file.name }}</span>
            <span class="col size">{{ (file.size / 1024).toFixed(2) }} KB</span>
            <span class="col status">{{ file.status }}</span>
            <span class="col remove">
              <span
                class="btn-remove"
                title="삭제"
                @click="onRemoveRow(file.id)"
                ><i class="icon"></i
              ></span>
            </span>
          </li>
        </ul>
      </div>
      <div class="add-files">
        <div v-bind="getRootProps()">
          <input v-bind="getInputProps()" style="display: none" />
          <div class="blank-files" v-if="isDragActive">
            <div class="blank-infos">
              <div class="info-drop">파일을 이곳에 드롭하세요.</div>
            </div>
          </div>
          <div class="blank-files" v-else>
            <div class="blank-infos">
              <div class="info-text">Drag & Drop to Upload File</div>
              <div class="file-text">Supports: PDF</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 삭제 확인 -->
    <AppDialog
      v-model:view="removeRow.view"
      :message="removeRow.msg"
      @confirm="cellRemoveConfirm"
    />
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useDropzone } from 'vue3-dropzone';

const uploadedFiles = ref([]); // 파일 리스트를 저장할 상태

const onDrop = (acceptedFiles, rejectReasons) => {
  console.log('Accepted Files:', acceptedFiles);
  console.log('Reject Reasons:', rejectReasons);

  const filesWithIds = acceptedFiles.map(file => ({
    id: Date.now() + Math.random(),
    name: file.name,
    size: file.size,
    fileObject: file,
    status: 'uploading',
  }));
  uploadedFiles.value.push(...filesWithIds);
};

const options = reactive({
  multiple: true, // 여러 파일 업로드 허용
  onDrop,
  accept: '.pdf', // 허용 확장자
});

const {
  getRootProps,
  getInputProps,
  isDragActive,
  isFocused,
  isDragReject,
  open,
} = useDropzone(options);

defineExpose({ open });

/******** 
삭제하기
***********/
const removeRow = reactive({
  view: false,
  msg: '정말로 삭제하시겠습니까?',
});
const selectedId = ref('');
const onRemoveRow = id => {
  console.log('uploadedFiles=', uploadedFiles);
  selectedId.value = id;
  removeRow.view = true;
};

// callDetailInfo 메소드 정의
const cellRemoveConfirm = () => {
  const updatedData = uploadedFiles.value.filter(
    item => item.id !== selectedId.value,
  );
  uploadedFiles.value = updatedData;
  selectedId.value = '';
};
</script>

<style lang="scss" scoped></style>
