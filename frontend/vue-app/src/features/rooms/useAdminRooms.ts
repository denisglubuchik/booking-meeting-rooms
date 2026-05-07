import { computed, reactive, ref } from "vue";
import { useMutation, useQuery, useQueryClient } from "@tanstack/vue-query";
import { toTypedSchema } from "@vee-validate/zod";
import { useForm } from "vee-validate";
import { z } from "zod";
import {
  activateRoom,
  createRoom,
  deleteRoomImage,
  deactivateRoom,
  getOffices,
  getRooms,
  humanizeApiError,
  queryKeys,
  setRoomImage,
  updateRoom,
} from "../../shared/api";
import type { Room } from "../../shared/types/api";
import { useConfirm } from "../ui/confirm";
import { useToast } from "../ui/toast";

export function useAdminRooms() {
  const toast = useToast();
  const confirm = useConfirm();
  const queryClient = useQueryClient();

  const showCreate = ref(false);
  const editingRoomId = ref<string | null>(null);
  const createImageFile = ref<File | null>(null);
  const allowedMimeTypes = new Set(["image/jpeg", "image/png", "image/webp"]);
  const createSchema = toTypedSchema(
    z.object({
      office_id: z.string().min(1, "Выберите офис."),
      name: z.string().trim().min(2, "Введите название комнаты."),
      floor: z.number().int().min(0, "Этаж не может быть отрицательным."),
      capacity: z.number().int().min(1, "Вместимость должна быть больше 0."),
      description: z.string().trim().min(3, "Введите описание."),
      equipment: z.string().trim().min(1, "Укажите оснащение."),
    }),
  );
  const editSchema = toTypedSchema(
    z.object({
      name: z.string().trim().min(2, "Введите название комнаты."),
      description: z.string().trim().min(3, "Введите описание."),
      equipment: z.string().trim().min(1, "Укажите оснащение."),
    }),
  );
  const filtersSchema = toTypedSchema(
    z
      .object({
        capacity_gte: z.number().int().min(1).optional(),
        capacity_lte: z.number().int().min(1).optional(),
      })
      .refine(
        (v) =>
          !(typeof v.capacity_gte === "number" && typeof v.capacity_lte === "number") ||
          v.capacity_gte <= v.capacity_lte,
        { message: "Минимальная вместимость не может быть больше максимальной.", path: ["capacity_lte"] },
      ),
  );

  const {
    defineField: defineCreateField,
    handleSubmit: handleCreateSubmit,
    setValues: setCreateValues,
    errors: createErrors,
  } = useForm({
    validationSchema: createSchema,
    initialValues: {
      office_id: "",
      name: "",
      floor: 1,
      capacity: 4,
      description: "",
      equipment: "экран, видеосвязь",
    },
  });
  const [createOfficeId] = defineCreateField("office_id");
  const [createName] = defineCreateField("name");
  const [createFloor] = defineCreateField("floor");
  const [createCapacity] = defineCreateField("capacity");
  const [createDescription] = defineCreateField("description");
  const [createEquipment] = defineCreateField("equipment");

  const {
    defineField: defineEditField,
    handleSubmit: handleEditSubmit,
    setValues: setEditValues,
    errors: editErrors,
  } = useForm({
    validationSchema: editSchema,
    initialValues: { name: "", description: "", equipment: "" },
  });
  const [editName] = defineEditField("name");
  const [editDescription] = defineEditField("description");
  const [editEquipment] = defineEditField("equipment");

  const { handleSubmit: handleFilterSubmit, errors: filterErrors } = useForm({
    validationSchema: filtersSchema,
    initialValues: { capacity_gte: undefined, capacity_lte: undefined },
  });

  const draftFilters = reactive({
    office_id: "",
    is_active: "",
    floor: undefined as number | undefined,
    capacity_gte: undefined as number | undefined,
    capacity_lte: undefined as number | undefined,
  });

  const appliedFilters = reactive({
    office_id: "",
    is_active: "",
    floor: undefined as number | undefined,
    capacity_gte: undefined as number | undefined,
    capacity_lte: undefined as number | undefined,
  });

  const officeFilterValue = computed({
    get: () => draftFilters.office_id || "__all",
    set: (value: string) => {
      draftFilters.office_id = value === "__all" ? "" : value;
    },
  });

  const activeFilterValue = computed({
    get: () => draftFilters.is_active || "__all",
    set: (value: string) => {
      draftFilters.is_active = value === "__all" ? "" : value;
    },
  });

  const officesQuery = useQuery({
    queryKey: queryKeys.officesLookup,
    queryFn: () => getOffices(),
  });

  function roomQueryFilters() {
    return {
      office_id: appliedFilters.office_id || undefined,
      is_active: appliedFilters.is_active === "" ? undefined : appliedFilters.is_active === "true",
      floor: typeof appliedFilters.floor === "number" ? appliedFilters.floor : undefined,
      capacity_gte: typeof appliedFilters.capacity_gte === "number" ? appliedFilters.capacity_gte : undefined,
      capacity_lte: typeof appliedFilters.capacity_lte === "number" ? appliedFilters.capacity_lte : undefined,
    };
  }

  const roomsQuery = useQuery({
    queryKey: computed(() => queryKeys.adminRooms({ ...appliedFilters })),
    queryFn: () => getRooms(roomQueryFilters()),
  });

  const offices = computed(() => officesQuery.data.value ?? []);
  const rooms = computed(() => roomsQuery.data.value ?? []);

  const filteredRooms = computed(() => rooms.value);
  function officeName(officeId: string) {
    return offices.value.find((office) => office.id === officeId)?.name || officeId;
  }

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

  async function refreshRooms() {
    await queryClient.invalidateQueries({ queryKey: ["admin-rooms"] });
  }

  const createMutation = useMutation({
    mutationFn: (values: {
      office_id: string;
      name: string;
      floor: number;
      capacity: number;
      description: string;
      equipment: string;
    }) =>
      createRoom({
        office_id: values.office_id,
        name: values.name.trim(),
        floor: values.floor,
        capacity: values.capacity,
        description: values.description.trim(),
        equipment: values.equipment.split(",").map((i) => i.trim()).filter(Boolean),
      }),
    onSuccess: async () => {
      setCreateValues({
        office_id: "",
        name: "",
        floor: 1,
        capacity: 4,
        description: "",
        equipment: "экран, видеосвязь",
      });
      showCreate.value = false;
      toast.success("Комната создана.");
      await refreshRooms();
    },
    onError: (err) => toast.error(humanizeApiError(err)),
  });

  const updateMutation = useMutation({
    mutationFn: ({ roomId, values }: { roomId: string; values: { name: string; description: string; equipment: string } }) =>
      updateRoom(roomId, {
        name: values.name.trim(),
        description: values.description.trim(),
        equipment: values.equipment.split(",").map((i) => i.trim()).filter(Boolean),
      }),
    onSuccess: async () => {
      editingRoomId.value = null;
      toast.success("Комната обновлена.");
      await refreshRooms();
    },
    onError: (err) => toast.error(humanizeApiError(err)),
  });

  const toggleMutation = useMutation({
    mutationFn: (room: Room) => (room.is_active ? deactivateRoom(room.id) : activateRoom(room.id)),
    onSuccess: async (_, room) => {
      toast.success(`Комната ${room.is_active ? "деактивирована" : "активирована"}.`);
      await refreshRooms();
    },
    onError: (err) => toast.error(humanizeApiError(err)),
  });

  const uploadImageMutation = useMutation({
    mutationFn: ({ roomId, file }: { roomId: string; file: File }) => setRoomImage(roomId, file),
    onSuccess: async () => {
      toast.success("Изображение комнаты обновлено.");
      await refreshRooms();
    },
    onError: (err) => toast.error(humanizeApiError(err)),
  });

  const deleteImageMutation = useMutation({
    mutationFn: (roomId: string) => deleteRoomImage(roomId),
    onSuccess: async () => {
      toast.success("Изображение комнаты удалено.");
      await refreshRooms();
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
    handleFilterSubmit(() => {
      appliedFilters.office_id = draftFilters.office_id;
      appliedFilters.is_active = draftFilters.is_active;
      appliedFilters.floor = draftFilters.floor;
      appliedFilters.capacity_gte = draftFilters.capacity_gte;
      appliedFilters.capacity_lte = draftFilters.capacity_lte;
    })();
  }

  function resetFilters() {
    draftFilters.office_id = "";
    draftFilters.is_active = "";
    draftFilters.floor = undefined;
    draftFilters.capacity_gte = undefined;
    draftFilters.capacity_lte = undefined;
    applyFilters();
  }

  function startEdit(room: Room) {
    editingRoomId.value = room.id;
    setEditValues({ name: room.name, description: room.description, equipment: room.equipment.join(", ") });
  }

  function cancelEdit() {
    editingRoomId.value = null;
  }

  const onCreate = handleCreateSubmit(async (values) => {
    const room = await createMutation.mutateAsync(values);
    if (createImageFile.value) {
      await uploadImageMutation.mutateAsync({ roomId: room.id, file: createImageFile.value });
      createImageFile.value = null;
    }
  });

  function onSaveEdit(roomId: string) {
    handleEditSubmit((values) => {
      updateMutation.mutate({ roomId, values });
    })();
  }

  async function toggleActive(room: Room) {
    const action = room.is_active ? "деактивировать" : "активировать";
    const ok = await confirm.ask({
      message: `Вы уверены, что хотите ${action} комнату?`,
      confirmText: room.is_active ? "Деактивировать" : "Активировать",
    });
    if (!ok) return;
    toggleMutation.mutate(room);
  }

  function onRoomImageSelected(room: Room, event: Event) {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;
    if (!allowedMimeTypes.has(file.type)) {
      toast.error("Поддерживаются только JPEG, PNG и WEBP.");
      input.value = "";
      return;
    }
    uploadImageMutation.mutate({ roomId: room.id, file });
    input.value = "";
  }

  function onCreateRoomImageSelected(event: Event) {
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

  async function removeRoomImage(room: Room) {
    if (!room.image_url) return;
    const ok = await confirm.ask({
      message: "Удалить изображение комнаты?",
      confirmText: "Удалить",
    });
    if (!ok) return;
    deleteImageMutation.mutate(room.id);
  }

  return {
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
    createImageFile,
    onCreateRoomImageSelected,
    onRoomImageSelected,
    removeRoomImage,
    uploadImageMutation,
    deleteImageMutation,
  };
}
