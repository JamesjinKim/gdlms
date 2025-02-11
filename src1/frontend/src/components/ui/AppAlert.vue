<template>
  <transition name="fade-view">
    <div class="dialog-wrapper alert" v-if="alertInfos.view">
      <div class="dialog-box">
        <!-- <span
          class="btn-close"
          @click="
            setAlertStatus({
              view: false,
              message: '',
            })
          "
          >닫기</span
        > -->
        <!-- <div class="dialog-header">
          <slot name="header">알림</slot>
        </div> -->
        <div class="dialog-body">
          <span v-html="alertInfos.message"></span>
        </div>
        <div class="dialog-footer">
          <button
            type="button"
            class="ui-button"
            @click="
              setAlertStatus({
                view: false,
                message: '',
              })
            "
          >
            확인
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { useAlert } from '@/composables/alert';

const { alertInfos } = useAlert();

const { setAlertStatus } = useAlert();
</script>
