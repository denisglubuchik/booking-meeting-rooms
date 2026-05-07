import { reactive } from "vue";

type Resolver = (ok: boolean) => void;

type ConfirmState = {
  open: boolean;
  title: string;
  message: string;
  confirmText: string;
  cancelText: string;
  resolver: Resolver | null;
};

const state = reactive<ConfirmState>({
  open: false,
  title: "Подтверждение",
  message: "",
  confirmText: "Подтвердить",
  cancelText: "Отмена",
  resolver: null,
});

export function useConfirm() {
  async function ask(params: {
    title?: string;
    message: string;
    confirmText?: string;
    cancelText?: string;
  }): Promise<boolean> {
    state.title = params.title || "Подтверждение";
    state.message = params.message;
    state.confirmText = params.confirmText || "Подтвердить";
    state.cancelText = params.cancelText || "Отмена";
    state.open = true;

    return new Promise((resolve) => {
      state.resolver = resolve;
    });
  }

  function resolve(ok: boolean) {
    if (state.resolver) state.resolver(ok);
    state.resolver = null;
    state.open = false;
  }

  return { state, ask, resolve };
}
