import { computed, reactive } from "vue";
import { useQuery } from "@tanstack/vue-query";
import { toTypedSchema } from "@vee-validate/zod";
import { useForm } from "vee-validate";
import { z } from "zod";
import { getBookingHistory, getUsers, humanizeApiError, queryKeys } from "../../shared/api";
import type { components } from "../../shared/api/schema";
import { formatDateTimeRu } from "../../shared/lib/datetime";

type HistoryAction = components["schemas"]["HistoryAction"];

function toDayStartIso(date: string) {
  return `${date}T00:00:00`;
}

function toDayEndIso(date: string) {
  return `${date}T23:59:59`;
}

export function useAdminBookingHistory() {
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
    action: "",
    performed_by: "",
    booking_id: "",
    start_date: "",
    end_date: "",
  });

  const { handleSubmit: handleFilterSubmit, errors: filterErrors } = useForm({
    validationSchema: filterSchema,
    initialValues: { start_date: "", end_date: "" },
  });

  const appliedFilters = reactive({
    action: "",
    performed_by: "",
    booking_id: "",
    start_date: "",
    end_date: "",
  });

  const pagination = reactive({
    limit: 50,
    offset: 0,
  });

  const actionFilterValue = computed({
    get: () => draftFilters.action || "__all",
    set: (value: string) => {
      draftFilters.action = value === "__all" ? "" : value;
    },
  });

  const userFilterValue = computed({
    get: () => draftFilters.performed_by || "__all",
    set: (value: string) => {
      draftFilters.performed_by = value === "__all" ? "" : value;
    },
  });

  function actionLabel(action: string) {
    if (action === "created") return "создано";
    if (action === "cancelled") return "отменено";
    if (action === "completed") return "завершено";
    if (action === "updated") return "обновлено";
    return "перенесено";
  }

  function fmt(value: string) {
    return formatDateTimeRu(value);
  }

  const usersQuery = useQuery({
    queryKey: queryKeys.usersLookup,
    queryFn: () => getUsers(),
  });

  const historyQuery = useQuery({
    queryKey: computed(() => queryKeys.adminBookingHistory({ ...appliedFilters, ...pagination })),
    queryFn: () =>
      getBookingHistory({
        action: (appliedFilters.action || undefined) as HistoryAction | undefined,
        performed_by: appliedFilters.performed_by || undefined,
        booking_id: appliedFilters.booking_id || undefined,
        created_at_gte: appliedFilters.start_date ? toDayStartIso(appliedFilters.start_date) : undefined,
        created_at_lte: appliedFilters.end_date ? toDayEndIso(appliedFilters.end_date) : undefined,
        limit: pagination.limit,
        offset: pagination.offset,
      }),
  });

  const users = computed(() => usersQuery.data.value ?? []);
  const historyItems = computed(() => historyQuery.data.value ?? []);
  const hasNextPage = computed(() => historyItems.value.length === pagination.limit);
  const hasPrevPage = computed(() => pagination.offset > 0);
  const pageLabel = computed(() => `${Math.floor(pagination.offset / pagination.limit) + 1}`);
  const pageRangeLabel = computed(() => {
    if (historyItems.value.length === 0) return "Показано 0";
    const start = pagination.offset + 1;
    const end = pagination.offset + historyItems.value.length;
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
      historyQuery.isLoading.value ||
      historyQuery.isFetching.value,
  );

  const errorText = computed(() => {
    if (usersQuery.error.value) return humanizeApiError(usersQuery.error.value);
    if (historyQuery.error.value) return humanizeApiError(historyQuery.error.value);
    return "";
  });

  function userName(id: string) {
    return users.value.find((u) => u.id === id)?.full_name || id;
  }

  function applyFilters() {
    handleFilterSubmit(() => {
      pagination.offset = 0;
      appliedFilters.action = draftFilters.action;
      appliedFilters.performed_by = draftFilters.performed_by;
      appliedFilters.booking_id = draftFilters.booking_id.trim();
      appliedFilters.start_date = draftFilters.start_date;
      appliedFilters.end_date = draftFilters.end_date;
    })();
  }

  function resetFilters() {
    draftFilters.action = "";
    draftFilters.performed_by = "";
    draftFilters.booking_id = "";
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
    actionFilterValue,
    userFilterValue,
    users,
    historyItems,
    hasNextPage,
    hasPrevPage,
    pageLabel,
    pageRangeLabel,
    pageSizeValue,
    isLoading,
    errorText,
    userName,
    actionLabel,
    fmt,
    applyFilters,
    resetFilters,
    nextPage,
    prevPage,
  };
}
