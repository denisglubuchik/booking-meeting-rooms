<template>
  <div class="stack">
    <PageHeader title="Найти комнату" />
    <FilterBar @submit="search">
      <Select :model-value="officeFilterValue" @update:model-value="officeFilterValue = String($event)">
        <SelectTrigger class="w-[220px]" aria-label="Фильтр по офису">
          <SelectValue placeholder="Офис: любой" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="__all">Офис: любой</SelectItem>
          <SelectItem v-for="office in offices" :key="office.id" :value="office.id">{{ office.name }}</SelectItem>
        </SelectContent>
      </Select>
      <Input v-model="draft.date" type="date" aria-label="Дата бронирования" />
      <Input v-model="draft.startTime" type="time" aria-label="Время начала" />
      <Input v-model="draft.endTime" type="time" aria-label="Время окончания" />
      <Input v-model.number="draft.floor" class="w-[140px]" type="number" min="0" placeholder="Этаж" aria-label="Этаж" />
      <Input v-model.number="draft.capacity_gte" class="w-[170px]" type="number" min="1" placeholder="Вместимость от" aria-label="Минимальная вместимость" />
      <Input v-model.number="draft.capacity_lte" class="w-[170px]" type="number" min="1" placeholder="Вместимость до" aria-label="Максимальная вместимость" />
      <AppButton variant="dark" type="submit">Найти</AppButton>
    </FilterBar>
    <ErrorState v-if="firstError" :message="firstError" />
    <div v-else class="row">
      <span class="kv">{{ appliedCriteria }}</span>
    </div>
    <LoadingState v-if="!firstError && isLoading" />
    <ErrorState v-else-if="!firstError && errorText" :message="errorText" />
    <EmptyState
      v-else-if="!firstError && rooms.length === 0"
      title="Свободных комнат не найдено"
      description="Попробуйте изменить время, офис или вместимость."
    />
    <div v-else-if="!firstError" class="grid grid-2-cols">
      <RoomCard
        v-for="room in rooms"
        :key="room.id"
        :name="room.name"
        :office-name="officeLabel"
        :floor="room.floor"
        :capacity="room.capacity"
        :image-url="room.image_url"
      >
        <template #actions>
          <StatusBadge status="created" label="свободна" />
          <span class="kv">{{ room.capacity }} мест</span>
          <RouterLink :to="{ path: '/bookings/new', query: bookingQuery(room.id) }" class="button button-dark">Забронировать</RouterLink>
          <RouterLink :to="`/rooms/${room.id}`" class="button">Подробнее</RouterLink>
        </template>
      </RoomCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { RouterLink } from "vue-router";
import { EmptyState, ErrorState, FilterBar, LoadingState, PageHeader, RoomCard, StatusBadge } from "../../components/common";
import AppButton from "../../components/ui/button/AppButton.vue";
import { Input } from "../../components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../components/ui/select";
import { useFindRoom } from "../../features/bookings";

const { draft, applied, officeFilterValue, offices, firstError, rooms, isLoading, errorText, search } = useFindRoom();

function bookingQuery(roomId: string) {
  return {
    roomId,
    officeId: applied.office_id || "",
    date: applied.date,
    start: applied.startTime,
    end: applied.endTime,
    floor: typeof applied.floor === "number" ? String(applied.floor) : "",
    capacityGte: typeof applied.capacity_gte === "number" ? String(applied.capacity_gte) : "",
    capacityLte: typeof applied.capacity_lte === "number" ? String(applied.capacity_lte) : "",
  };
}

const officeLabel = computed(() => {
  if (!applied.office_id) return "Офис: любой";
  const office = offices.value.find((item) => item.id === applied.office_id);
  return office ? `Офис: ${office.name}` : "Офис";
});

const appliedCriteria = computed(() => {
  const chunks = [`Дата: ${applied.date}`, `${applied.startTime}-${applied.endTime}`];
  if (applied.office_id) {
    const office = offices.value.find((item) => item.id === applied.office_id);
    if (office) chunks.push(`Офис: ${office.name}`);
  }
  if (typeof applied.floor === "number") chunks.push(`Этаж: ${applied.floor}`);
  if (typeof applied.capacity_gte === "number" && typeof applied.capacity_lte === "number") {
    chunks.push(`Вместимость: ${applied.capacity_gte}-${applied.capacity_lte}`);
  } else if (typeof applied.capacity_gte === "number") {
    chunks.push(`Вместимость: от ${applied.capacity_gte}`);
  } else if (typeof applied.capacity_lte === "number") {
    chunks.push(`Вместимость: до ${applied.capacity_lte}`);
  }
  return chunks.join(" · ");
});
</script>
