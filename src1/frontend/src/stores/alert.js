import { defineStore } from 'pinia';

export const useAlertStore = defineStore('alert', {
  state: () => ({
    alertInfos: {
      view: false,
      message: '',
    },
  }),
  actions: {
    setAlertStatus(state) {
      this.alertInfos = state;
    },
  },
});
