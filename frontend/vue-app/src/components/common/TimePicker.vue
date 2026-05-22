<template>
  <Input
    v-if="isCoarsePointer"
    :model-value="normalizedValue"
    type="time"
    :step="stepSeconds"
    lang="ru-RU"
    @update:model-value="onNativeInput"
  />
  <div v-else class="time-picker-desktop">
    <Select :model-value="selectedHour" @update:model-value="onHourChange">
      <SelectTrigger class="w-[92px]" aria-label="Часы">
        <SelectValue placeholder="ЧЧ" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem v-for="hour in hours" :key="hour" :value="hour">{{ hour }}</SelectItem>
      </SelectContent>
    </Select>
    <span class="kv">:</span>
    <Select :model-value="selectedMinute" @update:model-value="onMinuteChange">
      <SelectTrigger class="w-[92px]" aria-label="Минуты">
        <SelectValue placeholder="ММ" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem v-for="minute in minutes" :key="minute" :value="minute">{{ minute }}</SelectItem>
      </SelectContent>
    </Select>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";
import { Input } from "../ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../ui/select";

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
const selectedHour = computed(() => normalizedValue.value.slice(0, 2));
const selectedMinute = computed(() => normalizedValue.value.slice(3, 5));
const stepSeconds = computed(() => Math.max(1, props.stepMinutes) * 60);

const hours = Array.from({ length: 24 }, (_, i) => String(i).padStart(2, "0"));
const minutes = computed(() => {
  const step = Math.max(1, props.stepMinutes);
  const values: string[] = [];
  for (let i = 0; i < 60; i += step) {
    values.push(String(i).padStart(2, "0"));
  }
  return values;
});

function emitTime(hour: string, minute: string) {
  emit("update:modelValue", `${hour}:${minute}`);
}

function onHourChange(value: unknown) {
  if (value === null) return;
  emitTime(String(value), selectedMinute.value);
}

function onMinuteChange(value: unknown) {
  if (value === null) return;
  emitTime(selectedHour.value, String(value));
}

function onNativeInput(value: string | number) {
  const nextValue = normalizeTime(String(value));
  emit("update:modelValue", nextValue);
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
  display: inline-flex;
  align-items: center;
  gap: 8px;
}
</style>
