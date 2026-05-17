<template>
  <div class="stack">
    <PageHeader title="Главная" description="Текущая и предстоящие брони на сегодня и завтра." />

    <LoadingState v-if="isLoading" />
    <ErrorState v-else-if="errorText" :message="errorText" />
    <EmptyState
      v-else-if="!hasTodayBookings"
      title="Нет предстоящих бронирований"
      description="Сейчас нет активных и предстоящих встреч на сегодня и завтра."
    />
    <div v-else class="stack">
      <section v-if="todayBookings.created.length > 0" class="stack">
        <h3>Активные сейчас</h3>
        <BookingCard
          v-for="booking in todayBookings.created"
          :key="booking.id"
          :title="booking.title || 'Встреча без названия'"
          :datetime-label="`${formatDateRu(booking.start_time)} · ${formatTimeRu(booking.start_time)}-${formatTimeRu(booking.end_time)}`"
          :room-name="roomName(booking.room_id)"
        >
          <template #badge>
            <StatusBadge :status="booking.status" />
          </template>
          <div class="row">
            <RouterLink :to="`/bookings/${booking.id}`" class="button">Подробнее</RouterLink>
          </div>
        </BookingCard>
      </section>

      <section class="stack">
        <h3>Предстоящие</h3>
        <div v-if="todayBookings.completed.length === 0" class="panel muted">Нет предстоящих бронирований.</div>
        <BookingCard
          v-for="booking in todayBookings.completed"
          :key="booking.id"
          :title="booking.title || 'Встреча без названия'"
          :datetime-label="`${formatDateRu(booking.start_time)} · ${formatTimeRu(booking.start_time)}-${formatTimeRu(booking.end_time)}`"
          :room-name="roomName(booking.room_id)"
        >
          <template #badge>
            <StatusBadge :status="booking.status" />
          </template>
          <div class="row">
            <RouterLink :to="`/bookings/${booking.id}`" class="button">Подробнее</RouterLink>
          </div>
        </BookingCard>
      </section>

      <section class="stack">
        <h3>Отмененные (предстояли)</h3>
        <div v-if="todayBookings.cancelled.length === 0" class="panel muted">Нет отмененных предстоящих бронирований.</div>
        <BookingCard
          v-for="booking in todayBookings.cancelled"
          :key="booking.id"
          :title="booking.title || 'Встреча без названия'"
          :datetime-label="`${formatDateRu(booking.start_time)} · ${formatTimeRu(booking.start_time)}-${formatTimeRu(booking.end_time)}`"
          :room-name="roomName(booking.room_id)"
        >
          <template #badge>
            <StatusBadge :status="booking.status" />
          </template>
          <div class="row">
            <RouterLink :to="`/bookings/${booking.id}`" class="button">Подробнее</RouterLink>
          </div>
        </BookingCard>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import dayjs from "dayjs";
import { useQuery } from "@tanstack/vue-query";
import { RouterLink } from "vue-router";
import { BookingCard, EmptyState, ErrorState, LoadingState, PageHeader, StatusBadge } from "../../components/common";
import { getMyBookings, getRooms, humanizeApiError, queryKeys } from "../../shared/api";
import { formatDateRu, formatTimeRu } from "../../shared/lib/datetime";

const dashboardBookingFilters = computed(() => ({
  start_time_gte: dayjs().startOf("day").toISOString(),
  end_time_lte: dayjs().add(1, "day").endOf("day").toISOString(),
  sort_by: "start_time" as const,
  sort_order: "asc" as const,
  limit: 100,
  offset: 0,
}));

const bookingsQuery = useQuery({
  queryKey: computed(() => queryKeys.myBookingsList(dashboardBookingFilters.value)),
  queryFn: () => getMyBookings(dashboardBookingFilters.value),
  refetchOnMount: true,
});
const roomsQuery = useQuery({
  queryKey: queryKeys.roomsLookup,
  queryFn: () => getRooms(),
});

const isLoading = computed(
  () =>
    bookingsQuery.isLoading.value ||
    bookingsQuery.isFetching.value ||
    roomsQuery.isLoading.value ||
    roomsQuery.isFetching.value,
);

const errorText = computed(() => {
  if (bookingsQuery.error.value) return humanizeApiError(bookingsQuery.error.value);
  if (roomsQuery.error.value) return humanizeApiError(roomsQuery.error.value);
  return "";
});

const bookings = computed(() => bookingsQuery.data.value ?? []);
const rooms = computed(() => roomsQuery.data.value ?? []);
const now = computed(() => dayjs());
const endOfTomorrow = computed(() => dayjs().add(1, "day").endOf("day"));
const windowBookings = computed(() =>
  bookings.value.filter((booking) => {
    const start = dayjs(booking.start_time);
    const end = dayjs(booking.end_time);
    return end.isAfter(now.value) && start.isBefore(endOfTomorrow.value);
  }),
);

const todayBookings = computed(() => ({
  created: windowBookings.value.filter(
    (booking) =>
      booking.status === "created" &&
      dayjs(booking.start_time).isBefore(now.value) &&
      dayjs(booking.end_time).isAfter(now.value),
  ),
  completed: windowBookings.value.filter(
    (booking) =>
      booking.status === "created" &&
      (dayjs(booking.start_time).isAfter(now.value) || dayjs(booking.start_time).isSame(now.value)),
  ),
  cancelled: windowBookings.value.filter((booking) => booking.status === "cancelled"),
}));

const hasTodayBookings = computed(() => windowBookings.value.length > 0);

function roomName(roomId: string) {
  return rooms.value.find((room) => room.id === roomId)?.name || roomId;
}
</script>
