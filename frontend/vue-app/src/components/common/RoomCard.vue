<template>
  <article class="panel stack">
    <img v-if="imageUrl" :src="imageUrl" :alt="`Фото комнаты ${name}`" class="photo-image" />
    <div v-else class="photo"></div>
    <strong>{{ name }} · {{ capacity }} мест</strong>
    <span class="muted">{{ officeName }} · этаж {{ floor }}</span>
    <div class="row">
      <slot name="actions" />
    </div>
  </article>
</template>

<script setup lang="ts">
defineProps<{
  name: string;
  officeName: string;
  floor: number;
  capacity: number;
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
