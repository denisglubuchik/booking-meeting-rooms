<template>
  <RouterView v-if="isPublic" />
  <AppShell v-else>
    <RouterView />
  </AppShell>
  <Toaster />
  <ConfirmDialog />
</template>

<script setup lang="ts">
import { computed } from "vue";
import { RouterView, useRoute } from "vue-router";
import "vue-sonner/style.css";
import AppShell from "./app/layouts/AppShell.vue";
import ConfirmDialog from "./components/ConfirmDialog.vue";
import { Toaster } from "@/components/ui/sonner";

const route = useRoute();
const isPublic = computed(() => Boolean(route.meta.public));
</script>
