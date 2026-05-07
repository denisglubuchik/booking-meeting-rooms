<template>
  <article class="panel stack">
    <img v-if="imageUrl" :src="imageUrl" :alt="`Фото офиса ${name}`" class="photo-image" />
    <div v-else class="photo"></div>
    <strong>{{ name }}</strong>
    <span class="muted">{{ city }}, {{ address }}</span>
  </article>
</template>

<script setup lang="ts">
defineProps<{
  name: string;
  city: string;
  address: string;
  imageUrl?: string | null;
}>();
</script>

<style scoped>
.photo-image {
  width: 100%;
  height: 168px;
  object-fit: cover;
  border-radius: 12px;
}
</style>
