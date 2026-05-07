<template>
  <div class="stack">
    <PageHeader
      title="Дашборд"
      description="Быстрый сценарий: выбрать параметры и найти свободную комнату."
    />

    <LoadingState v-if="isLoading" />
    <ErrorState v-else-if="errorText" :message="errorText" />

    <div v-else class="grid">
      <StatCard label="Активные брони" :value="activeBookings" />
      <StatCard label="Свободно сейчас" :value="availableNow" />
      <StatCard label="Офисы" :value="officesCount" />
      <StatCard label="Мои встречи сегодня" :value="todayBookings" />
    </div>

    <div class="panel stack">
      <h3>Быстрый поиск переговорной</h3>
      <div class="grid grid-3-compact">
        <select v-model="quickOfficeId" class="kv" aria-label="Офис для быстрого поиска">
          <option value="">Офис: любой</option>
          <option v-for="office in offices" :key="office.id" :value="office.id">{{ office.name }}</option>
        </select>
        <input v-model="quickDate" class="kv" type="date" aria-label="Дата для быстрого поиска" />
        <div class="row">
          <input v-model="quickStart" class="kv" type="time" aria-label="Время начала для быстрого поиска" />
          <input v-model="quickEnd" class="kv" type="time" aria-label="Время окончания для быстрого поиска" />
        </div>
      </div>
      <div class="row">
        <RouterLink class="button button-dark" :to="{ path: '/find-room', query: quickSearchQuery }">Найти комнату</RouterLink>
        <RouterLink class="button" to="/my-bookings">Мои бронирования</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useQueries } from "@tanstack/vue-query";
import { RouterLink } from "vue-router";
import { ErrorState, LoadingState, PageHeader, StatCard } from "../../components/common";
import { getAvailableRooms, getMyBookings, getOffices, humanizeApiError } from "../../shared/api";
import { isSameDay } from "../../shared/lib/datetime";

const now = new Date();
const oneHourLater = new Date(now.getTime() + 60 * 60 * 1000);

const quickOfficeId = ref("");
const quickDate = ref(todayIsoDate(now));
const quickStart = ref(toTimeInput(now));
const quickEnd = ref(toTimeInput(oneHourLater));
const quickSearchQuery = computed(() => ({
  officeId: quickOfficeId.value || "",
  date: quickDate.value,
  start: quickStart.value,
  end: quickEnd.value,
  source: "dashboard",
}));

function todayIsoDate(d: Date) {
  return d.toISOString().slice(0, 10);
}

function toTimeInput(d: Date) {
  return d.toISOString().slice(11, 16);
}

const queryResults = useQueries({
  queries: [
    { queryKey: ["dashboard-my-bookings"], queryFn: () => getMyBookings() },
    { queryKey: ["dashboard-offices"], queryFn: () => getOffices({ is_active: true }) },
    {
      queryKey: ["dashboard-available-now", now.toISOString(), oneHourLater.toISOString()],
      queryFn: () => getAvailableRooms({ start_time: now.toISOString(), end_time: oneHourLater.toISOString() }),
    },
  ],
});

const bookingsQuery = computed(() => queryResults.value[0]);
const officesQuery = computed(() => queryResults.value[1]);
const availableQuery = computed(() => queryResults.value[2]);

const isLoading = computed(
  () =>
    bookingsQuery.value.isLoading ||
    bookingsQuery.value.isFetching ||
    officesQuery.value.isLoading ||
    officesQuery.value.isFetching ||
    availableQuery.value.isLoading ||
    availableQuery.value.isFetching,
);

const errorText = computed(() => {
  if (bookingsQuery.value.error) return humanizeApiError(bookingsQuery.value.error);
  if (officesQuery.value.error) return humanizeApiError(officesQuery.value.error);
  if (availableQuery.value.error) return humanizeApiError(availableQuery.value.error);
  return "";
});

const bookings = computed(() => bookingsQuery.value.data ?? []);
const offices = computed(() => officesQuery.value.data ?? []);
const available = computed(() => availableQuery.value.data ?? []);

const activeBookings = computed(() => bookings.value.filter((b) => b.status === "created").length);
const todayBookings = computed(() => bookings.value.filter((b) => isSameDay(b.start_time, now)).length);
const officesCount = computed(() => offices.value.length);
const availableNow = computed(() => available.value.length);
</script>
