<template>
  <div
    v-if="confirm.state.open"
    ref="backdropRef"
    class="fixed inset-0 z-[60] grid place-items-center bg-[rgba(47,36,29,0.35)] p-4"
    tabindex="-1"
    @click="confirm.resolve(false)"
    @keydown.esc.prevent="confirm.resolve(false)"
  >
    <div
      ref="dialogRef"
      role="dialog"
      aria-modal="true"
      :aria-label="confirm.state.title"
      class="w-full max-w-[460px] rounded-2xl border border-[var(--line-strong)] bg-[#fffdf9] p-4 shadow-[0_16px_34px_rgba(47,36,29,0.2)]"
      @click.stop
      @keydown.tab.prevent="onTabWithinDialog"
    >
      <h3 class="mb-2 text-lg font-semibold">{{ confirm.state.title }}</h3>
      <p class="muted">{{ confirm.state.message }}</p>
      <div class="mt-4 flex justify-end gap-2">
        <Button variant="outline" @click="confirm.resolve(false)">{{ confirm.state.cancelText }}</Button>
        <Button ref="confirmButtonRef" @click="confirm.resolve(true)">{{ confirm.state.confirmText }}</Button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { nextTick, ref, watch } from "vue";
import { useConfirm } from "../features/ui/confirm";
import { Button } from "@/components/ui/button";

const confirm = useConfirm();
const backdropRef = ref<HTMLElement | null>(null);
const dialogRef = ref<HTMLElement | null>(null);
const confirmButtonRef = ref<InstanceType<typeof Button> | null>(null);
const returnFocusEl = ref<HTMLElement | null>(null);

function onTabWithinDialog(event: KeyboardEvent) {
  const container = dialogRef.value;
  if (!container) return;
  const focusable = Array.from(
    container.querySelectorAll<HTMLElement>(
      'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])',
    ),
  );
  if (focusable.length === 0) return;
  const first = focusable[0];
  const last = focusable[focusable.length - 1];
  const active = document.activeElement as HTMLElement | null;
  if (event.shiftKey) {
    if (!active || active === first) {
      last.focus();
      return;
    }
    const prev = focusable[Math.max(0, focusable.indexOf(active) - 1)];
    prev?.focus();
    return;
  }
  if (!active || active === last) {
    first.focus();
    return;
  }
  const next = focusable[Math.min(focusable.length - 1, focusable.indexOf(active) + 1)];
  next?.focus();
}

watch(
  () => confirm.state.open,
  async (isOpen) => {
    if (isOpen) {
      returnFocusEl.value = document.activeElement instanceof HTMLElement ? document.activeElement : null;
      await nextTick();
      backdropRef.value?.focus();
      const buttonEl = confirmButtonRef.value?.$el as HTMLElement | undefined;
      buttonEl?.focus();
      return;
    }
    returnFocusEl.value?.focus();
    returnFocusEl.value = null;
  },
);
</script>
