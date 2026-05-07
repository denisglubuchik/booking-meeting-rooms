<template>
  <form class="panel admin-filter" @submit.prevent="onSubmit">
    <slot />
  </form>
</template>

<script setup lang="ts">
const emit = defineEmits<{ (e: "submit"): void }>();

function onSubmit() {
  emit("submit");
}
</script>
