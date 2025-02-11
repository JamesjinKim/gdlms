import { useSpinnerStore } from '@/stores/spinner';
import { storeToRefs } from 'pinia';

export function useSpinner() {
  const store = useSpinnerStore();
  const { spinnerStatus } = storeToRefs(store);
  const { setSpinnerStatus } = store;
  return {
    spinnerStatus,
    setSpinnerStatus,
  };
}
