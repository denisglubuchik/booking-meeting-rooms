import { computed, reactive, ref } from "vue";
import { useMutation, useQuery, useQueryClient } from "@tanstack/vue-query";
import { toTypedSchema } from "@vee-validate/zod";
import { useForm } from "vee-validate";
import { z } from "zod";
import {
  activateOffice,
  createOffice,
  deleteOfficeImage,
  deactivateOffice,
  getOffices,
  humanizeApiError,
  queryKeys,
  setOfficeImage,
  updateOffice,
} from "../../shared/api";
import type { Office } from "../../shared/types/api";
import { useConfirm } from "../ui/confirm";
import { useToast } from "../ui/toast";

export function useAdminOffices() {
  const toast = useToast();
  const confirm = useConfirm();
  const queryClient = useQueryClient();

  const showCreate = ref(false);
  const editingOfficeId = ref<string | null>(null);
  const createImageFile = ref<File | null>(null);
  const allowedMimeTypes = new Set(["image/jpeg", "image/png", "image/webp"]);
  const createSchema = toTypedSchema(
    z.object({
      name: z.string().trim().min(2, "Введите название офиса."),
      city: z.string().trim().min(2, "Введите город."),
      address: z.string().trim().min(3, "Введите адрес."),
    }),
  );
  const editSchema = toTypedSchema(
    z.object({
      name: z.string().trim().min(2, "Введите название офиса."),
      city: z.string().trim().min(2, "Введите город."),
      address: z.string().trim().min(3, "Введите адрес."),
    }),
  );
  const draftFilters = reactive({ city: "", is_active: "" });
  const appliedFilters = reactive({ city: "", is_active: "" });
  const activeFilterValue = computed({
    get: () => draftFilters.is_active || "__all",
    set: (value: string) => {
      draftFilters.is_active = value === "__all" ? "" : value;
    },
  });

  const {
    defineField: defineCreateField,
    handleSubmit: handleCreateSubmit,
    setValues: setCreateValues,
    errors: createErrors,
  } = useForm({
    validationSchema: createSchema,
    initialValues: { name: "", city: "", address: "" },
  });
  const [createName] = defineCreateField("name");
  const [createCity] = defineCreateField("city");
  const [createAddress] = defineCreateField("address");

  const {
    defineField: defineEditField,
    handleSubmit: handleEditSubmit,
    setValues: setEditValues,
    errors: editErrors,
  } = useForm({
    validationSchema: editSchema,
    initialValues: { name: "", city: "", address: "" },
  });
  const [editName] = defineEditField("name");
  const [editCity] = defineEditField("city");
  const [editAddress] = defineEditField("address");

  function queryFilters() {
    return {
      city: appliedFilters.city.trim() || undefined,
      is_active: appliedFilters.is_active === "" ? undefined : appliedFilters.is_active === "true",
    };
  }

  const officesQuery = useQuery({
    queryKey: computed(() => queryKeys.adminOffices({ ...appliedFilters })),
    queryFn: () => getOffices(queryFilters()),
  });

  const offices = computed(() => officesQuery.data.value ?? []);
  const isLoading = computed(() => officesQuery.isLoading.value || officesQuery.isFetching.value);
  const errorText = computed(() =>
    officesQuery.error.value ? humanizeApiError(officesQuery.error.value) : "",
  );

  async function refreshOffices() {
    await queryClient.invalidateQueries({ queryKey: ["admin-offices"] });
  }

  const createMutation = useMutation({
    mutationFn: (values: { name: string; city: string; address: string }) =>
      createOffice({
        name: values.name.trim(),
        city: values.city.trim(),
        address: values.address.trim(),
      }),
    onSuccess: async () => {
      setCreateValues({ name: "", city: "", address: "" });
      showCreate.value = false;
      toast.success("Офис создан.");
      await refreshOffices();
    },
    onError: (err) => toast.error(humanizeApiError(err)),
  });

  const updateMutation = useMutation({
    mutationFn: ({ officeId, values }: { officeId: string; values: { name: string; city: string; address: string } }) =>
      updateOffice(officeId, {
        name: values.name.trim(),
        city: values.city.trim(),
        address: values.address.trim(),
      }),
    onSuccess: async () => {
      editingOfficeId.value = null;
      toast.success("Офис обновлен.");
      await refreshOffices();
    },
    onError: (err) => toast.error(humanizeApiError(err)),
  });

  const toggleMutation = useMutation({
    mutationFn: (office: Office) =>
      office.is_active ? deactivateOffice(office.id) : activateOffice(office.id),
    onSuccess: async (_, office) => {
      toast.success(`Офис ${office.is_active ? "деактивирован" : "активирован"}.`);
      await refreshOffices();
    },
    onError: (err) => toast.error(humanizeApiError(err)),
  });

  const uploadImageMutation = useMutation({
    mutationFn: ({ officeId, file }: { officeId: string; file: File }) => setOfficeImage(officeId, file),
    onSuccess: async () => {
      toast.success("Изображение офиса обновлено.");
      await refreshOffices();
    },
    onError: (err) => toast.error(humanizeApiError(err)),
  });

  const deleteImageMutation = useMutation({
    mutationFn: (officeId: string) => deleteOfficeImage(officeId),
    onSuccess: async () => {
      toast.success("Изображение офиса удалено.");
      await refreshOffices();
    },
    onError: (err) => toast.error(humanizeApiError(err)),
  });

  const isBusy = computed(
    () =>
      isLoading.value ||
      createMutation.isPending.value ||
      updateMutation.isPending.value ||
      toggleMutation.isPending.value ||
      uploadImageMutation.isPending.value ||
      deleteImageMutation.isPending.value,
  );

  function toggleCreate() {
    showCreate.value = !showCreate.value;
  }

  function applyFilters() {
    appliedFilters.city = draftFilters.city;
    appliedFilters.is_active = draftFilters.is_active;
  }

  function resetFilters() {
    draftFilters.city = "";
    draftFilters.is_active = "";
    applyFilters();
  }

  function startEdit(office: Office) {
    editingOfficeId.value = office.id;
    setEditValues({ name: office.name, city: office.city, address: office.address });
  }

  function cancelEdit() {
    editingOfficeId.value = null;
  }

  const onCreate = handleCreateSubmit(async (values) => {
    const office = await createMutation.mutateAsync(values);
    if (createImageFile.value) {
      await uploadImageMutation.mutateAsync({ officeId: office.id, file: createImageFile.value });
      createImageFile.value = null;
    }
  });

  function onSaveEdit(officeId: string) {
    handleEditSubmit((values) => {
      updateMutation.mutate({ officeId, values });
    })();
  }

  async function toggleActive(office: Office) {
    const action = office.is_active ? "деактивировать" : "активировать";
    const ok = await confirm.ask({
      message: `Вы уверены, что хотите ${action} офис?`,
      confirmText: office.is_active ? "Деактивировать" : "Активировать",
    });
    if (!ok) return;
    toggleMutation.mutate(office);
  }

  function onOfficeImageSelected(office: Office, event: Event) {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;
    if (!allowedMimeTypes.has(file.type)) {
      toast.error("Поддерживаются только JPEG, PNG и WEBP.");
      input.value = "";
      return;
    }
    uploadImageMutation.mutate({ officeId: office.id, file });
    input.value = "";
  }

  function onCreateOfficeImageSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;
    if (!allowedMimeTypes.has(file.type)) {
      toast.error("Поддерживаются только JPEG, PNG и WEBP.");
      input.value = "";
      createImageFile.value = null;
      return;
    }
    createImageFile.value = file;
  }

  async function removeOfficeImage(office: Office) {
    if (!office.image_url) return;
    const ok = await confirm.ask({
      message: "Удалить изображение офиса?",
      confirmText: "Удалить",
    });
    if (!ok) return;
    deleteImageMutation.mutate(office.id);
  }

  return {
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
    createImageFile,
    onCreateOfficeImageSelected,
    onOfficeImageSelected,
    removeOfficeImage,
    uploadImageMutation,
    deleteImageMutation,
  };
}
