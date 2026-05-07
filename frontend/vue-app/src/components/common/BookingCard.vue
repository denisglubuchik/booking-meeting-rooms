<template>
  <article class="panel stack">
    <div class="row row-between-start">
      <div>
        <strong>{{ title }}</strong>
        <div class="muted">{{ datetimeLabel }}</div>
        <div class="muted">Комната: {{ roomName }}</div>
      </div>
      <slot name="badge" />
    </div>
    <slot />
  </article>
</template>

<script setup lang="ts">
defineProps<{
  title: string;
  datetimeLabel: string;
  roomName: string;
}>();
</script>
