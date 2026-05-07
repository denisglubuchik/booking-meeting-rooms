<template>
  <div>
    <h2>{{ title }}</h2>
    <p class="muted">{{ subtitle }}</p>
    <div class="grid mt-4">
      <div v-for="(item, idx) in items" :key="idx" class="mini-card">{{ item }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ title: string; subtitle: string; items: string[] }>();
</script>
