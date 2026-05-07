<template>
  <p class="muted">{{ message || "Загрузка..." }}</p>
</template>

<script setup lang="ts">
defineProps<{
  message?: string;
}>();
</script>
