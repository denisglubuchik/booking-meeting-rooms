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

          <div v-if="booking.status === 'created'" class="row">
            <AppButton :disabled="isMutating" @click="startReschedule(booking.id)">Перенести</AppButton>
            <AppButton :disabled="isMutating" @click="startChangeRoom(booking.id)">Сменить комнату</AppButton>
            <AppButton :disabled="isMutating" @click="onCancel(booking.id)">
              {{ isMutating ? 'Подождите...' : 'Отменить' }}
            </AppButton>
          </div>

          <div v-if="selectedRescheduleBookingId === booking.id" class="panel stack">
            <strong>Перенос бронирования</strong>
            <div class="row">
              <Input v-model="rescheduleDraft.date" type="date" aria-label="Новая дата бронирования" />
              <Input v-model="rescheduleDraft.start" type="time" aria-label="Новое время начала" />
              <Input v-model="rescheduleDraft.end" type="time" aria-label="Новое время окончания" />
            </div>
            <ErrorState v-if="rescheduleError" :message="rescheduleError" />
            <div class="row">
              <AppButton variant="dark" :disabled="isMutating" @click="submitReschedule">
                {{ isMutating ? 'Сохраняем...' : 'Сохранить' }}
              </AppButton>
              <AppButton :disabled="isMutating" @click="cancelReschedule">Отмена</AppButton>
            </div>
          </div>

          <div v-if="selectedRoomChangeBookingId === booking.id" class="panel stack">
            <strong>Выбор новой комнаты</strong>
            <p class="muted">
              Интервал: {{ formatDate(booking.start_time) }} · {{ formatTime(booking.start_time) }}-{{ formatTime(booking.end_time) }}
            </p>
            <p v-if="availableRoomsForChangeQuery.isLoading.value || availableRoomsForChangeQuery.isFetching.value" class="muted">
              Ищем свободные комнаты...
            </p>
            <ErrorState v-else-if="roomChangeError" :message="roomChangeError" />
            <p v-else-if="availableRoomsForChange.length === 0" class="muted">
              Для этого времени нет других свободных комнат.
            </p>
            <template v-else>
              <Select :model-value="selectedNewRoomId" @update:model-value="selectedNewRoomId = String($event)">
                <SelectTrigger class="w-full" aria-label="Выбор новой комнаты">
                  <SelectValue placeholder="Выберите новую комнату" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem v-for="room in availableRoomsForChange" :key="room.id" :value="room.id">
                    {{ room.name }} · этаж {{ room.floor }} · {{ room.capacity }} мест
                  </SelectItem>
                </SelectContent>
              </Select>
              <div class="row">
                <AppButton variant="dark" :disabled="isMutating || !selectedNewRoomId" @click="submitChangeRoom">
                  {{ isMutating ? 'Сохраняем...' : 'Сменить комнату' }}
                </AppButton>
                <AppButton :disabled="isMutating" @click="cancelChangeRoom">Отмена</AppButton>
              </div>
            </template>
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
        </BookingCard>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import AppButton from "../../components/ui/button/AppButton.vue";
import { Input } from "../../components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../components/ui/select";
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
  isMutating,
  onCancel,
  selectedRescheduleBookingId,
  rescheduleDraft,
  rescheduleError,
  startReschedule,
  cancelReschedule,
  submitReschedule,
  selectedRoomChangeBookingId,
  availableRoomsForChange,
  availableRoomsForChangeQuery,
  selectedNewRoomId,
  roomChangeError,
  startChangeRoom,
  cancelChangeRoom,
  submitChangeRoom,
} = useMyBookings();
</script>
