<template>
  <div class="stack">
    <PageHeader title="Мои бронирования" />
    <LoadingState v-if="isLoading" />
    <ErrorState v-else-if="errorText" :message="errorText" />
    <EmptyState
      v-else-if="!hasBookings"
      title="У вас пока нет бронирований"
      description="Найдите свободную комнату и создайте первую встречу."
    />
    <div v-else class="stack">
      <section class="stack">
        <h3>Предстоящие</h3>
        <div v-if="groupedBookings.upcoming.length === 0" class="panel muted">Нет предстоящих бронирований.</div>
        <BookingCard
          v-for="booking in groupedBookings.upcoming"
          :key="booking.id"
          :title="booking.title || 'Встреча без названия'"
          :datetime-label="`${formatDate(booking.start_time)} · ${formatTime(booking.start_time)}-${formatTime(booking.end_time)}`"
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
        <h3>Прошедшие</h3>
        <div v-if="groupedBookings.past.length === 0" class="panel muted">Нет прошедших бронирований.</div>
        <BookingCard
          v-for="booking in groupedBookings.past"
          :key="booking.id"
          :title="booking.title || 'Встреча без названия'"
          :datetime-label="`${formatDate(booking.start_time)} · ${formatTime(booking.start_time)}-${formatTime(booking.end_time)}`"
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
        <h3>Отмененные</h3>
        <div v-if="groupedBookings.cancelled.length === 0" class="panel muted">Нет отмененных бронирований.</div>
        <BookingCard
          v-for="booking in groupedBookings.cancelled"
          :key="booking.id"
          :title="booking.title || 'Встреча без названия'"
          :datetime-label="`${formatDate(booking.start_time)} · ${formatTime(booking.start_time)}-${formatTime(booking.end_time)}`"
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
import { RouterLink } from "vue-router";
import { BookingCard, EmptyState, ErrorState, LoadingState, PageHeader, StatusBadge } from "../../components/common";
import { useMyBookings } from "../../features/bookings";

const {
  groupedBookings,
  hasBookings,
  isLoading,
  errorText,
  formatDate,
  formatTime,
  roomName,
} = useMyBookings();
</script>
