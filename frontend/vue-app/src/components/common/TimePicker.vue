<template>
  <Input :model-value="normalizedValue" type="time" :step="stepSeconds" lang="ru-RU" @update:model-value="onNativeInput" />
</template>

<script setup lang="ts">
import { computed } from "vue";
import { Input } from "../ui/input";

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

function isValidTime(value: string) {
  return /^([01]\d|2[0-3]):([0-5]\d)$/.test(value);
}

function normalizeTime(value: string) {
  if (isValidTime(value)) return value;
  return "00:00";
}

const normalizedValue = computed(() => normalizeTime(props.modelValue ?? ""));
const stepSeconds = computed(() => Math.max(1, props.stepMinutes) * 60);

function onNativeInput(value: string | number) {
  emit("update:modelValue", normalizeTime(String(value)));
}
</script>
