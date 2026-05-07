<template>
  <div class="stack">
    <PageHeader title="Админ: комнаты" />
    <FilterBar @submit="applyFilters">
      <div class="admin-field admin-col-4">
        <Label>Офис</Label>
        <Select :model-value="officeFilterValue" @update:model-value="officeFilterValue = String($event)">
          <SelectTrigger aria-label="Фильтр по офису">
            <SelectValue placeholder="Офис: все" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="__all">Офис: все</SelectItem>
            <SelectItem v-for="office in offices" :key="office.id" :value="office.id">{{ office.name }}</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div class="admin-field admin-col-3">
        <Label>Статус</Label>
        <Select :model-value="activeFilterValue" @update:model-value="activeFilterValue = String($event)">
          <SelectTrigger aria-label="Фильтр по статусу комнаты">
            <SelectValue placeholder="Любой статус" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="__all">Любой статус</SelectItem>
            <SelectItem value="true">Только активные</SelectItem>
            <SelectItem value="false">Только неактивные</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div class="admin-field admin-col-2">
        <Label>Этаж</Label>
        <Input v-model.number="draftFilters.floor" type="number" min="0" placeholder="Любой" aria-label="Фильтр по этажу" />
      </div>
      <div class="admin-field admin-col-2">
        <Label>Вместимость от</Label>
        <Input v-model.number="draftFilters.capacity_gte" type="number" min="1" placeholder="Любая" aria-label="Минимальная вместимость" />
      </div>
      <div class="admin-field admin-col-1">
        <Label>До</Label>
        <Input v-model.number="draftFilters.capacity_lte" type="number" min="1" placeholder="∞" aria-label="Максимальная вместимость" />
      </div>
      <div class="admin-actions">
        <AppButton :disabled="isBusy" type="submit">Обновить</AppButton>
        <AppButton type="button" :disabled="isBusy" @click="resetFilters">Сбросить</AppButton>
        <AppButton variant="dark" type="button" :disabled="isBusy" @click="toggleCreate">{{ showCreate ? 'Скрыть форму' : 'Создать комнату' }}</AppButton>
      </div>
    </FilterBar>
    <ErrorState v-if="filterErrors.capacity_lte" :message="String(filterErrors.capacity_lte)" />

    <form v-if="showCreate" class="panel stack" @submit.prevent="onCreate">
      <strong>Новая комната</strong>
      <Label>Офис</Label>
      <Select :model-value="createOfficeId" @update:model-value="createOfficeId = String($event)">
        <SelectTrigger class="w-[320px]" aria-label="Офис для новой комнаты">
          <SelectValue placeholder="Выберите офис" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem v-for="office in offices" :key="office.id" :value="office.id">{{ office.name }}</SelectItem>
        </SelectContent>
      </Select>
      <Label>Название</Label>
      <Input v-model="createName" placeholder="Название" aria-label="Название комнаты" />
      <Label>Этаж</Label>
      <Input v-model.number="createFloor" type="number" placeholder="Этаж" aria-label="Этаж комнаты" />
      <Label>Вместимость</Label>
      <Input v-model.number="createCapacity" type="number" placeholder="Вместимость" aria-label="Вместимость комнаты" />
      <Label>Описание</Label>
      <Input v-model="createDescription" placeholder="Описание" aria-label="Описание комнаты" />
      <Label>Оснащение</Label>
      <Input v-model="createEquipment" placeholder="Оснащение через запятую" aria-label="Оснащение комнаты" />
      <Label>Изображение (опционально)</Label>
      <Input
        type="file"
        accept="image/jpeg,image/png,image/webp"
        :disabled="isBusy"
        aria-label="Изображение новой комнаты"
        @change="onCreateRoomImageSelected"
      />
      <ErrorState
        v-if="createErrors.office_id || createErrors.name || createErrors.floor || createErrors.capacity || createErrors.description || createErrors.equipment"
        :message="String(createErrors.office_id || createErrors.name || createErrors.floor || createErrors.capacity || createErrors.description || createErrors.equipment)"
      />
      <div class="row">
        <AppButton variant="dark" type="submit" :disabled="isBusy">{{ createMutation.isPending.value ? 'Создание...' : 'Создать' }}</AppButton>
      </div>
    </form>

    <LoadingState v-if="isLoading" />
    <ErrorState v-else-if="errorText" :message="errorText" />
    <EmptyState
      v-else-if="filteredRooms.length === 0"
      title="Комнаты не найдены"
      description="Измените фильтры или создайте новую комнату."
    />

    <DataTable v-else :columns="['Название', 'Офис', 'Этаж', 'Вместимость', 'Изображение', 'Статус', 'Действия']">
      <TableRow v-for="room in filteredRooms" :key="room.id">
        <template v-if="editingRoomId === room.id">
          <TableCell><Input v-model="editName" aria-label="Изменить название комнаты" /></TableCell>
          <TableCell>{{ officeName(room.office_id) }}</TableCell>
          <TableCell>Этаж {{ room.floor }}</TableCell>
          <TableCell>{{ room.capacity }} мест</TableCell>
          <TableCell>
            <img v-if="room.image_url" :src="room.image_url" alt="Изображение комнаты" class="admin-image-preview" />
            <span v-else class="muted">Нет изображения</span>
          </TableCell>
          <TableCell><StatusBadge :status="room.is_active ? 'active' : 'inactive'" :label="room.is_active ? 'активна' : 'неактивна'" /></TableCell>
          <TableCell>
            <div class="stack">
              <div class="row">
                <AppButton variant="dark" :disabled="isBusy" @click="onSaveEdit(room.id)">{{ updateMutation.isPending.value ? 'Сохранение...' : 'Сохранить' }}</AppButton>
                <AppButton :disabled="isBusy" @click="cancelEdit">Отмена</AppButton>
              </div>
              <div class="row">
                <div class="stack">
                  <Label>Описание</Label>
                  <Input v-model="editDescription" class="w-[320px]" aria-label="Изменить описание комнаты" />
                </div>
                <div class="stack">
                  <Label>Оснащение</Label>
                  <Input v-model="editEquipment" class="w-[320px]" aria-label="Изменить оснащение комнаты" />
                </div>
              </div>
              <div class="row">
                <Input
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  :disabled="isBusy"
                  aria-label="Загрузить изображение комнаты"
                  @change="onRoomImageSelected(room, $event)"
                />
                <AppButton :disabled="isBusy || !room.image_url" @click="removeRoomImage(room)">Удалить фото</AppButton>
              </div>
              <ErrorState
                v-if="editErrors.name || editErrors.description || editErrors.equipment"
                :message="String(editErrors.name || editErrors.description || editErrors.equipment)"
              />
            </div>
          </TableCell>
        </template>
        <template v-else>
          <TableCell>{{ room.name }}</TableCell>
          <TableCell>{{ officeName(room.office_id) }}</TableCell>
          <TableCell>Этаж {{ room.floor }}</TableCell>
          <TableCell>{{ room.capacity }} мест</TableCell>
          <TableCell>
            <img v-if="room.image_url" :src="room.image_url" alt="Изображение комнаты" class="admin-image-preview" />
            <span v-else class="muted">Нет изображения</span>
          </TableCell>
          <TableCell><StatusBadge :status="room.is_active ? 'active' : 'inactive'" :label="room.is_active ? 'активна' : 'неактивна'" /></TableCell>
          <TableCell>
            <div class="admin-table-actions">
              <AppButton :disabled="isBusy" @click="startEdit(room)">Редактировать</AppButton>
              <AppButton :disabled="isBusy" @click="toggleActive(room)">{{ toggleMutation.isPending.value ? 'Подождите...' : (room.is_active ? 'Деактивировать' : 'Активировать') }}</AppButton>
            </div>
          </TableCell>
        </template>
      </TableRow>
    </DataTable>
  </div>
</template>

<script setup lang="ts">
import { DataTable, EmptyState, ErrorState, FilterBar, LoadingState, PageHeader, StatusBadge } from "../../components/common";
import { TableCell, TableRow } from "../../components/ui/table";
import AppButton from "../../components/ui/button/AppButton.vue";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../components/ui/select";
import { useAdminRooms } from "../../features/rooms";

const {
  showCreate,
  editingRoomId,
  createOfficeId,
  createName,
  createFloor,
  createCapacity,
  createDescription,
  createEquipment,
  createErrors,
  editName,
  editDescription,
  editEquipment,
  editErrors,
  filterErrors,
  draftFilters,
  officeFilterValue,
  activeFilterValue,
  offices,
  filteredRooms,
  officeName,
  isLoading,
  errorText,
  createMutation,
  updateMutation,
  toggleMutation,
  isBusy,
  toggleCreate,
  applyFilters,
  resetFilters,
  startEdit,
  cancelEdit,
  onCreate,
  onSaveEdit,
  toggleActive,
  onCreateRoomImageSelected,
  onRoomImageSelected,
  removeRoomImage,
} = useAdminRooms();
</script>

<style scoped>
.admin-image-preview {
  width: 72px;
  height: 48px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid var(--border);
}
</style>
