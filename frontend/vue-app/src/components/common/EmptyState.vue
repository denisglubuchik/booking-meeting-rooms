<template>
  <div class="panel stack">
    <strong>{{ title }}</strong>
    <span v-if="description" class="muted">{{ description }}</span>
    <div v-if="$slots.actions" class="row">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string;
  description?: string;
}>();
</script>
