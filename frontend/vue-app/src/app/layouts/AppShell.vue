<template>
  <div class="app-bg">
    <a href="#main-content" class="skip-link">Перейти к содержимому</a>
    <div class="container">
      <aside class="sidebar card">
        <div class="row row-between-start">
          <h1>RoomFlow</h1>
          <Button
            variant="outline"
            class="sidebar-toggle"
            :aria-expanded="String(navOpen)"
            aria-controls="main-nav"
            aria-label="Переключить навигацию"
            @click="navOpen = !navOpen"
          >
            Меню
          </Button>
        </div>
        <nav id="main-nav" :class="{ 'sidebar-nav-hidden': !navOpen }">
          <RouterLink to="/">Главная</RouterLink>
          <RouterLink to="/offices">Офисы</RouterLink>
          <RouterLink to="/rooms">Комнаты</RouterLink>
          <RouterLink to="/find-room">Найти комнату</RouterLink>
          <RouterLink to="/my-bookings">Мои бронирования</RouterLink>
          <RouterLink to="/profile">Профиль</RouterLink>
          <template v-if="auth.role === 'admin'">
            <RouterLink to="/admin/offices">Админ: офисы</RouterLink>
            <RouterLink to="/admin/rooms">Админ: комнаты</RouterLink>
            <RouterLink to="/admin/bookings">Админ: бронирования</RouterLink>
            <RouterLink to="/admin/users">Админ: пользователи</RouterLink>
          </template>
        </nav>
      </aside>
      <main id="main-content" class="content" tabindex="-1">
        <header class="card topbar">
          <div>
            <strong>{{ auth.fullName || 'Гость' }}</strong>
            <span class="muted"> · {{ auth.role }}</span>
          </div>
          <div class="row">
            <Button variant="outline" aria-label="Выйти из аккаунта" @click="onLogout">Выйти</Button>
          </div>
        </header>
        <section class="card page"><slot /></section>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { RouterLink } from "vue-router";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../../features/auth/store";
import { Button } from "@/components/ui/button";

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();
const navOpen = ref(true);

onMounted(() => {
  if (typeof window === "undefined") return;
  navOpen.value = !window.matchMedia("(max-width: 1050px)").matches;
});

watch(
  () => route.fullPath,
  () => {
    if (typeof window === "undefined") return;
    if (window.matchMedia("(max-width: 1050px)").matches) {
      navOpen.value = false;
    }
  },
);

function onLogout() {
  auth.logout();
  void router.replace("/login");
}
</script>
