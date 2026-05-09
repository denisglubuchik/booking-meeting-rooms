import { computed, reactive } from "vue";
import { useQuery } from "@tanstack/vue-query";
import { toTypedSchema } from "@vee-validate/zod";
import { useForm } from "vee-validate";
import { z } from "zod";
import { useRoute } from "vue-router";
import { getAvailableRooms, getOffices, humanizeApiError } from "../../shared/api";
import { isValidTime24h } from "../../shared/lib/time";

function minutesFromTime(timeStr: string) {
  const [hours = "0", minutes = "0"] = timeStr.split(":");
  return Number(hours) * 60 + Number(minutes);
}

function addDays(dateStr: string, days: number) {
  const date = new Date(`${dateStr}T00:00:00`);
  date.setDate(date.getDate() + days);
  return date.toISOString().slice(0, 10);
}

function toIsoRange(dateStr: string, startTime: string, endTime: string) {
  const startMinutes = minutesFromTime(startTime);
  const endMinutes = minutesFromTime(endTime);
  const endDate = endMinutes <= startMinutes ? addDays(dateStr, 1) : dateStr;
  return {
    start_time: `${dateStr}T${startTime}:00`,
    end_time: `${endDate}T${endTime}:00`,
  };
}

export function useFindRoom() {
  const route = useRoute();
  const now = new Date();
  const initialDate = now.toISOString().slice(0, 10);
  const initialStart = typeof route.query.start === "string" ? route.query.start : "14:00";
  const initialEnd = typeof route.query.end === "string" ? route.query.end : "15:00";
  const initialOfficeId = typeof route.query.officeId === "string" ? route.query.officeId : "";
  const queryDate = typeof route.query.date === "string" ? route.query.date : initialDate;
  const initialFloor = typeof route.query.floor === "string" ? Number(route.query.floor) : undefined;
  const isDashboardSearch = route.query.source === "dashboard";
  const initialCapacityGte =
    typeof route.query.capacityGte === "string" ? Number(route.query.capacityGte) : isDashboardSearch ? undefined : 6;
  const initialCapacityLte = typeof route.query.capacityLte === "string" ? Number(route.query.capacityLte) : undefined;

  const schema = toTypedSchema(
    z
      .object({
        office_id: z.string().optional(),
        date: z.string().min(1, "Выберите дату."),
        startTime: z.string().min(1, "Выберите время начала."),
        endTime: z.string().min(1, "Выберите время окончания."),
        floor: z.number().int().min(0).optional(),
        capacity_gte: z.number().int().min(1).optional(),
        capacity_lte: z.number().int().min(1).optional(),
      })
      .refine((v) => isValidTime24h(v.startTime), {
        path: ["startTime"],
        message: "Введите время в формате 24 часа, например 15:30.",
      })
      .refine((v) => isValidTime24h(v.endTime), {
        path: ["endTime"],
        message: "Введите время в формате 24 часа, например 16:30.",
      })
      .refine((v) => v.startTime !== v.endTime, {
        path: ["endTime"],
        message: "Время начала и окончания не должны совпадать.",
      })
      .refine(
        (v) =>
          !(typeof v.capacity_gte === "number" && typeof v.capacity_lte === "number") ||
          v.capacity_gte <= v.capacity_lte,
        {
          path: ["capacity_lte"],
          message: "Минимальная вместимость не может быть больше максимальной.",
        },
      )
      .refine((v) => v.date.length > 0, {
        path: ["date"],
        message: "Выберите дату.",
      }),
  );

  const { defineField, handleSubmit, errors } = useForm({
    validationSchema: schema,
    initialValues: {
      office_id: initialOfficeId,
      date: queryDate,
      startTime: initialStart,
      endTime: initialEnd,
      floor: Number.isFinite(initialFloor) ? initialFloor : undefined,
      capacity_gte: Number.isFinite(initialCapacityGte) ? initialCapacityGte : undefined,
      capacity_lte: Number.isFinite(initialCapacityLte) ? initialCapacityLte : undefined,
    },
  });

  const [office_id] = defineField("office_id");
  const [date] = defineField("date");
  const [startTime] = defineField("startTime");
  const [endTime] = defineField("endTime");
  const [floor] = defineField("floor");
  const [capacity_gte] = defineField("capacity_gte");
  const [capacity_lte] = defineField("capacity_lte");

  const draft = reactive({ office_id, date, startTime, endTime, floor, capacity_gte, capacity_lte });
  const applied = reactive({
    office_id: initialOfficeId,
    date: queryDate,
    startTime: initialStart,
    endTime: initialEnd,
    floor: Number.isFinite(initialFloor) ? initialFloor : (undefined as number | undefined),
    capacity_gte: Number.isFinite(initialCapacityGte) ? initialCapacityGte : (undefined as number | undefined),
    capacity_lte: Number.isFinite(initialCapacityLte) ? initialCapacityLte : (undefined as number | undefined),
  });

  const officeFilterValue = computed({
    get: () => draft.office_id || "__all",
    set: (value: string) => {
      draft.office_id = value === "__all" ? "" : value;
    },
  });

  const officesQuery = useQuery({
    queryKey: ["find-room-offices"],
    queryFn: () => getOffices({ is_active: true }),
  });

  const firstError = computed(
    () =>
      errors.value.office_id ||
      errors.value.date ||
      errors.value.startTime ||
      errors.value.endTime ||
      errors.value.floor ||
      errors.value.capacity_gte ||
      errors.value.capacity_lte ||
      "",
  );

  const roomsQuery = useQuery({
    queryKey: computed(() => ["find-room", { ...applied }]),
    queryFn: () =>
      getAvailableRooms({
        ...toIsoRange(applied.date, applied.startTime, applied.endTime),
        office_id: applied.office_id || undefined,
        floor: applied.floor,
        capacity_gte: applied.capacity_gte,
        capacity_lte: applied.capacity_lte,
      }),
  });

  const offices = computed(() => officesQuery.data.value ?? []);
  const rooms = computed(() => roomsQuery.data.value ?? []);
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

  const search = handleSubmit((values) => {
    applied.office_id = values.office_id ?? draft.office_id ?? "";
    applied.date = values.date ?? draft.date ?? initialDate;
    applied.startTime = values.startTime ?? draft.startTime ?? "14:00";
    applied.endTime = values.endTime ?? draft.endTime ?? "15:00";
    applied.floor = typeof values.floor === "number" ? Math.max(0, Number(values.floor) || 0) : undefined;
    applied.capacity_gte =
      typeof values.capacity_gte === "number" ? Math.max(1, Number(values.capacity_gte) || 1) : undefined;
    applied.capacity_lte =
      typeof values.capacity_lte === "number" ? Math.max(1, Number(values.capacity_lte) || 1) : undefined;
  });

  return { draft, applied, officeFilterValue, offices, firstError, rooms, isLoading, errorText, search };
}
