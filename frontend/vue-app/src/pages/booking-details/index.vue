<template>
  <div class="stack">
    <PageHeader title="Детали бронирования" />
    <LoadingState v-if="isLoading" />
    <ErrorState v-else-if="errorText" :message="errorText" />
    <EmptyState
      v-else-if="!details || !booking || !room"
      title="Бронирование не найдено"
      description="Проверьте ссылку или вернитесь к списку бронирований."
    >
      <template #actions>
        <RouterLink to="/my-bookings" class="button">К моим бронированиям</RouterLink>
      </template>
    </EmptyState>
    <div v-else class="grid grid-2-cols booking-details-grid">
      <div class="stack booking-details-main">
        <div class="panel stack">
          <strong>{{ booking.title || "Встреча без названия" }}</strong>
          <div class="row">
            <StatusBadge :status="booking.status" />
            <span class="kv">{{ formatDate(booking.start_time) }}</span>
            <span class="kv">{{ formatTime(booking.start_time) }}-{{ formatTime(booking.end_time) }}</span>
          </div>
          <div class="kv">Комната: {{ room.name }}</div>
          <div class="kv">Этаж: {{ room.floor }}</div>
          <div class="kv">Вместимость: {{ room.capacity }}</div>
          <div class="kv">Офис: {{ officeTitle }}</div>
          <div class="kv">Адрес: {{ officeAddress }}</div>
          <div class="kv">Оснащение: {{ room.equipment.length ? room.equipment.join(", ") : "-" }}</div>
        </div>

        <div v-if="canManageBooking" class="panel stack">
          <h3>Управление бронированием</h3>
          <div class="row">
            <button class="button" :disabled="isMutating" @click="startReschedule">Перенести</button>
            <button class="button" :disabled="isMutating" @click="startChangeRoom">Сменить комнату</button>
            <button class="button" :disabled="isMutating" @click="cancelCurrentBooking">
              {{ isMutating ? "Подождите..." : "Отменить" }}
            </button>
          </div>

          <div v-if="selectedReschedule" class="panel stack">
            <strong>Перенос бронирования</strong>
            <div class="row">
              <Input v-model="rescheduleDraft.date" type="date" aria-label="Новая дата бронирования" />
              <Input v-model="rescheduleDraft.start" type="time" aria-label="Новое время начала" />
              <Input v-model="rescheduleDraft.end" type="time" aria-label="Новое время окончания" />
            </div>
            <ErrorState v-if="rescheduleError" :message="rescheduleError" />
            <div class="row">
              <button class="button button-dark" :disabled="isMutating" @click="submitReschedule">
                {{ isMutating ? "Сохраняем..." : "Сохранить" }}
              </button>
              <button class="button" :disabled="isMutating" @click="cancelReschedule">Отмена</button>
            </div>
          </div>

          <div v-if="selectedRoomChange" class="panel stack">
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
                  <SelectItem v-for="candidate in availableRoomsForChange" :key="candidate.id" :value="candidate.id">
                    {{ candidate.name }} · этаж {{ candidate.floor }} · {{ candidate.capacity }} мест
                  </SelectItem>
                </SelectContent>
              </Select>
              <div class="row">
                <button class="button button-dark" :disabled="isMutating || !selectedNewRoomId" @click="submitChangeRoom">
                  {{ isMutating ? "Сохраняем..." : "Сменить комнату" }}
                </button>
                <button class="button" :disabled="isMutating" @click="cancelChangeRoom">Отмена</button>
              </div>
            </template>
          </div>
        </div>

        <div class="panel stack">
        <h3>Участники</h3>
        <div v-if="participants.length === 0" class="muted">Участники не найдены.</div>
        <div v-for="participant in participants" :key="participant.user_id" class="booking-participant-row">
          <div class="stack gap-1">
            <strong>{{ participant.full_name }}</strong>
            <span class="muted">{{ participant.email }}</span>
          </div>
          <div class="booking-participant-actions">
            <span class="kv">{{ participant.role === "organizer" ? "организатор" : "участник" }}</span>
            <button
              v-if="canManageParticipants && participant.role !== 'organizer'"
              class="button"
              :disabled="isMutating"
              @click="removeParticipant(participant.user_id, participant.full_name, participant.role)"
            >
              Удалить
            </button>
          </div>
        </div>

        <div v-if="canManageParticipants" class="panel stack">
          <h4>Добавить участника</h4>
          <Input
            v-model="userSearch"
            placeholder="Введите имя или email (минимум 2 символа)"
            aria-label="Поиск пользователя для добавления"
          />
          <ErrorState v-if="lookupErrorText" :message="lookupErrorText" />
          <p v-else-if="lookupLoading" class="muted">Ищем пользователей...</p>
          <div v-else-if="userSearch.trim().length >= 2" class="stack">
            <button
              v-for="user in suggestedUsers"
              :key="user.id"
              type="button"
              class="button booking-user-option"
              :class="{ 'booking-user-option-active': selectedUserId === user.id }"
              @click="selectUser(user.id)"
            >
              <span>{{ user.full_name }}</span>
              <span class="muted">{{ user.email }}</span>
            </button>
            <p v-if="suggestedUsers.length === 0" class="muted">Подходящих пользователей не найдено.</p>
          </div>
          <button class="button button-dark" :disabled="!selectedUserId || isMutating" @click="addSelectedUser">
            {{ isMutating ? "Сохраняем..." : "Добавить участника" }}
          </button>
        </div>
      </div>
      </div>

      <div class="panel stack booking-image-panel">
        <img v-if="room.image_url" :src="room.image_url" :alt="`Фото комнаты ${room.name}`" class="booking-room-photo" />
        <div v-else class="photo"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { RouterLink } from "vue-router";
import { EmptyState, ErrorState, LoadingState, PageHeader, StatusBadge } from "../../components/common";
import { Input } from "../../components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../components/ui/select";
import { useBookingDetails } from "../../features/bookings";
import { formatDateRu, formatTimeRu } from "../../shared/lib/datetime";

const {
  details,
  booking,
  room,
  office,
  participants,
  canManageParticipants,
  canManageBooking,
  userSearch,
  selectedUserId,
  suggestedUsers,
  selectedReschedule,
  rescheduleDraft,
  rescheduleError,
  selectedRoomChange,
  selectedNewRoomId,
  availableRoomsForChange,
  availableRoomsForChangeQuery,
  roomChangeError,
  isLoading,
  lookupLoading,
  isMutating,
  errorText,
  lookupErrorText,
  selectUser,
  addSelectedUser,
  removeParticipant,
  startReschedule,
  cancelReschedule,
  submitReschedule,
  startChangeRoom,
  cancelChangeRoom,
  submitChangeRoom,
  cancelCurrentBooking,
} = useBookingDetails();

function formatDate(value: string) {
  return formatDateRu(value);
}

function formatTime(value: string) {
  return formatTimeRu(value);
}

const officeTitle = computed(() => (office.value ? office.value.name : "Офис"));
const officeAddress = computed(() => {
  if (!office.value) return "-";
  return `${office.value.city}, ${office.value.address}`;
});
</script>

<style scoped>
.booking-room-photo {
  width: 100%;
  height: 420px;
  object-fit: cover;
  border-radius: 12px;
}

.booking-details-grid {
  align-items: start;
}

.booking-details-main {
  order: 1;
}

.booking-image-panel {
  order: 2;
  position: sticky;
  top: 16px;
}

.booking-participant-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  padding: 10px 12px;
  border: 1px solid var(--line);
  border-radius: 12px;
  background: #fffdf9;
}

.booking-participant-actions {
  margin-left: auto;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
  flex: 0 0 auto;
}

.booking-user-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  text-align: left;
  width: 100%;
}

.booking-user-option-active {
  border-color: var(--line-strong);
  background: #f8f2ea;
}

.gap-1 {
  gap: 4px;
}

@media (max-width: 900px) {
  .booking-image-panel {
    position: static;
    top: auto;
  }

  .booking-room-photo {
    height: 300px;
  }
}
</style>
