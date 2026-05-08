<template>
  <div class="stack">
    <PageHeader title="Админ: история бронирований" />

    <FilterBar @submit="applyFilters">
      <div class="admin-field admin-col-3">
        <Label>Действие</Label>
        <Select :model-value="actionFilterValue" @update:model-value="actionFilterValue = String($event)">
          <SelectTrigger aria-label="Фильтр по действию">
            <SelectValue placeholder="Все действия" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="__all">Все действия</SelectItem>
            <SelectItem value="created">создано</SelectItem>
            <SelectItem value="rescheduled">перенесено</SelectItem>
            <SelectItem value="updated">обновлено</SelectItem>
            <SelectItem value="cancelled">отменено</SelectItem>
            <SelectItem value="completed">завершено</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div class="admin-field admin-col-4">
        <Label>Исполнитель</Label>
        <Select :model-value="userFilterValue" @update:model-value="userFilterValue = String($event)">
          <SelectTrigger aria-label="Фильтр по исполнителю">
            <SelectValue placeholder="Все пользователи" />
          </SelectTrigger>
          <SelectContent>
            <div class="p-1">
              <Input
                v-model="userSearch"
                placeholder="Поиск пользователя..."
                aria-label="Поиск пользователя"
                @keydown.stop
                @keypress.stop
                @keyup.stop
              />
            </div>
            <SelectItem value="__all">Все пользователи</SelectItem>
            <SelectItem v-for="user in filteredUsers" :key="user.id" :value="user.id">{{ user.full_name }}</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div class="admin-field admin-col-5">
        <Label>Booking ID</Label>
        <Input v-model="draftFilters.booking_id" placeholder="UUID бронирования" aria-label="Фильтр по booking id" />
      </div>

      <div class="admin-field admin-col-2">
        <Label>Период от</Label>
        <Input v-model="draftFilters.start_date" type="date" title="Начало периода" aria-label="Начало периода" />
      </div>

      <div class="admin-field admin-col-2">
        <Label>Период до</Label>
        <Input v-model="draftFilters.end_date" type="date" title="Конец периода" aria-label="Конец периода" />
      </div>

      <div class="admin-actions">
        <AppButton variant="dark" type="submit" :disabled="isLoading">{{ isLoading ? "Загрузка..." : "Применить" }}</AppButton>
        <AppButton type="button" :disabled="isLoading" @click="resetFilters">Сбросить</AppButton>
      </div>
    </FilterBar>

    <ErrorState v-if="filterErrors.end_date" :message="String(filterErrors.end_date)" />
    <LoadingState v-if="isLoading" />
    <ErrorState v-else-if="errorText" :message="errorText" />
    <EmptyState v-else-if="historyItems.length === 0" title="История изменений не найдена" />
    <DataTable v-else :columns="['Дата', 'Действие', 'Booking ID', 'Исполнитель', 'Описание']">
      <TableRow v-for="item in historyItems" :key="item.id">
        <TableCell>{{ fmt(item.created_at) }}</TableCell>
        <TableCell><StatusBadge :status="item.action" :label="actionLabel(item.action)" /></TableCell>
        <TableCell class="font-mono text-xs">{{ item.booking_id }}</TableCell>
        <TableCell>{{ userName(item.performed_by) }}</TableCell>
        <TableCell>{{ item.details || "-" }}</TableCell>
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
import { useAdminBookingHistory } from "../../features/bookings/useAdminBookingHistory";

const {
  draftFilters,
  filterErrors,
  actionFilterValue,
  userFilterValue,
  users,
  historyItems,
  hasNextPage,
  hasPrevPage,
  pageLabel,
  pageRangeLabel,
  pageSizeValue,
  isLoading,
  errorText,
  userName,
  actionLabel,
  fmt,
  applyFilters,
  resetFilters,
  nextPage,
  prevPage,
} = useAdminBookingHistory();

const userSearch = ref("");

const filteredUsers = computed(() => {
  const q = userSearch.value.trim().toLowerCase();
  if (!q) return users.value;
  return users.value.filter((user) => `${user.full_name} ${user.email}`.toLowerCase().includes(q));
});
</script>
