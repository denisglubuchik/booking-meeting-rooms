<template>
  <Input
    v-if="isCoarsePointer"
    :model-value="normalizedValue"
    type="time"
    :step="stepSeconds"
    lang="ru-RU"
    @update:model-value="onNativeInput"
  />
  <TimeFieldRoot
    v-else
    v-slot="{ segments }"
    :model-value="desktopValue"
    locale="ru-RU"
    :hour-cycle="24"
    granularity="minute"
    :step="{ minute: normalizedStepMinutes }"
    :step-snapping="true"
    @update:model-value="onDesktopChange"
  >
    <div class="time-picker-desktop">
      <template v-for="item in segments" :key="`${item.part}-${item.value}`">
        <TimeFieldInput
          :part="item.part"
          :class="item.part === 'literal' ? 'time-segment-literal' : 'time-segment-input'"
        >
          {{ item.value }}
        </TimeFieldInput>
      </template>
    </div>
  </TimeFieldRoot>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";
import { Time } from "@internationalized/date";
import { Input } from "../ui/input";
import { TimeFieldInput, TimeFieldRoot } from "reka-ui";

const props = withDefaults(
  defineProps<{
    modelValue?: string;
    stepMinutes?: number;
  }>(),
  {
    stepMinutes: 5,
  },
);

const emit = defineEmits<{
  (e: "update:modelValue", value: string): void;
}>();

const isCoarsePointer = ref(false);
let pointerMedia: MediaQueryList | null = null;
let pointerListener: (() => void) | null = null;

function isValidTime(value: string) {
  return /^([01]\d|2[0-3]):([0-5]\d)$/.test(value);
}

function normalizeTime(value: string) {
  if (isValidTime(value)) return value;
  return "00:00";
}

const normalizedValue = computed(() => normalizeTime(props.modelValue ?? ""));
const stepSeconds = computed(() => Math.max(1, props.stepMinutes) * 60);
const normalizedStepMinutes = computed(() => Math.max(1, props.stepMinutes));

const desktopValue = computed(() => {
  const [hours = "00", minutes = "00"] = normalizedValue.value.split(":");
  return new Time(Number(hours), Number(minutes));
});

function onNativeInput(value: string | number) {
  const nextValue = normalizeTime(String(value));
  emit("update:modelValue", nextValue);
}

function onDesktopChange(value: unknown) {
  if (!value) return;
  if (typeof value !== "object" || value === null || !("hour" in value) || !("minute" in value)) return;
  const hours = String((value as { hour: number }).hour).padStart(2, "0");
  const minutes = String((value as { minute: number }).minute).padStart(2, "0");
  emit("update:modelValue", `${hours}:${minutes}`);
}

function updatePointerMode() {
  if (typeof window === "undefined" || typeof window.matchMedia !== "function") return;
  isCoarsePointer.value = window.matchMedia("(pointer: coarse)").matches;
}

onMounted(() => {
  updatePointerMode();
  pointerMedia = window.matchMedia("(pointer: coarse)");
  pointerListener = () => updatePointerMode();
  pointerMedia.addEventListener("change", pointerListener);
});

onUnmounted(() => {
  if (pointerMedia && pointerListener) pointerMedia.removeEventListener("change", pointerListener);
});
</script>

<style scoped>
.time-picker-desktop {
  display: flex;
  align-items: center;
  min-height: 52px;
  border-radius: 14px;
  border: 1px solid var(--line);
  background: #fffdf9;
  padding: 0 14px;
  gap: 2px;
}

.time-segment-input {
  min-width: 1.8ch;
  border-radius: 8px;
  text-align: center;
  font-size: 32px;
  line-height: 1;
  padding: 8px 3px;
  outline: none;
}

.time-segment-input[data-placeholder] {
  opacity: 0.65;
}

.time-segment-input:focus-visible {
  background: #f3ede4;
}

.time-segment-literal {
  font-size: 24px;
  line-height: 1;
  padding: 6px 2px;
}

@media (max-width: 900px) {
  .time-picker-desktop {
    min-height: 48px;
  }

  .time-segment-input {
    font-size: 28px;
  }

  .time-segment-literal {
    font-size: 22px;
  }
}
</style>
