import { computed, ref, watchEffect } from "vue";
import { useMutation, useQuery } from "@tanstack/vue-query";
import { toTypedSchema } from "@vee-validate/zod";
import { useForm } from "vee-validate";
import { useRoute, useRouter } from "vue-router";
import { z } from "zod";
import { createBooking, getOffices, getRooms, humanizeApiError } from "../../shared/api";
import { isValidTime24h } from "../../shared/lib/time";
import { useToast } from "../ui/toast";

function toIso(date: string, time: string) {
  return `${date}T${time}:00`;
}

export function useCreateBooking() {
  const route = useRoute();
  const router = useRouter();
  const toast = useToast();
  const success = ref("");

  const now = new Date();
  const schema = toTypedSchema(
    z
      .object({
        room_id: z.string().min(1, "Выберите комнату."),
        date: z.string().min(1, "Выберите дату."),
        start: z.string().min(1, "Выберите время начала."),
        end: z.string().min(1, "Выберите время окончания."),
        title: z.string().optional(),
      })
      .refine((v) => isValidTime24h(v.start), {
        path: ["start"],
        message: "Введите время в формате 24 часа, например 15:30.",
      })
      .refine((v) => isValidTime24h(v.end), {
        path: ["end"],
        message: "Введите время в формате 24 часа, например 16:30.",
      })
      .refine((v) => v.start < v.end, {
        path: ["end"],
        message: "Время окончания должно быть позже начала.",
      })
      .refine((v) => !!v.date, {
        path: ["date"],
        message: "Выберите дату.",
      }),
  );

  const { defineField, errors, handleSubmit, setFieldValue } = useForm({
    validationSchema: schema,
    initialValues: {
      room_id: "",
      date: now.toISOString().slice(0, 10),
      start: "15:30",
      end: "16:30",
      title: "",
    },
  });

  const [roomId] = defineField("room_id");
  const [date] = defineField("date");
  const [start] = defineField("start");
  const [end] = defineField("end");
  const [title] = defineField("title");

  const officeId = computed(() => {
    const value = route.query.officeId;
    return typeof value === "string" ? value : "";
  });
  const floor = computed(() => {
    const value = route.query.floor;
    if (typeof value !== "string" || !value) return undefined;
    const next = Number(value);
    return Number.isFinite(next) ? next : undefined;
  });
  const capacityGte = computed(() => {
    const value = route.query.capacityGte;
    if (typeof value !== "string" || !value) return undefined;
    const next = Number(value);
    return Number.isFinite(next) ? next : undefined;
  });
  const capacityLte = computed(() => {
    const value = route.query.capacityLte;
    if (typeof value !== "string" || !value) return undefined;
    const next = Number(value);
    return Number.isFinite(next) ? next : undefined;
  });

  const roomsQuery = useQuery({
    queryKey: computed(() => [
      "booking-rooms",
      {
        office_id: officeId.value,
        floor: floor.value,
        capacity_gte: capacityGte.value,
        capacity_lte: capacityLte.value,
      },
    ]),
    queryFn: () =>
      getRooms({
        is_active: true,
        office_id: officeId.value || undefined,
        floor: floor.value,
        capacity_gte: capacityGte.value,
        capacity_lte: capacityLte.value,
      }),
  });
  const officesQuery = useQuery({
    queryKey: ["booking-offices"],
    queryFn: () => getOffices({ is_active: true }),
  });

  const rooms = computed(() => roomsQuery.data.value ?? []);
  const selectedRoom = computed(() => rooms.value.find((room) => room.id === roomId.value));
  const selectedOffice = computed(() => offices.value.find((office) => office.id === selectedRoom.value?.office_id));
  const isLoading = computed(
    () =>
      roomsQuery.isLoading.value ||
      roomsQuery.isFetching.value ||
      officesQuery.isLoading.value ||
      officesQuery.isFetching.value,
  );
  const errorText = computed(() => {
    if (roomsQuery.error.value) return humanizeApiError(roomsQuery.error.value);
    if (officesQuery.error.value) return humanizeApiError(officesQuery.error.value);
    return "";
  });
  const firstError = computed(
    () => errors.value.room_id || errors.value.date || errors.value.start || errors.value.end || "",
  );

  watchEffect(() => {
    const queryRoomId = route.query.roomId;
    if (typeof queryRoomId === "string" && rooms.value.some((room) => room.id === queryRoomId)) {
      setFieldValue("room_id", queryRoomId);
    }
  });
  const offices = computed(() => officesQuery.data.value ?? []);

  watchEffect(() => {
    const queryDate = route.query.date;
    if (typeof queryDate === "string" && queryDate) setFieldValue("date", queryDate);
    const queryStart = route.query.start;
    if (typeof queryStart === "string" && queryStart) setFieldValue("start", queryStart);
    const queryEnd = route.query.end;
    if (typeof queryEnd === "string" && queryEnd) setFieldValue("end", queryEnd);
  });

  const createMutation = useMutation({
    mutationFn: (values: { room_id: string; date: string; start: string; end: string; title?: string }) =>
      createBooking({
        room_id: values.room_id,
        start_time: toIso(values.date, values.start),
        end_time: toIso(values.date, values.end),
        title: values.title?.trim() ? values.title.trim() : null,
      }),
    onSuccess: async () => {
      success.value = "Бронирование создано.";
      toast.success("Бронирование успешно создано.");
      await router.push("/my-bookings");
    },
    onError: (err) => {
      toast.error(humanizeApiError(err));
    },
  });

  const onSubmit = handleSubmit((values) => {
    createMutation.mutate(values);
  });

  return {
    roomId,
    date,
    start,
    end,
    title,
    rooms,
    offices,
    selectedOffice,
    selectedRoom,
    isLoading,
    errorText,
    firstError,
    success,
    createMutation,
    onSubmit,
  };
}
