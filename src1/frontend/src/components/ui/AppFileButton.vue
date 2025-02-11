<template>
  <div class="filebox button">
    <label :for="`file-btn${id}`" class="blue mr5">{{ label }}</label>
    <input
      type="file"
      :id="`file-btn${id}`"
      class="upload-hidden"
      :accept="accept"
      @change="onSelectFile"
      ref="fileInput"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAlert } from '@/composables/alert';
const { setAlertStatus } = useAlert();

const props = defineProps({
  id: {
    type: [String, Number],
    default: 1,
  },
  accept: {
    type: String,
    default: '.jpg, .png, .jpeg',
  },
  imageUrl: {
    type: String,
    default: '',
  },
  label: {
    type: String,
    default: '찾기',
  },
  useCancel: {
    type: Boolean,
    default: true,
  },
  modelValue: {
    default: '',
  },
});

const emit = defineEmits(['update:modelValue']);

const fileName = ref('');

const fileInput = ref(null);

const resetFile = () => {
  emit('update:modelValue', {});
  fileName.value = '';
};

const getInputFile = () => {
  let files = fileInput.value.files;
  console.log({ files });
  return files.length > 0 ? files[0] : null;
};

const onSelectFile = event => {
  if (window.FileReader) {
    fileName.value = event.target.files[0].name;
  }
  if (!('url' in window) && 'webkitURL' in window) {
    window.URL = window.webkitURL;
  }

  const extArray = event.target.files[0].name.split('.');
  const ext = extArray[extArray.length - 1];
  if (props.accept.indexOf(ext) === -1) {
    setAlertStatus({
      view: true,
      message: `확장자가 ${props.accept} 인 파일을 선택하세요.`,
    });
    resetFile();
    return;
  }

  emit('update:modelValue', {
    fileName: fileName,
    imageUrl: URL.createObjectURL(event.target.files[0]),
    inputFile: getInputFile(),
  });
};
</script>

<style></style>
