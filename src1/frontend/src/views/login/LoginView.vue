<template>
  <div class="login-wrap">
    <div class="form-box">
      <form @submit.prevent="submitForm" class="form">
        <div class="form-header">
          <div class="logo"></div>
        </div>
        <div class="form-body">
          <div class="login-inputs">
            <div class="input-id">
              <span class="icon"></span>
              <AppInput
                type="text"
                class="id"
                placeholder="ID"
                v-model="logInfo.userId"
              />
            </div>
            <div class="input-password">
              <span class="icon"></span>
              <AppInput
                type="password"
                class="password"
                placeholder="PASSWORD"
                v-model="logInfo.userPwd"
              />
            </div>
          </div>
          <div class="login-btns">
            <button type="submit" class="btn-login">로그인</button>
          </div>
        </div>
        <div class="form-footer">
          <div class="btns"></div>
          <div class="copyright">
            Copyright© 2025 GDLMS. All rights reserved.
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { object, string } from 'yup';
import { useAlert } from '@/composables/alert';
import AppInput from '@/components/ui/AppInput.vue';

const router = useRouter();

const store = useAuthStore();
const { setUser, setToken } = store;

const logInfo = reactive({
  userId: '',
  userPwd: '',
});

const schema = object().shape({
  userId: string()
    .required('아이디를 입력하세요.')
    .min(5, '아이디는 5글자 이상 입력'),
  userPwd: string()
    .required('패스워드를 입력하세요.')
    .min(5, data => `패스워드는 ${data.min}글자 이상 입력`),
});
const { setAlertStatus } = useAlert();

const submitForm = async () => {
  try {
    await schema.validateSync(logInfo, { abortEarly: false });

    const sompleToken = 'dsafadsf@3$dsfdasfvx123';

    const userInfo = {
      userId: logInfo.userId,
      permission: 'USER-00',
    };
    setUser(userInfo);
    setToken(sompleToken);

    router.push('/main');
  } catch (error) {
    const result = error.inner[0];

    if (result.path === 'userId') {
      setAlertStatus({ view: true, message: result.message });
      return;
    }
    if (result.path === 'userPwd') {
      setAlertStatus({ view: true, message: result.message });
      return;
    }
    // setAlertStatus({ view: true, message: result.message });
  }
};
</script>

<style lang="scss"></style>
