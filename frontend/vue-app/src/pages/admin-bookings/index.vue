<template>
  <div class="stack">
    <PageHeader title="Админ: бронирования" />

    <FilterBar @submit="applyFilters">
      <div class="admin-field admin-col-3">
        <Label>Статус</Label>
        <Select :model-value="statusFilterValue" @update:model-value="statusFilterValue = String($event)">
          <SelectTrigger aria-label="Фильтр по статусу бронирования">
            <SelectValue placeholder="Все статусы" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="__all">Все статусы</SelectItem>
            <SelectItem value="created">активно</SelectItem>
            <SelectItem value="cancelled">отменено</SelectItem>
            <SelectItem value="completed">завершено</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div class="admin-field admin-col-4">
        <Label>Пользователь</Label>
        <Select :model-value="userFilterValue" @update:model-value="userFilterValue = String($event)">
          <SelectTrigger aria-label="Фильтр по пользователю">
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
        <Label>Комната</Label>
        <Select :model-value="roomFilterValue" @update:model-value="roomFilterValue = String($event)">
          <SelectTrigger aria-label="Фильтр по комнате">
            <SelectValue placeholder="Все комнаты" />
          </SelectTrigger>
          <SelectContent>
            <div class="p-1">
              <Input
                v-model="roomSearch"
                placeholder="Поиск комнаты..."
                aria-label="Поиск комнаты"
                @keydown.stop
                @keypress.stop
                @keyup.stop
              />
            </div>
            <SelectItem value="__all">Все комнаты</SelectItem>
            <template v-for="group in groupedRooms" :key="group.officeId">
              <SelectGroup>
                <SelectLabel>{{ group.officeName }}</SelectLabel>
                <SelectItem v-for="room in group.rooms" :key="room.id" :value="room.id">{{ room.name }}</SelectItem>
              </SelectGroup>
            </template>
          </SelectContent>
        </Select>
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
        <AppButton variant="dark" type="submit" :disabled="isLoading">{{ isLoading ? 'Загрузка...' : 'Применить' }}</AppButton>
        <AppButton type="button" :disabled="isLoading" @click="resetFilters">Сбросить</AppButton>
      </div>
    </FilterBar>

    <ErrorState v-if="filterErrors.end_date" :message="String(filterErrors.end_date)" />
    <LoadingState v-if="isLoading" />
    <ErrorState v-else-if="errorText" :message="errorText" />
    <EmptyState v-else-if="bookings.length === 0" title="Бронирования не найдены" />
    <DataTable v-else :columns="['Встреча', 'Пользователь', 'Комната', 'Начало', 'Окончание', 'Статус', 'Действия']">
      <TableRow v-for="booking in bookings" :key="booking.id">
        <TableCell>{{ booking.title || 'Без названия' }}</TableCell>
        <TableCell>{{ userName(booking.created_by) }}</TableCell>
        <TableCell>{{ roomName(booking.room_id) }}</TableCell>
        <TableCell>{{ fmt(booking.start_time) }}</TableCell>
        <TableCell>{{ fmt(booking.end_time) }}</TableCell>
        <TableCell><StatusBadge :status="booking.status" :label="statusLabel(booking.status)" /></TableCell>
        <TableCell>
          <RouterLink :to="`/bookings/${booking.id}`" class="button">Открыть</RouterLink>
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
import { RouterLink } from "vue-router";
import { DataTable, EmptyState, ErrorState, FilterBar, LoadingState, PageHeader, StatusBadge } from "../../components/common";
import { TableCell, TableRow } from "../../components/ui/table";
import AppButton from "../../components/ui/button/AppButton.vue";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";
import { Select, SelectContent, SelectGroup, SelectItem, SelectLabel, SelectTrigger, SelectValue } from "../../components/ui/select";
import { useAdminBookings } from "../../features/bookings";
import { useAdminOffices } from "../../features/offices";
import type { Room } from "../../shared/types/api";

const {
  draftFilters,
  filterErrors,
  statusFilterValue,
  userFilterValue,
  roomFilterValue,
  users,
  rooms,
  bookings,
  hasNextPage,
  hasPrevPage,
  pageLabel,
  pageRangeLabel,
  pageSizeValue,
  isLoading,
  errorText,
  fmt,
  statusLabel,
  userName,
  roomName,
  applyFilters,
  resetFilters,
  nextPage,
  prevPage,
} = useAdminBookings();
const { offices } = useAdminOffices();

const userSearch = ref("");
const roomSearch = ref("");

const filteredUsers = computed(() => {
  const q = userSearch.value.trim().toLowerCase();
  if (!q) return users.value;
  return users.value.filter((user) => `${user.full_name} ${user.email}`.toLowerCase().includes(q));
});

const filteredRooms = computed(() => {
  const q = roomSearch.value.trim().toLowerCase();
  if (!q) return rooms.value;
  return rooms.value.filter((room) => room.name.toLowerCase().includes(q));
});

const groupedRooms = computed(() => {
  const officeMap = new Map(offices.value.map((office) => [office.id, office.name]));
  const groups = new Map<string, { officeId: string; officeName: string; rooms: Room[] }>();

  for (const room of filteredRooms.value) {
    const officeId = room.office_id || "__unknown";
    const officeName = officeMap.get(officeId) || "Офис не указан";
    const existing = groups.get(officeId);
    if (existing) {
      existing.rooms.push(room);
      continue;
    }
    groups.set(officeId, { officeId, officeName, rooms: [room] });
  }

  return Array.from(groups.values()).sort((a, b) => a.officeName.localeCompare(b.officeName, "ru"));
});
</script>
