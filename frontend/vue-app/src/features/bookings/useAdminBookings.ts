import { computed, reactive } from "vue";
import { useQuery } from "@tanstack/vue-query";
import { toTypedSchema } from "@vee-validate/zod";
import { useForm } from "vee-validate";
import { z } from "zod";
import { getAllBookings, getRooms, getUsers, humanizeApiError, queryKeys } from "../../shared/api";
import type { BookingStatus } from "../../shared/types/api";
import { formatDateTimeRu } from "../../shared/lib/datetime";

function toDayStartIso(date: string) {
  return `${date}T00:00:00`;
}

function toDayEndIso(date: string) {
  return `${date}T23:59:59`;
}

export function useAdminBookings() {
  const filterSchema = toTypedSchema(
    z
      .object({
        start_date: z.string().optional(),
        end_date: z.string().optional(),
      })
      .refine((v) => !(v.start_date && v.end_date) || v.start_date <= v.end_date, {
        message: "Дата начала периода не может быть позже даты конца периода.",
        path: ["end_date"],
      }),
  );

  const draftFilters = reactive({
    status: "",
    user_id: "",
    room_id: "",
    start_date: "",
    end_date: "",
  });
  const { handleSubmit: handleFilterSubmit, errors: filterErrors } = useForm({
    validationSchema: filterSchema,
    initialValues: { start_date: "", end_date: "" },
  });

  const appliedFilters = reactive({
    status: "",
    user_id: "",
    room_id: "",
    start_date: "",
    end_date: "",
  });
  const pagination = reactive({
    limit: 50,
    offset: 0,
  });

  const statusFilterValue = computed({
    get: () => draftFilters.status || "__all",
    set: (value: string) => {
      draftFilters.status = value === "__all" ? "" : value;
    },
  });

  const userFilterValue = computed({
    get: () => draftFilters.user_id || "__all",
    set: (value: string) => {
      draftFilters.user_id = value === "__all" ? "" : value;
    },
  });

  const roomFilterValue = computed({
    get: () => draftFilters.room_id || "__all",
    set: (value: string) => {
      draftFilters.room_id = value === "__all" ? "" : value;
    },
  });

  function fmt(value: string) {
    return formatDateTimeRu(value);
  }

  function badgeClass(status: string) {
    if (status === "created") return "badge-created";
    if (status === "cancelled") return "badge-cancelled";
    return "badge-completed";
  }

  function statusLabel(status: string) {
    if (status === "created") return "активно";
    if (status === "cancelled") return "отменено";
    return "завершено";
  }

  const usersQuery = useQuery({
    queryKey: queryKeys.usersLookup,
    queryFn: () => getUsers(),
  });

  const roomsQuery = useQuery({
    queryKey: queryKeys.roomsLookup,
    queryFn: () => getRooms(),
  });

  const bookingsQuery = useQuery({
    queryKey: computed(() => queryKeys.adminBookings({ ...appliedFilters, ...pagination })),
    queryFn: () =>
      getAllBookings({
        status: (appliedFilters.status || undefined) as BookingStatus | undefined,
        user_id: appliedFilters.user_id || undefined,
        room_id: appliedFilters.room_id || undefined,
        start_time_gte: appliedFilters.start_date ? toDayStartIso(appliedFilters.start_date) : undefined,
        end_time_lte: appliedFilters.end_date ? toDayEndIso(appliedFilters.end_date) : undefined,
        limit: pagination.limit,
        offset: pagination.offset,
      }),
  });

  const users = computed(() => usersQuery.data.value ?? []);
  const rooms = computed(() => roomsQuery.data.value ?? []);
  const bookings = computed(() => bookingsQuery.data.value ?? []);
  const hasNextPage = computed(() => bookings.value.length === pagination.limit);
  const hasPrevPage = computed(() => pagination.offset > 0);
  const pageLabel = computed(() => `${Math.floor(pagination.offset / pagination.limit) + 1}`);
  const pageRangeLabel = computed(() => {
    if (bookings.value.length === 0) return "Показано 0";
    const start = pagination.offset + 1;
    const end = pagination.offset + bookings.value.length;
    return `Показано ${start}-${end}`;
  });
  const pageSizeValue = computed({
    get: () => String(pagination.limit),
    set: (value: string) => {
      const next = Number.parseInt(value, 10);
      if (!Number.isFinite(next) || next <= 0) return;
      pagination.limit = next;
      pagination.offset = 0;
    },
  });
  const isLoading = computed(
    () =>
      usersQuery.isLoading.value ||
      usersQuery.isFetching.value ||
      roomsQuery.isLoading.value ||
      roomsQuery.isFetching.value ||
      bookingsQuery.isLoading.value ||
      bookingsQuery.isFetching.value,
  );

  const errorText = computed(() => {
    if (usersQuery.error.value) return humanizeApiError(usersQuery.error.value);
    if (roomsQuery.error.value) return humanizeApiError(roomsQuery.error.value);
    if (bookingsQuery.error.value) return humanizeApiError(bookingsQuery.error.value);
    return "";
  });

  function userName(id: string) {
    return users.value.find((u) => u.id === id)?.full_name || id;
  }

  function roomName(id: string) {
    return rooms.value.find((r) => r.id === id)?.name || id;
  }

  function applyFilters() {
    handleFilterSubmit(() => {
      pagination.offset = 0;
      appliedFilters.status = draftFilters.status;
      appliedFilters.user_id = draftFilters.user_id;
      appliedFilters.room_id = draftFilters.room_id;
      appliedFilters.start_date = draftFilters.start_date;
      appliedFilters.end_date = draftFilters.end_date;
    })();
  }

  function resetFilters() {
    draftFilters.status = "";
    draftFilters.user_id = "";
    draftFilters.room_id = "";
    draftFilters.start_date = "";
    draftFilters.end_date = "";
    applyFilters();
  }

  function nextPage() {
    if (!hasNextPage.value) return;
    pagination.offset += pagination.limit;
  }

  function prevPage() {
    if (!hasPrevPage.value) return;
    pagination.offset = Math.max(0, pagination.offset - pagination.limit);
  }

  return {
    draftFilters,
    filterErrors,
    statusFilterValue,
    userFilterValue,
    roomFilterValue,
    users,
    rooms,
    bookings,
    hasNextPage,
    hasPrevPage,
    pageLabel,
    pageRangeLabel,
    pageSizeValue,
    isLoading,
    errorText,
    fmt,
    badgeClass,
    statusLabel,
    userName,
    roomName,
    applyFilters,
    resetFilters,
    nextPage,
    prevPage,
  };
}
