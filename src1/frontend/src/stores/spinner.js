import { defineStore } from 'pinia';

export const useSpinnerStore = defineStore('spinner', {
  state: () => ({
    spinnerStatus: false,
  }),
  actions: {
    setSpinnerStatus(state) {
      this.spinnerStatus = state;
    },
  },
});
