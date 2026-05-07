<template>
  <div class="stack">
    <PageHeader title="Комнаты" />
    <FilterBar @submit="applyFilter">
      <Select :model-value="officeFilterValue" @update:model-value="officeFilterValue = String($event)">
        <SelectTrigger class="w-[220px]">
          <SelectValue placeholder="Офис: все" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="__all">Офис: все</SelectItem>
          <SelectItem v-for="office in offices" :key="office.id" :value="office.id">{{ office.name }}</SelectItem>
        </SelectContent>
      </Select>
      <Input v-model.number="draftFloor" class="w-[140px]" type="number" min="0" placeholder="Этаж" />
      <Input v-model.number="draftCapacityGte" class="w-[170px]" type="number" min="1" placeholder="Вместимость от" />
      <Input v-model.number="draftCapacityLte" class="w-[170px]" type="number" min="1" placeholder="Вместимость до" />
      <AppButton variant="dark" type="submit">Применить</AppButton>
      <AppButton type="button" @click="resetFilters">Сбросить</AppButton>
    </FilterBar>
    <ErrorState v-if="capacityError" :message="capacityError" />
    <div v-if="hasAppliedFilters" class="row">
      <span class="kv">{{ selectedOfficeLabel }}</span>
      <span class="kv">{{ appliedFloorLabel }}</span>
      <span class="kv">{{ appliedCapacityLabel }}</span>
    </div>
    <LoadingState v-if="isLoading" />
    <ErrorState v-else-if="errorText" :message="errorText" />
    <EmptyState
      v-else-if="offices.length === 0"
      title="Сейчас нет доступных офисов"
      description="Когда администратор добавит активные офисы, комнаты появятся здесь."
    />
    <EmptyState
      v-else-if="rooms.length === 0"
      title="Комнаты не найдены"
      description="Попробуйте изменить фильтры или сбросить параметры поиска."
    />
    <div v-else class="grid grid-3-cols">
      <RoomCard
        v-for="room in rooms"
        :key="room.id"
        :name="room.name"
        :capacity="room.capacity"
        :floor="room.floor"
        :office-name="officeName(room.office_id)"
        :image-url="room.image_url"
      >
        <template #actions>
          <RouterLink :to="`/rooms/${room.id}`" class="button">Подробнее</RouterLink>
          <RouterLink :to="{ path: '/bookings/new', query: { roomId: room.id } }" class="button button-dark">Забронировать</RouterLink>
        </template>
      </RoomCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useQuery } from "@tanstack/vue-query";
import { RouterLink } from "vue-router";
import AppButton from "../../components/ui/button/AppButton.vue";
import { Input } from "../../components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../components/ui/select";
import { EmptyState, ErrorState, FilterBar, LoadingState, PageHeader, RoomCard } from "../../components/common";
import { getOffices, getRooms, humanizeApiError } from "../../shared/api";

const draftOfficeId = ref("");
const draftFloor = ref<number | undefined>(undefined);
const draftCapacityGte = ref<number | undefined>(2);
const draftCapacityLte = ref<number | undefined>(undefined);
const appliedOfficeId = ref("");
const appliedFloor = ref<number | undefined>(undefined);
const appliedCapacityGte = ref<number | undefined>(2);
const appliedCapacityLte = ref<number | undefined>(undefined);
const capacityError = ref("");

const officeFilterValue = computed({
  get: () => draftOfficeId.value || "__all",
  set: (value: string) => {
    draftOfficeId.value = value === "__all" ? "" : value;
  },
});

const officesQuery = useQuery({
  queryKey: ["employee-room-offices"],
  queryFn: () => getOffices({ is_active: true }),
});

const roomsQuery = useQuery({
  queryKey: computed(() => [
    "employee-rooms",
    {
      office_id: appliedOfficeId.value,
      floor: appliedFloor.value,
      capacity_gte: appliedCapacityGte.value,
      capacity_lte: appliedCapacityLte.value,
    },
  ]),
  queryFn: () =>
    getRooms({
      is_active: true,
      office_id: appliedOfficeId.value || undefined,
      floor: appliedFloor.value,
      capacity_gte: appliedCapacityGte.value,
      capacity_lte: appliedCapacityLte.value,
    }),
});

const offices = computed(() => officesQuery.data.value ?? []);
const rooms = computed(() => roomsQuery.data.value ?? []);
const isLoading = computed(
  () =>
    officesQuery.isLoading.value ||
    officesQuery.isFetching.value ||
    roomsQuery.isLoading.value ||
    roomsQuery.isFetching.value,
);
const errorText = computed(() => {
  if (officesQuery.error.value) return humanizeApiError(officesQuery.error.value);
  if (roomsQuery.error.value) return humanizeApiError(roomsQuery.error.value);
  return "";
});

function applyFilter() {
  capacityError.value = "";
  const nextGte =
    typeof draftCapacityGte.value === "number" ? Math.max(1, Number(draftCapacityGte.value) || 1) : undefined;
  const nextLte =
    typeof draftCapacityLte.value === "number" ? Math.max(1, Number(draftCapacityLte.value) || 1) : undefined;
  if (typeof nextGte === "number" && typeof nextLte === "number" && nextGte > nextLte) {
    capacityError.value = "Минимальная вместимость не может быть больше максимальной.";
    return;
  }
  appliedOfficeId.value = draftOfficeId.value;
  appliedFloor.value = typeof draftFloor.value === "number" ? Math.max(0, Number(draftFloor.value) || 0) : undefined;
  appliedCapacityGte.value = nextGte;
  appliedCapacityLte.value = nextLte;
}

function resetFilters() {
  draftOfficeId.value = "";
  draftFloor.value = undefined;
  draftCapacityGte.value = 2;
  draftCapacityLte.value = undefined;
  applyFilter();
}

function officeName(officeId: string) {
  return offices.value.find((office) => office.id === officeId)?.name || "Офис";
}

const selectedOfficeLabel = computed(() =>
  appliedOfficeId.value ? `Офис: ${officeName(appliedOfficeId.value)}` : "Офис: все",
);
const appliedFloorLabel = computed(() =>
  typeof appliedFloor.value === "number" ? `Этаж: ${appliedFloor.value}` : "Этаж: любой",
);
const appliedCapacityLabel = computed(() => {
  if (typeof appliedCapacityGte.value === "number" && typeof appliedCapacityLte.value === "number") {
    return `Вместимость: ${appliedCapacityGte.value}-${appliedCapacityLte.value}`;
  }
  if (typeof appliedCapacityGte.value === "number") return `Вместимость: от ${appliedCapacityGte.value}`;
  if (typeof appliedCapacityLte.value === "number") return `Вместимость: до ${appliedCapacityLte.value}`;
  return "Вместимость: любая";
});
const hasAppliedFilters = computed(
  () =>
    Boolean(appliedOfficeId.value) ||
    typeof appliedFloor.value === "number" ||
    typeof appliedCapacityGte.value === "number" ||
    typeof appliedCapacityLte.value === "number",
);
</script>
