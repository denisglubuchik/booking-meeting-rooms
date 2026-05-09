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
        <label class="stack auth-label">
          Пароль
          <div class="password-field">
            <Input v-model="password" :type="isPasswordVisible ? 'text' : 'password'" aria-label="Пароль" class="password-input" />
            <button
              type="button"
              class="password-toggle"
              :aria-label="isPasswordVisible ? 'Скрыть пароль' : 'Показать пароль'"
              :title="isPasswordVisible ? 'Скрыть пароль' : 'Показать пароль'"
              @click="isPasswordVisible = !isPasswordVisible"
            >
              <EyeIcon v-if="!isPasswordVisible" class="size-5" />
              <EyeOffIcon v-else class="size-5" />
            </button>
          </div>
        </label>
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
import { ref } from "vue";
import { RouterLink } from "vue-router";
import { EyeIcon, EyeOffIcon } from "lucide-vue-next";
import { ErrorState } from "../../components/common";
import AppButton from "../../components/ui/button/AppButton.vue";
import { Input } from "../../components/ui/input";
import { useRegister } from "../../features/auth";

const { fullName, email, password, firstError, loading, error, success, onSubmit } = useRegister();
const isPasswordVisible = ref(false);
</script>

<style scoped>
.password-field {
  position: relative;
}

.password-input {
  padding-right: 2.75rem;
}

.password-toggle {
  position: absolute;
  top: 50%;
  right: 0.75rem;
  transform: translateY(-50%);
  border: 0;
  background: transparent;
  color: var(--muted);
  padding: 0;
  cursor: pointer;
  line-height: 0;
}

.password-toggle:hover {
  color: var(--text);
}

.password-toggle:focus-visible {
  outline: 2px solid var(--line-strong);
  outline-offset: 2px;
  border-radius: 6px;
}
</style>
