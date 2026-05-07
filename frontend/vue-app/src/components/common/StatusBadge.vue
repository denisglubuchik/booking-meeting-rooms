<template>
  <span class="badge" :class="badgeClass">{{ normalizedLabel }}</span>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  status: string;
  label?: string;
}>();

const badgeClass = computed(() => {
  if (props.status === "created" || props.status === "active") return "badge-created";
  if (props.status === "cancelled" || props.status === "inactive") return "badge-cancelled";
  return "badge-completed";
});

const normalizedLabel = computed(() => {
  if (props.label) return props.label;
  if (props.status === "created") return "активно";
  if (props.status === "cancelled") return "отменено";
  if (props.status === "completed") return "завершено";
  if (props.status === "active") return "активен";
  if (props.status === "inactive") return "неактивен";
  return props.status;
});
</script>
