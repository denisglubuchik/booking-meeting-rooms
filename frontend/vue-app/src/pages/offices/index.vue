<template>
  <div class="stack">
    <PageHeader title="Офисы" description="Сотруднику показываются только активные офисы." />
    <LoadingState v-if="isLoading" />
    <ErrorState v-else-if="errorText" :message="errorText" />
    <EmptyState
      v-else-if="offices.length === 0"
      title="Активных офисов пока нет"
      description="Попробуйте зайти позже или обратитесь к администратору."
    />
    <div v-else class="grid grid-3-cols">
      <OfficeCard
        v-for="office in offices"
        :key="office.id"
        :name="office.name"
        :city="office.city"
        :address="office.address"
        :image-url="office.image_url"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useQuery } from "@tanstack/vue-query";
import { EmptyState, ErrorState, LoadingState, OfficeCard, PageHeader } from "../../components/common";
import { getOffices, humanizeApiError } from "../../shared/api";

const officesQuery = useQuery({
  queryKey: ["employee-offices"],
  queryFn: () => getOffices({ is_active: true }),
});

const offices = computed(() => officesQuery.data.value ?? []);
const isLoading = computed(() => officesQuery.isLoading.value || officesQuery.isFetching.value);
const errorText = computed(() => (officesQuery.error.value ? humanizeApiError(officesQuery.error.value) : ""));
</script>
