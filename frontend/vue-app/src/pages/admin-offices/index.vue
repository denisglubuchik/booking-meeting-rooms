<template>
  <div class="stack">
    <PageHeader title="Админ: офисы" />

    <FilterBar @submit="applyFilters">
      <div class="admin-field admin-col-5">
        <Label>Город</Label>
        <Input v-model="draftFilters.city" placeholder="Любой город" aria-label="Фильтр по городу" />
      </div>
      <div class="admin-field admin-col-3">
        <Label>Статус</Label>
        <Select :model-value="activeFilterValue" @update:model-value="activeFilterValue = String($event)">
          <SelectTrigger aria-label="Фильтр по статусу офиса">
            <SelectValue placeholder="Любой статус" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="__all">Любой статус</SelectItem>
            <SelectItem value="true">Только активные</SelectItem>
            <SelectItem value="false">Только неактивные</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div class="admin-actions">
        <AppButton :disabled="isBusy" type="submit">Обновить</AppButton>
        <AppButton type="button" :disabled="isBusy" @click="resetFilters">Сбросить</AppButton>
        <AppButton variant="dark" type="button" :disabled="isBusy" @click="toggleCreate">{{ showCreate ? 'Скрыть форму' : 'Создать офис' }}</AppButton>
      </div>
    </FilterBar>

    <form v-if="showCreate" class="panel stack" @submit.prevent="onCreate">
      <strong>Новый офис</strong>
      <Label>Название</Label>
      <Input v-model="createName" placeholder="Название" aria-label="Название офиса" />
      <Label>Город</Label>
      <Input v-model="createCity" placeholder="Город" aria-label="Город офиса" />
      <Label>Адрес</Label>
      <Input v-model="createAddress" placeholder="Адрес" aria-label="Адрес офиса" />
      <Label>Изображение (опционально)</Label>
      <Input
        type="file"
        accept="image/jpeg,image/png,image/webp"
        :disabled="isBusy"
        aria-label="Изображение нового офиса"
        @change="onCreateOfficeImageSelected"
      />
      <ErrorState
        v-if="createErrors.name || createErrors.city || createErrors.address"
        :message="String(createErrors.name || createErrors.city || createErrors.address)"
      />
      <div class="row"><AppButton variant="dark" type="submit" :disabled="isBusy">{{ createMutation.isPending.value ? 'Создание...' : 'Создать' }}</AppButton></div>
    </form>

    <LoadingState v-if="isLoading" />
    <ErrorState v-else-if="errorText" :message="errorText" />
    <EmptyState
      v-else-if="offices.length === 0"
      title="Офисы не найдены"
      description="Измените фильтры или создайте новый офис."
    />

    <DataTable v-else :columns="['Название', 'Город', 'Адрес', 'Изображение', 'Статус', 'Действия']">
      <TableRow v-for="office in offices" :key="office.id">
        <template v-if="editingOfficeId === office.id">
          <TableCell><Input v-model="editName" aria-label="Изменить название офиса" /></TableCell>
          <TableCell><Input v-model="editCity" aria-label="Изменить город офиса" /></TableCell>
          <TableCell><Input v-model="editAddress" aria-label="Изменить адрес офиса" /></TableCell>
          <TableCell>
            <img v-if="office.image_url" :src="office.image_url" alt="Изображение офиса" class="admin-image-preview" />
            <span v-else class="muted">Нет изображения</span>
          </TableCell>
          <TableCell><StatusBadge :status="office.is_active ? 'active' : 'inactive'" :label="office.is_active ? 'активен' : 'неактивен'" /></TableCell>
          <TableCell>
            <div class="stack">
              <div class="row">
                <AppButton variant="dark" :disabled="isBusy" @click="onSaveEdit(office.id)">{{ updateMutation.isPending.value ? 'Сохранение...' : 'Сохранить' }}</AppButton>
                <AppButton :disabled="isBusy" @click="cancelEdit">Отмена</AppButton>
              </div>
              <div class="row">
                <Input
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  :disabled="isBusy"
                  aria-label="Загрузить изображение офиса"
                  @change="onOfficeImageSelected(office, $event)"
                />
                <AppButton :disabled="isBusy || !office.image_url" @click="removeOfficeImage(office)">Удалить фото</AppButton>
              </div>
            </div>
            <ErrorState
              v-if="editErrors.name || editErrors.city || editErrors.address"
              :message="String(editErrors.name || editErrors.city || editErrors.address)"
            />
          </TableCell>
        </template>
        <template v-else>
          <TableCell>{{ office.name }}</TableCell>
          <TableCell>{{ office.city }}</TableCell>
          <TableCell>{{ office.address }}</TableCell>
          <TableCell>
            <img v-if="office.image_url" :src="office.image_url" alt="Изображение офиса" class="admin-image-preview" />
            <span v-else class="muted">Нет изображения</span>
          </TableCell>
          <TableCell><StatusBadge :status="office.is_active ? 'active' : 'inactive'" :label="office.is_active ? 'активен' : 'неактивен'" /></TableCell>
          <TableCell>
            <div class="admin-table-actions">
              <AppButton :disabled="isBusy" @click="startEdit(office)">Редактировать</AppButton>
              <AppButton :disabled="isBusy" @click="toggleActive(office)">{{ toggleMutation.isPending.value ? 'Подождите...' : (office.is_active ? 'Деактивировать' : 'Активировать') }}</AppButton>
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
import { useAdminOffices } from "../../features/offices";

const {
  draftFilters,
  activeFilterValue,
  showCreate,
  createName,
  createCity,
  createAddress,
  createErrors,
  createMutation,
  offices,
  editingOfficeId,
  editName,
  editCity,
  editAddress,
  editErrors,
  updateMutation,
  toggleMutation,
  isLoading,
  errorText,
  isBusy,
  toggleCreate,
  applyFilters,
  resetFilters,
  startEdit,
  cancelEdit,
  onCreate,
  onSaveEdit,
  toggleActive,
  onCreateOfficeImageSelected,
  onOfficeImageSelected,
  removeOfficeImage,
} = useAdminOffices();
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
