import { useAlertStore } from '@/stores/alert';
import { storeToRefs } from 'pinia';

export function useAlert() {
  const store = useAlertStore();
  const { alertInfos } = storeToRefs(store);
  const { setAlertStatus } = store;
  return {
    alertInfos,
    setAlertStatus,
  };
}
