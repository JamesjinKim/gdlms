import { defineStore } from 'pinia';
import { useLocalStorage, StorageSerializers } from '@vueuse/core';

// console.log('[getUserFromStorage]', getUserFromStorage());

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: useLocalStorage('x_user', null, {
      serializer: StorageSerializers.object,
    }),
    token: useLocalStorage('x_auth', null),
    checkId: useLocalStorage('x_logId', null),
  }),
  getters: {
    isLoggedIn(state) {
      return state.token;
    },
    userToken(state) {
      return state.token;
    },
    userInfo(state) {
      return state.user;
    },
    useCheckId(state) {
      return state.checkId;
    },
  },
  actions: {
    setUser(user) {
      this.user = user;
    },
    setToken(token) {
      this.token = token;
    },
    setCheckId(checkId) {
      this.checkId = checkId;
    },
    logout() {
      this.user = null;
      this.token = null;
    },
  },
});
