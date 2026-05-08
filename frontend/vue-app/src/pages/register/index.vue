<template>
  <div class="stack auth-shell">
    <div class="grid grid-2-cols auth-grid">
      <div class="panel auth-side">
        <p class="auth-eyebrow">Booking</p>
        <h3 class="auth-title">Создайте рабочий аккаунт</h3>
        <p class="muted auth-copy">После регистрации вы сможете искать и бронировать переговорные.</p>
      </div>
      <form class="panel stack auth-form" @submit.prevent="onSubmit">
        <label class="stack auth-label">Полное имя<Input v-model="fullName" aria-label="Полное имя" /></label>
        <label class="stack auth-label">Email<Input v-model="email" type="email" aria-label="Email" /></label>
        <label class="stack auth-label">Пароль<Input v-model="password" type="password" aria-label="Пароль" /></label>
        <ErrorState v-if="firstError" :message="firstError" />
        <ErrorState v-if="error" :message="error" />
        <p v-if="success" class="muted text-success">{{ success }}</p>
        <AppButton variant="dark" type="submit" :disabled="loading">{{ loading ? 'Создаем...' : 'Зарегистрироваться' }}</AppButton>
        <RouterLink to="/login" class="muted auth-link">Уже есть аккаунт? Войти</RouterLink>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from "vue-router";
import { ErrorState } from "../../components/common";
import AppButton from "../../components/ui/button/AppButton.vue";
import { Input } from "../../components/ui/input";
import { useRegister } from "../../features/auth";

const { fullName, email, password, firstError, loading, error, success, onSubmit } = useRegister();
</script>
