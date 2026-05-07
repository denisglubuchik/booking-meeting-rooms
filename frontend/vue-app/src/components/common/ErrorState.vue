<template>
  <p class="muted text-danger">{{ message }}</p>
</template>

<script setup lang="ts">
defineProps<{
  message: string;
}>();
</script>
