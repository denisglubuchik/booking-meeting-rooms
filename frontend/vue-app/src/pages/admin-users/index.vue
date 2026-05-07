<template>
  <div class="stack">
    <PageHeader title="Админ: пользователи" />

    <FilterBar @submit="applyFilters">
      <div class="admin-field admin-field-full">
        <Label>Поиск пользователя</Label>
        <Input v-model="userSearch" placeholder="Имя или email" aria-label="Поиск пользователей" />
      </div>

      <div class="admin-field admin-col-3">
        <Label>Роль</Label>
        <Select :model-value="roleFilterValue" @update:model-value="roleFilterValue = String($event)">
          <SelectTrigger aria-label="Фильтр по роли">
            <SelectValue placeholder="Все роли" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="__all">Все роли</SelectItem>
            <SelectItem value="employee">сотрудник</SelectItem>
            <SelectItem value="admin">администратор</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div class="admin-field admin-col-3">
        <Label>Статус</Label>
        <Select :model-value="activeFilterValue" @update:model-value="activeFilterValue = String($event)">
          <SelectTrigger aria-label="Фильтр по статусу пользователя">
            <SelectValue placeholder="Любой статус" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="__all">Любой статус</SelectItem>
            <SelectItem value="true">Только активные</SelectItem>
            <SelectItem value="false">Только неактивные</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div class="admin-field admin-col-3">
        <Label>Создан после</Label>
        <Input v-model="draftFilters.created_from" type="date" title="Создан после" aria-label="Создан после" />
      </div>

      <div class="admin-field admin-col-3">
        <Label>Создан до</Label>
        <Input v-model="draftFilters.created_to" type="date" title="Создан до" aria-label="Создан до" />
      </div>

      <div class="admin-actions">
        <AppButton variant="dark" type="submit" :disabled="isBusy">{{ isBusy ? 'Загрузка...' : 'Применить' }}</AppButton>
        <AppButton type="button" :disabled="isBusy" @click="resetFilters">Сбросить</AppButton>
      </div>
    </FilterBar>
    <ErrorState v-if="filterErrors.created_to" :message="String(filterErrors.created_to)" />

    <LoadingState v-if="isLoading" />
    <ErrorState v-else-if="errorText" :message="errorText" />
    <EmptyState v-else-if="filteredUsers.length === 0" title="Пользователи не найдены" />
    <DataTable v-else :columns="['Имя', 'Email', 'Роль', 'Создан', 'Статус', 'Действия']">
      <TableRow v-for="user in filteredUsers" :key="user.id">
        <TableCell>{{ user.full_name }}</TableCell>
        <TableCell>{{ user.email }}</TableCell>
        <TableCell>{{ roleLabel(user.role) }}</TableCell>
        <TableCell>{{ formatCreatedAt(user.created_at) }}</TableCell>
        <TableCell><StatusBadge :status="user.is_active ? 'active' : 'inactive'" :label="user.is_active ? 'активен' : 'неактивен'" /></TableCell>
        <TableCell>
          <div class="admin-users-actions">
            <AppButton :disabled="isBusy" @click="toggleRole(user)">{{ isBusy ? 'Подождите...' : (user.role === 'admin' ? 'Сделать сотрудником' : 'Сделать администратором') }}</AppButton>
            <AppButton :disabled="isBusy" @click="toggleActive(user)">{{ isBusy ? 'Подождите...' : (user.is_active ? 'Деактивировать' : 'Активировать') }}</AppButton>
          </div>
        </TableCell>
      </TableRow>
    </DataTable>

    <div class="admin-pagination">
      <div class="admin-pagination-left">
        <div class="admin-pagination-size">
          <span class="muted">На странице</span>
          <Select :model-value="pageSizeValue" @update:model-value="pageSizeValue = String($event)">
            <SelectTrigger aria-label="Количество элементов на странице">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="10">10</SelectItem>
              <SelectItem value="25">25</SelectItem>
              <SelectItem value="50">50</SelectItem>
              <SelectItem value="100">100</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      <div class="admin-pagination-center">
        <AppButton :disabled="isLoading || !hasPrevPage" @click="prevPage">Назад</AppButton>
        <span class="muted admin-pagination-page">Страница {{ pageLabel }}</span>
        <AppButton :disabled="isLoading || !hasNextPage" @click="nextPage">Дальше</AppButton>
      </div>
      <div class="admin-pagination-right">
        <span class="muted admin-pagination-range">{{ pageRangeLabel }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { DataTable, EmptyState, ErrorState, FilterBar, LoadingState, PageHeader, StatusBadge } from "../../components/common";
import { TableCell, TableRow } from "../../components/ui/table";
import AppButton from "../../components/ui/button/AppButton.vue";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../components/ui/select";
import { useAdminUsers } from "../../features/users";

const {
  draftFilters,
  filterErrors,
  roleFilterValue,
  activeFilterValue,
  users,
  hasNextPage,
  hasPrevPage,
  pageLabel,
  pageRangeLabel,
  pageSizeValue,
  isLoading,
  isBusy,
  errorText,
  applyFilters,
  resetFilters,
  nextPage,
  prevPage,
  formatCreatedAt,
  roleLabel,
  toggleRole,
  toggleActive,
} = useAdminUsers();

const userSearch = ref("");

const filteredUsers = computed(() => {
  const q = userSearch.value.trim().toLowerCase();
  if (!q) return users.value;
  return users.value.filter((user) => `${user.full_name} ${user.email}`.toLowerCase().includes(q));
});
</script>

<style scoped>
.admin-users-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  min-width: 0;
}

.admin-users-actions :deep(button) {
  white-space: normal;
}
</style>
