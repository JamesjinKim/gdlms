import AppDialog from '@/components/ui/AppDialog.vue';
import AppWindow from '@/components/ui/AppWindow.vue';
import AppInput from '@/components/ui/AppInput.vue';
import SubTitle from '@/components/common/SubTitle.vue';

export default {
  install(app) {
    app.component('AppDialog', AppDialog);
    app.component('AppWindow', AppWindow);
    app.component('AppInput', AppInput);
    app.component('SubTitle', SubTitle);
  },
};
