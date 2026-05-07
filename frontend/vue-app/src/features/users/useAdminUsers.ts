import { computed, reactive } from "vue";
import { useMutation, useQuery, useQueryClient } from "@tanstack/vue-query";
import { toTypedSchema } from "@vee-validate/zod";
import { useForm } from "vee-validate";
import { z } from "zod";
import {
  activateUser,
  deactivateUser,
  demoteToEmployee,
  getUsers,
  humanizeApiError,
  promoteToAdmin,
  queryKeys,
} from "../../shared/api";
import type { User } from "../../shared/types/api";
import { formatDateTimeRu } from "../../shared/lib/datetime";
import { useAuthStore } from "../auth";
import { useConfirm } from "../ui/confirm";
import { useToast } from "../ui/toast";

function toDayStartIso(date: string) {
  return `${date}T00:00:00`;
}

function toDayEndIso(date: string) {
  return `${date}T23:59:59`;
}

export function useAdminUsers() {
  const toast = useToast();
  const confirm = useConfirm();
  const queryClient = useQueryClient();
  const auth = useAuthStore();

  const filterSchema = toTypedSchema(
    z
      .object({
        created_from: z.string().optional(),
        created_to: z.string().optional(),
      })
      .refine((v) => !(v.created_from && v.created_to) || v.created_from <= v.created_to, {
        message: "Дата 'создан после' не может быть позже даты 'создан до'.",
        path: ["created_to"],
      }),
  );

  const draftFilters = reactive({
    role: "",
    is_active: "",
    created_from: "",
    created_to: "",
  });
  const { handleSubmit: handleFilterSubmit, errors: filterErrors } = useForm({
    validationSchema: filterSchema,
    initialValues: { created_from: "", created_to: "" },
  });

  const appliedFilters = reactive({
    role: "",
    is_active: "",
    created_from: "",
    created_to: "",
  });
  const pagination = reactive({
    limit: 50,
    offset: 0,
  });

  const roleFilterValue = computed({
    get: () => draftFilters.role || "__all",
    set: (value: string) => {
      draftFilters.role = value === "__all" ? "" : value;
    },
  });

  const activeFilterValue = computed({
    get: () => draftFilters.is_active || "__all",
    set: (value: string) => {
      draftFilters.is_active = value === "__all" ? "" : value;
    },
  });

  function currentFilters() {
    return {
      role: (appliedFilters.role || undefined) as "employee" | "admin" | undefined,
      is_active: appliedFilters.is_active === "" ? undefined : appliedFilters.is_active === "true",
      created_at_gte: appliedFilters.created_from ? toDayStartIso(appliedFilters.created_from) : undefined,
      created_at_lte: appliedFilters.created_to ? toDayEndIso(appliedFilters.created_to) : undefined,
      limit: pagination.limit,
      offset: pagination.offset,
    };
  }

  const usersQuery = useQuery({
    queryKey: computed(() => queryKeys.adminUsers({ ...appliedFilters, ...pagination })),
    queryFn: () => getUsers(currentFilters()),
  });

  const users = computed(() => usersQuery.data.value ?? []);
  const hasNextPage = computed(() => users.value.length === pagination.limit);
  const hasPrevPage = computed(() => pagination.offset > 0);
  const pageLabel = computed(() => `${Math.floor(pagination.offset / pagination.limit) + 1}`);
  const pageRangeLabel = computed(() => {
    if (users.value.length === 0) return "Показано 0";
    const start = pagination.offset + 1;
    const end = pagination.offset + users.value.length;
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
  const isLoading = computed(() => usersQuery.isLoading.value || usersQuery.isFetching.value);
  const errorText = computed(() => (usersQuery.error.value ? humanizeApiError(usersQuery.error.value) : ""));

  const roleMutation = useMutation({
    mutationFn: async (user: User) => {
      if (user.role === "admin") return demoteToEmployee(user.id);
      return promoteToAdmin(user.id);
    },
    onSuccess: async () => {
      toast.success("Роль пользователя обновлена.");
      await queryClient.invalidateQueries({ queryKey: ["admin-users"] });
    },
    onError: (err) => {
      toast.error(humanizeApiError(err));
    },
  });

  const activeMutation = useMutation({
    mutationFn: async (user: User) => {
      if (user.is_active) return deactivateUser(user.id);
      return activateUser(user.id);
    },
    onSuccess: async () => {
      toast.success("Статус пользователя обновлен.");
      await queryClient.invalidateQueries({ queryKey: ["admin-users"] });
    },
    onError: (err) => {
      toast.error(humanizeApiError(err));
    },
  });

  const isBusy = computed(() => isLoading.value || roleMutation.isPending.value || activeMutation.isPending.value);

  function applyFilters() {
    handleFilterSubmit(() => {
      pagination.offset = 0;
      appliedFilters.role = draftFilters.role;
      appliedFilters.is_active = draftFilters.is_active;
      appliedFilters.created_from = draftFilters.created_from;
      appliedFilters.created_to = draftFilters.created_to;
    })();
  }

  function resetFilters() {
    draftFilters.role = "";
    draftFilters.is_active = "";
    draftFilters.created_from = "";
    draftFilters.created_to = "";
    applyFilters();
  }

  async function toggleRole(user: User) {
    if (user.email === auth.email && user.role === "admin") {
      toast.error("Нельзя снять роль администратора у своей учетной записи.");
      return;
    }
    const targetRole = user.role === "admin" ? "сотрудником" : "админом";
    const ok = await confirm.ask({
      message: `Сменить роль пользователя на ${targetRole}?`,
      confirmText: "Изменить роль",
    });
    if (!ok) return;
    roleMutation.mutate(user);
  }

  async function toggleActive(user: User) {
    if (user.email === auth.email && user.is_active) {
      toast.error("Нельзя деактивировать свою учетную запись.");
      return;
    }
    const action = user.is_active ? "деактивировать" : "активировать";
    const ok = await confirm.ask({
      message: `Вы уверены, что хотите ${action} пользователя?`,
      confirmText: user.is_active ? "Деактивировать" : "Активировать",
    });
    if (!ok) return;
    activeMutation.mutate(user);
  }

  function nextPage() {
    if (!hasNextPage.value) return;
    pagination.offset += pagination.limit;
  }

  function prevPage() {
    if (!hasPrevPage.value) return;
    pagination.offset = Math.max(0, pagination.offset - pagination.limit);
  }

  function formatCreatedAt(value?: string) {
    if (!value) return "—";
    return formatDateTimeRu(value);
  }

  function roleLabel(role: string) {
    if (role === "admin") return "администратор";
    if (role === "employee") return "сотрудник";
    return role;
  }

  return {
    draftFilters,
    filterErrors,
    roleFilterValue,
    activeFilterValue,
    users,
    pagination,
    hasNextPage,
    hasPrevPage,
    pageLabel,
    pageRangeLabel,
    pageSizeValue,
    isLoading,
    isBusy,
    errorText,
    applyFilters,
    resetFilters,
    nextPage,
    prevPage,
    formatCreatedAt,
    roleLabel,
    toggleRole,
    toggleActive,
  };
}
