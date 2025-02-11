<template>
  <div class="app-input__wrapper">
    <input
      :type="type === 'price' ? 'tel' : type"
      :value="modelValue"
      :placeholder="placeholder"
      autocomplete="off"
      @input="bindNumber"
      @focus="onFocus"
      @blur="onBlur"
    />
    <div class="error-msg" v-if="msg !== ''">{{ msg }}</div>
  </div>
</template>

<script setup>
import { isReactive, isRef, ref, watch } from 'vue';

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: '',
  },
  placeholder: {
    type: String,
    default: '',
  },
  type: {
    type: String,
    default: 'text',
  },
  msg: {
    type: String,
    default: '',
  },
});

const emit = defineEmits(['update:modelValue', 'blur']);

// const comma = val => {
//   return String(val).replace(/(\d)(?=(?:\d{3})+(?!\d))/g, '$1,');
// };
// const uncomma = str => {
//   return String(str).replace(/[^\d]+/g, '');
// };

const bindNumber = $event => {
  var value = $event.target.value;
  if (props.type === 'tel') {
    if (value.length >= 11) {
      value = value.replace(/^(\d{2,3})(\d{3,4})(\d{4})$/, `$1-$2-$3`);
    }
  }
  if (props.type === 'price') {
    console.log('run~~');
    var currency = +value.replace(/[^\d]/g, '').toString();
    value = Intl.NumberFormat().format(currency);
  }
  if (props.type === 'number') {
    const reg = /[ㄱ-ㅎ|ㅏ-ㅣ|가-힣|a-z]/;
    if (reg.exec(props.modelValue) !== null) {
      let value = props.modelValue;
      emit('update:modelValue', value.replace(/[^0-9]/g, ''));
    }
    if (isNaN(parseFloat(value))) {
      emit('update:modelValue', '');
    }
  }
  if (props.type === 'price') {
    checkPriceComma();
  }

  emit('update:modelValue', value);
  // emit('inputChange');
};

const onFocus = () => {
  if (props.type === 'number' || props.type === 'price') {
    if (props.modelValue == 0) {
      emit('update:modelValue', '');
    }
  }
};
const onBlur = () => {
  if (props.type === 'number' || props.type === 'price') {
    if (props.modelValue == 0) {
      emit('update:modelValue', 0);
    }
  }
  emit('blur');
};
const checkPriceComma = () => {
  console.log('price~~');
  let priceValue = String(props.modelValue);
  var currency = +priceValue.replace(/[^\d]/g, '').toString();
  priceValue = Intl.NumberFormat().format(currency);
  emit('update:modelValue', priceValue);
};

if (props.type === 'price') {
  checkPriceComma();
}
</script>
