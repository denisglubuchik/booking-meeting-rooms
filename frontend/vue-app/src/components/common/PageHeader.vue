<template>
  <header class="page-header stack">
    <h2>{{ title }}</h2>
    <p v-if="description" class="muted">{{ description }}</p>
  </header>
</template>

<script setup lang="ts">
defineProps<{
  title: string;
  description?: string;
}>();
</script>
