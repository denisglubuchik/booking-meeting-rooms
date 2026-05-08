import { toast as sonnerToast } from "vue-sonner";

export type ToastKind = "success" | "error" | "info";
type ToastOptions = {
  duration?: number;
};

export function useToast() {
  return {
    success: (text: string, options?: ToastOptions) =>
      sonnerToast.success(text, options),
    error: (text: string, options?: ToastOptions) =>
      sonnerToast.error(text, options),
    info: (text: string, options?: ToastOptions) =>
      sonnerToast.info(text, options),
  };
}
