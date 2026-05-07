import { computed, reactive, ref } from "vue";
import dayjs from "dayjs";
import { useMutation, useQuery, useQueryClient } from "@tanstack/vue-query";
import {
  cancelBooking,
  changeBookingRoom,
  getAvailableRooms,
  getMyBookings,
  getRooms,
  humanizeApiError,
  rescheduleBooking,
} from "../../shared/api";
import { formatDateRu, formatTimeRu } from "../../shared/lib/datetime";
import { useConfirm } from "../ui/confirm";
import { useToast } from "../ui/toast";

export function useMyBookings() {
  const toast = useToast();
  const confirm = useConfirm();
  const queryClient = useQueryClient();

  const bookingsQuery = useQuery({
    queryKey: ["my-bookings"],
    queryFn: () => getMyBookings(),
  });

  const roomsQuery = useQuery({
    queryKey: ["rooms-lookup"],
    queryFn: () => getRooms(),
  });

  const bookings = computed(() => bookingsQuery.data.value ?? []);
  const rooms = computed(() => roomsQuery.data.value ?? []);
  const groupedBookings = computed(() => {
    const now = dayjs();
    const upcoming = bookings.value.filter((booking) => booking.status === "created" && dayjs(booking.end_time).isAfter(now));
    const past = bookings.value.filter(
      (booking) =>
        (booking.status === "created" && dayjs(booking.end_time).isBefore(now)) || booking.status === "completed",
    );
    const cancelled = bookings.value.filter((booking) => booking.status === "cancelled");
    return { upcoming, past, cancelled };
  });
  const hasBookings = computed(() => bookings.value.length > 0);
  const isLoading = computed(
    () =>
      bookingsQuery.isLoading.value ||
      bookingsQuery.isFetching.value ||
      roomsQuery.isLoading.value ||
      roomsQuery.isFetching.value,
  );

  const errorText = computed(() => {
    if (bookingsQuery.error.value) return humanizeApiError(bookingsQuery.error.value);
    if (roomsQuery.error.value) return humanizeApiError(roomsQuery.error.value);
    return "";
  });

  function formatDate(value: string) {
    return formatDateRu(value);
  }

  function formatTime(value: string) {
    return formatTimeRu(value);
  }

  function badgeClass(status: string) {
    if (status === "created") return "badge-created";
    if (status === "cancelled") return "badge-cancelled";
    return "badge-completed";
  }

  function roomName(roomId: string) {
    return rooms.value.find((r) => r.id === roomId)?.name || roomId;
  }

  const selectedRescheduleBookingId = ref<string | null>(null);
  const rescheduleDraft = reactive({
    date: "",
    start: "",
    end: "",
  });
  const rescheduleError = ref("");

  const selectedRoomChangeBookingId = ref<string | null>(null);
  const selectedNewRoomId = ref("");

  const selectedRescheduleBooking = computed(() =>
    bookings.value.find((booking) => booking.id === selectedRescheduleBookingId.value) ?? null,
  );
  const selectedRoomChangeBooking = computed(() =>
    bookings.value.find((booking) => booking.id === selectedRoomChangeBookingId.value) ?? null,
  );

  const availableRoomsForChangeQuery = useQuery({
    queryKey: computed(() => [
      "booking-change-rooms",
      selectedRoomChangeBooking.value?.id,
      selectedRoomChangeBooking.value?.start_time,
      selectedRoomChangeBooking.value?.end_time,
    ]),
    queryFn: async () => {
      const booking = selectedRoomChangeBooking.value;
      if (!booking) return [];
      return getAvailableRooms({
        start_time: booking.start_time,
        end_time: booking.end_time,
      });
    },
    enabled: computed(() => Boolean(selectedRoomChangeBooking.value)),
  });
  const availableRoomsForChange = computed(() =>
    (availableRoomsForChangeQuery.data.value ?? []).filter((room) => room.id !== selectedRoomChangeBooking.value?.room_id),
  );
  const roomChangeError = computed(() =>
    availableRoomsForChangeQuery.error.value ? humanizeApiError(availableRoomsForChangeQuery.error.value) : "",
  );

  async function refreshBookings() {
    await queryClient.invalidateQueries({ queryKey: ["my-bookings"] });
  }

  const cancelMutation = useMutation({
    mutationFn: (bookingId: string) => cancelBooking(bookingId),
    onSuccess: async () => {
      toast.success("Бронирование отменено.");
      await refreshBookings();
    },
    onError: (err) => {
      toast.error(humanizeApiError(err));
    },
  });

  const rescheduleMutation = useMutation({
    mutationFn: ({ bookingId, start, end }: { bookingId: string; start: string; end: string }) =>
      rescheduleBooking(bookingId, start, end),
    onSuccess: async () => {
      toast.success("Бронирование перенесено.");
      await refreshBookings();
    },
    onError: (err) => {
      toast.error(humanizeApiError(err));
    },
  });

  const roomMutation = useMutation({
    mutationFn: ({ bookingId, roomId }: { bookingId: string; roomId: string }) =>
      changeBookingRoom(bookingId, roomId),
    onSuccess: async () => {
      toast.success("Комната изменена.");
      await refreshBookings();
    },
    onError: (err) => {
      toast.error(humanizeApiError(err));
    },
  });

  const isMutating = computed(
    () => cancelMutation.isPending.value || rescheduleMutation.isPending.value || roomMutation.isPending.value,
  );

  async function onCancel(bookingId: string) {
    const ok = await confirm.ask({ message: "Отменить это бронирование?", confirmText: "Отменить" });
    if (!ok) return;
    cancelMutation.mutate(bookingId);
  }

  function startReschedule(bookingId: string) {
    const booking = bookings.value.find((b) => b.id === bookingId);
    if (!booking) return;
    const start = dayjs(booking.start_time);
    const end = dayjs(booking.end_time);
    selectedRescheduleBookingId.value = bookingId;
    rescheduleDraft.date = start.format("YYYY-MM-DD");
    rescheduleDraft.start = start.format("HH:mm");
    rescheduleDraft.end = end.format("HH:mm");
    rescheduleError.value = "";
  }

  function cancelReschedule() {
    selectedRescheduleBookingId.value = null;
    rescheduleError.value = "";
  }

  async function submitReschedule() {
    const booking = selectedRescheduleBooking.value;
    if (!booking) return;
    rescheduleError.value = "";
    if (!rescheduleDraft.date || !rescheduleDraft.start || !rescheduleDraft.end) {
      rescheduleError.value = "Заполните дату и время для переноса.";
      return;
    }
    if (rescheduleDraft.start >= rescheduleDraft.end) {
      rescheduleError.value = "Время окончания должно быть позже времени начала.";
      return;
    }
    const nextStart = dayjs(`${rescheduleDraft.date}T${rescheduleDraft.start}:00`);
    const nextEnd = dayjs(`${rescheduleDraft.date}T${rescheduleDraft.end}:00`);
    if (!nextStart.isSame(nextEnd, "day")) {
      rescheduleError.value = "Начало и окончание должны быть в пределах одного дня.";
      return;
    }
    const ok = await confirm.ask({ message: "Сохранить новые дату и время бронирования?", confirmText: "Сохранить" });
    if (!ok) return;
    rescheduleMutation.mutate(
      { bookingId: booking.id, start: nextStart.toISOString(), end: nextEnd.toISOString() },
      {
        onSuccess: () => {
          selectedRescheduleBookingId.value = null;
        },
      },
    );
  }

  function startChangeRoom(bookingId: string) {
    selectedRoomChangeBookingId.value = bookingId;
    selectedNewRoomId.value = "";
  }

  function cancelChangeRoom() {
    selectedRoomChangeBookingId.value = null;
    selectedNewRoomId.value = "";
  }

  async function submitChangeRoom() {
    const booking = selectedRoomChangeBooking.value;
    if (!booking || !selectedNewRoomId.value) return;
    const nextRoom = availableRoomsForChange.value.find((room) => room.id === selectedNewRoomId.value);
    if (!nextRoom) return;
    const ok = await confirm.ask({ message: `Сменить комнату на ${nextRoom.name}?`, confirmText: "Сменить" });
    if (!ok) return;
    roomMutation.mutate(
      { bookingId: booking.id, roomId: nextRoom.id },
      {
        onSuccess: () => {
          selectedRoomChangeBookingId.value = null;
          selectedNewRoomId.value = "";
        },
      },
    );
  }

  return {
    bookings,
    groupedBookings,
    hasBookings,
    isLoading,
    errorText,
    formatDate,
    formatTime,
    badgeClass,
    roomName,
    isMutating,
    onCancel,
    selectedRescheduleBookingId,
    rescheduleDraft,
    rescheduleError,
    startReschedule,
    cancelReschedule,
    submitReschedule,
    selectedRoomChangeBookingId,
    availableRoomsForChange,
    availableRoomsForChangeQuery,
    selectedNewRoomId,
    roomChangeError,
    startChangeRoom,
    cancelChangeRoom,
    submitChangeRoom,
  };
}
