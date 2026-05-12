<template>
  <div class="stack">
    <PageHeader title="Профиль" />
    <LoadingState v-if="isLoading" />
    <ErrorState v-else-if="errorText" :message="errorText" />

    <div v-else class="grid grid-2-cols">
      <div class="panel stack">
        <strong>{{ user?.full_name }}</strong>
        <span class="muted">{{ user?.email }}</span>
        <div class="kv">Роль: {{ userRoleLabel }}</div>
        <div class="kv">Статус: {{ user?.is_active ? 'активен' : 'неактивен' }}</div>
      </div>
      <form class="panel stack" @submit.prevent="onSubmit">
        <h3>Редактирование</h3>
        <label class="stack">Полное имя<Input v-model="fullName" aria-label="Полное имя" /></label>
        <label class="stack">Email<Input v-model="email" type="email" aria-label="Email" /></label>
        <ErrorState v-if="firstError" :message="firstError" />
        <AppButton variant="dark" type="submit" :disabled="updateMutation.isPending.value">{{ updateMutation.isPending.value ? 'Сохраняем...' : 'Сохранить изменения' }}</AppButton>
      </form>
    </div>

    <div v-if="!isLoading && !errorText" class="panel stack">
      <h3>Активные сессии</h3>
      <LoadingState v-if="sessionsLoading" />
      <ErrorState v-else-if="sessionsErrorText" :message="sessionsErrorText" />
      <div v-else-if="sessions.length === 0" class="muted">Сессий пока нет.</div>
      <div v-else class="stack">
        <div v-for="session in sessions" :key="session.id" class="panel stack">
          <div class="kv">Создана: {{ formatDateTimeRu(session.created_at) }}</div>
          <div class="kv">Истекает: {{ formatDateTimeRu(session.expires_at) }}</div>
          <div class="kv">IP: {{ session.ip || "—" }}</div>
          <div class="kv">User-Agent: {{ session.user_agent || "—" }}</div>
          <div class="kv">
            Статус: {{ session.revoked_at ? `отозвана (${formatDateTimeRu(session.revoked_at)})` : "активна" }}
          </div>
          <AppButton
            variant="outline"
            :disabled="Boolean(session.revoked_at) || revokeSessionMutation.isPending.value"
            @click="revokeUserSession(session.id)"
          >
            Отозвать
          </AppButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ErrorState, LoadingState, PageHeader } from "../../components/common";
import AppButton from "../../components/ui/button/AppButton.vue";
import { Input } from "../../components/ui/input";
import { useProfile } from "../../features/profile";
import { formatDateTimeRu } from "../../shared/lib/datetime";

const {
  user,
  isLoading,
  errorText,
  userRoleLabel,
  fullName,
  email,
  firstError,
  updateMutation,
  onSubmit,
  sessions,
  sessionsLoading,
  sessionsErrorText,
  revokeSessionMutation,
  revokeUserSession,
} = useProfile();
</script>
