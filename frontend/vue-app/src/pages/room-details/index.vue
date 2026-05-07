<template>
  <div class="stack">
    <PageHeader title="Детали переговорной" />
    <LoadingState v-if="isLoading" />
    <ErrorState v-else-if="errorText" :message="errorText" />
    <EmptyState
      v-else-if="!room"
      title="Комната не найдена"
      description="Проверьте ссылку или вернитесь к списку комнат."
    >
      <template #actions>
        <RouterLink to="/rooms" class="button">К списку комнат</RouterLink>
      </template>
    </EmptyState>
    <EmptyState
      v-else-if="!room.is_active"
      title="Эта комната сейчас неактивна"
      description="Бронирование недоступно, пока администратор не активирует комнату."
    >
      <template #actions>
        <RouterLink to="/rooms" class="button">К списку комнат</RouterLink>
      </template>
    </EmptyState>
    <div v-else class="grid grid-2-cols">
      <div class="panel stack">
        <img v-if="room.image_url" :src="room.image_url" :alt="`Фото комнаты ${room.name}`" class="room-photo" />
        <div v-else class="photo"></div>
      </div>
      <div class="panel stack">
        <strong>{{ room.name }}</strong>
        <span class="muted">{{ officeLabel }}</span>
        <span class="muted">Этаж {{ room.floor }}</span>
        <div class="row">
          <span class="kv">{{ room.capacity }} мест</span>
          <span v-for="item in room.equipment" :key="item" class="kv">{{ item }}</span>
        </div>
        <h3>Занятость</h3>
        <Input v-model="selectedDate" type="date" class="w-[220px]" aria-label="Дата занятости комнаты" />
        <p class="muted">Показано на {{ selectedDateLabel }}</p>
        <div class="stack">
          <div v-for="booking in bookingsForDate" :key="booking.id" class="kv">
            {{ fmt(booking.start_time) }}-{{ fmt(booking.end_time) }} · {{ booking.status }}
          </div>
          <div v-if="bookingsForDate.length === 0" class="kv">На выбранную дату бронирований нет</div>
        </div>
        <RouterLink :to="{ path: '/bookings/new', query: { roomId: room.id, date: selectedDate } }" class="button button-dark">Создать бронирование</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import dayjs from "dayjs";
import { useQuery } from "@tanstack/vue-query";
import { RouterLink, useRoute } from "vue-router";
import { EmptyState, ErrorState, LoadingState, PageHeader } from "../../components/common";
import { Input } from "../../components/ui/input";
import { getOfficeById, getRoomBookings, getRoomById, humanizeApiError } from "../../shared/api";
import { formatDateRu, formatTimeRu } from "../../shared/lib/datetime";

const route = useRoute();
const roomId = computed(() => String(route.params.id));
const selectedDate = ref(dayjs().format("YYYY-MM-DD"));

function fmt(value: string) {
  return formatTimeRu(value);
}

const roomQuery = useQuery({
  queryKey: computed(() => ["room-details", roomId.value]),
  queryFn: () => getRoomById(roomId.value),
});
const bookingsQuery = useQuery({
  queryKey: computed(() => ["room-bookings", roomId.value]),
  queryFn: () => getRoomBookings(roomId.value),
});
const room = computed(() => roomQuery.data.value ?? null);
const bookings = computed(() => bookingsQuery.data.value ?? []);
const officeQuery = useQuery({
  queryKey: computed(() => ["room-office", room.value?.office_id]),
  queryFn: () => getOfficeById(room.value!.office_id),
  enabled: computed(() => Boolean(room.value?.office_id)),
});
const office = computed(() => officeQuery.data.value ?? null);
const officeLabel = computed(() =>
  office.value ? `${office.value.name} · ${office.value.city}, ${office.value.address}` : "Офис",
);
const bookingsForDate = computed(() =>
  bookings.value.filter((booking) => dayjs(booking.start_time).format("YYYY-MM-DD") === selectedDate.value),
);
const selectedDateLabel = computed(() => formatDateRu(selectedDate.value));

const isLoading = computed(
  () =>
    roomQuery.isLoading.value ||
    roomQuery.isFetching.value ||
    bookingsQuery.isLoading.value ||
    bookingsQuery.isFetching.value ||
    officeQuery.isLoading.value ||
    officeQuery.isFetching.value,
);

const errorText = computed(() => {
  if (roomQuery.error.value) return humanizeApiError(roomQuery.error.value);
  if (bookingsQuery.error.value) return humanizeApiError(bookingsQuery.error.value);
  return "";
});
</script>

<style scoped>
.room-photo {
  width: 100%;
  height: 320px;
  object-fit: cover;
  border-radius: 12px;
}
</style>
