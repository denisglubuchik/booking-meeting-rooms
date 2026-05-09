<template>
  <div class="stack">
    <PageHeader title="Создать бронирование" description="Только в пределах одного календарного дня." />

    <LoadingState v-if="isLoading" />
    <ErrorState v-else-if="errorText" :message="errorText" />

    <div v-else class="grid grid-2-cols">
      <form class="panel stack" @submit.prevent="onSubmit">
        <Select :model-value="roomId" @update:model-value="roomId = String($event)">
          <SelectTrigger class="w-full" aria-label="Выбор комнаты">
            <SelectValue placeholder="Выберите комнату" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem v-for="room in rooms" :key="room.id" :value="room.id">
              {{ room.name }} ({{ room.capacity }} мест)
            </SelectItem>
          </SelectContent>
        </Select>
        <Input v-model="date" type="date" aria-label="Дата встречи" />
        <Input v-model="start" type="text" inputmode="numeric" placeholder="ЧЧ:ММ (24ч)" aria-label="Время начала встречи" />
        <Input v-model="end" type="text" inputmode="numeric" placeholder="ЧЧ:ММ (24ч)" aria-label="Время окончания встречи" />
        <Input v-model="title" placeholder="Название встречи" aria-label="Название встречи" />
        <ErrorState v-if="firstError" :message="firstError" />
        <AppButton variant="dark" type="submit" :disabled="createMutation.isPending.value">{{ createMutation.isPending.value ? 'Создаем...' : 'Подтвердить бронь' }}</AppButton>
      </form>
      <div class="panel stack">
        <strong>Сводка</strong>
        <div class="kv">Комната: {{ selectedRoom?.name || 'не выбрана' }}</div>
        <div class="kv">Офис: {{ selectedOffice?.name || '-' }}</div>
        <div class="kv">Дата: {{ date }}</div>
        <div class="kv">Интервал: {{ start }}-{{ end }}</div>
        <div class="kv">Вместимость: {{ selectedRoom?.capacity || '-' }}</div>
        <div class="kv">Оснащение: {{ selectedRoom?.equipment.join(', ') || '-' }}</div>
        <p v-if="success" class="muted">{{ success }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ErrorState, LoadingState, PageHeader } from "../../components/common";
import AppButton from "../../components/ui/button/AppButton.vue";
import { Input } from "../../components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../components/ui/select";
import { useCreateBooking } from "../../features/bookings";

const { roomId, date, start, end, title, rooms, selectedRoom, selectedOffice, isLoading, errorText, firstError, success, createMutation, onSubmit } =
  useCreateBooking();
</script>
