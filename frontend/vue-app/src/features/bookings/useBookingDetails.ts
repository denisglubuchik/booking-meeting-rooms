import { computed, reactive, ref } from "vue";
import dayjs from "dayjs";
import { useMutation, useQuery, useQueryClient } from "@tanstack/vue-query";
import { useRoute } from "vue-router";
import { useI18n } from "vue-i18n";
import {
  addBookingParticipant,
  cancelBooking,
  changeBookingRoom,
  getAvailableRooms,
  getBookingDetails,
  humanizeApiError,
  lookupUsers,
  queryKeys,
  removeBookingParticipant,
  rescheduleBooking,
} from "../../shared/api";
import { useAuthStore } from "../auth/store";
import { useConfirm } from "../ui/confirm";
import { useToast } from "../ui/toast";

export function useBookingDetails() {
  const route = useRoute();
  const auth = useAuthStore();
  const toast = useToast();
  const confirm = useConfirm();
  const queryClient = useQueryClient();
  const { t } = useI18n();

  const bookingId = computed(() => String(route.params.id ?? ""));
  const userSearch = ref("");
  const selectedUserId = ref("");

  const bookingDetailsQuery = useQuery({
    queryKey: computed(() => queryKeys.bookingDetails(bookingId.value)),
    queryFn: () => getBookingDetails(bookingId.value),
    enabled: computed(() => Boolean(bookingId.value)),
  });

  const details = computed(() => bookingDetailsQuery.data.value ?? null);
  const booking = computed(() => details.value?.booking ?? null);
  const room = computed(() => details.value?.room ?? null);
  const office = computed(() => details.value?.office ?? null);
  const participants = computed(() => details.value?.participants ?? []);
  const participantIds = computed(() => new Set(participants.value.map((item) => item.user_id)));

  const myParticipant = computed(
    () => participants.value.find((item) => item.user_id === auth.id) ?? null,
  );
  const canManageParticipants = computed(() => {
    const currentBooking = booking.value;
    if (!currentBooking) return false;
    if (currentBooking.status !== "created") return false;
    return auth.role === "admin" || myParticipant.value?.role === "organizer";
  });
  const canManageBooking = computed(() => {
    const currentBooking = booking.value;
    if (!currentBooking) return false;
    if (currentBooking.status !== "created") return false;
    return auth.role === "admin" || currentBooking.created_by === auth.id;
  });

  const userLookupQuery = useQuery({
    queryKey: computed(() => queryKeys.userLookup(userSearch.value.trim().toLowerCase())),
    queryFn: () => lookupUsers(userSearch.value.trim(), 20),
    enabled: computed(() => userSearch.value.trim().length >= 2 && canManageParticipants.value),
  });

  const suggestedUsers = computed(() =>
    (userLookupQuery.data.value ?? []).filter((item) => !participantIds.value.has(item.id)),
  );

  const addParticipantMutation = useMutation({
    mutationFn: (userId: string) => addBookingParticipant(bookingId.value, userId),
    onSuccess: async (result) => {
      selectedUserId.value = "";
      userSearch.value = "";
      toast.success("Участник добавлен.", { duration: 1400 });
      for (const [index, warning] of result.warnings.entries()) {
        const delayMs = 1500 + index * 250;
        setTimeout(() => {
          toast.info(formatWarningMessage(warning.code, warning.message));
        }, delayMs);
      }
      await queryClient.invalidateQueries({ queryKey: queryKeys.bookingDetails(bookingId.value) });
      await queryClient.invalidateQueries({ queryKey: ["my-bookings"] });
      await queryClient.invalidateQueries({ queryKey: ["admin-bookings"] });
    },
    onError: (error) => {
      toast.error(humanizeApiError(error));
    },
  });

  const removeParticipantMutation = useMutation({
    mutationFn: (userId: string) => removeBookingParticipant(bookingId.value, userId),
    onSuccess: async () => {
      toast.success("Участник удален.");
      await queryClient.invalidateQueries({ queryKey: queryKeys.bookingDetails(bookingId.value) });
      await queryClient.invalidateQueries({ queryKey: ["my-bookings"] });
      await queryClient.invalidateQueries({ queryKey: ["admin-bookings"] });
    },
    onError: (error) => {
      toast.error(humanizeApiError(error));
    },
  });

  const selectedReschedule = ref(false);
  const rescheduleDraft = reactive({
    date: "",
    start: "",
    end: "",
  });
  const rescheduleError = ref("");

  const selectedRoomChange = ref(false);
  const selectedNewRoomId = ref("");

  const availableRoomsForChangeQuery = useQuery({
    queryKey: computed(() => [
      "booking-details-change-rooms",
      booking.value?.id,
      booking.value?.start_time,
      booking.value?.end_time,
      selectedRoomChange.value,
    ]),
    queryFn: async () => {
      if (!booking.value || !selectedRoomChange.value) return [];
      return getAvailableRooms({
        start_time: booking.value.start_time,
        end_time: booking.value.end_time,
      });
    },
    enabled: computed(() => Boolean(booking.value && selectedRoomChange.value)),
  });
  const availableRoomsForChange = computed(() =>
    (availableRoomsForChangeQuery.data.value ?? []).filter((item) => item.id !== booking.value?.room_id),
  );
  const roomChangeError = computed(() =>
    availableRoomsForChangeQuery.error.value ? humanizeApiError(availableRoomsForChangeQuery.error.value) : "",
  );

  const cancelMutation = useMutation({
    mutationFn: () => cancelBooking(bookingId.value),
    onSuccess: async () => {
      toast.success("Бронирование отменено.");
      await queryClient.invalidateQueries({ queryKey: queryKeys.bookingDetails(bookingId.value) });
      await queryClient.invalidateQueries({ queryKey: ["my-bookings"] });
      await queryClient.invalidateQueries({ queryKey: ["admin-bookings"] });
    },
    onError: (error) => {
      toast.error(humanizeApiError(error));
    },
  });

  const rescheduleMutation = useMutation({
    mutationFn: ({ start, end }: { start: string; end: string }) =>
      rescheduleBooking(bookingId.value, start, end),
    onSuccess: async () => {
      selectedReschedule.value = false;
      toast.success("Бронирование перенесено.");
      await queryClient.invalidateQueries({ queryKey: queryKeys.bookingDetails(bookingId.value) });
      await queryClient.invalidateQueries({ queryKey: ["my-bookings"] });
      await queryClient.invalidateQueries({ queryKey: ["admin-bookings"] });
    },
    onError: (error) => {
      toast.error(humanizeApiError(error));
    },
  });

  const roomMutation = useMutation({
    mutationFn: (roomId: string) => changeBookingRoom(bookingId.value, roomId),
    onSuccess: async () => {
      selectedRoomChange.value = false;
      selectedNewRoomId.value = "";
      toast.success("Комната изменена.");
      await queryClient.invalidateQueries({ queryKey: queryKeys.bookingDetails(bookingId.value) });
      await queryClient.invalidateQueries({ queryKey: ["my-bookings"] });
      await queryClient.invalidateQueries({ queryKey: ["admin-bookings"] });
    },
    onError: (error) => {
      toast.error(humanizeApiError(error));
    },
  });

  const isLoading = computed(
    () => bookingDetailsQuery.isLoading.value || bookingDetailsQuery.isFetching.value,
  );
  const lookupLoading = computed(
    () => userLookupQuery.isLoading.value || userLookupQuery.isFetching.value,
  );
  const isMutating = computed(
    () =>
      addParticipantMutation.isPending.value ||
      removeParticipantMutation.isPending.value ||
      cancelMutation.isPending.value ||
      rescheduleMutation.isPending.value ||
      roomMutation.isPending.value,
  );
  const errorText = computed(() =>
    bookingDetailsQuery.error.value ? humanizeApiError(bookingDetailsQuery.error.value) : "",
  );
  const lookupErrorText = computed(() =>
    userLookupQuery.error.value ? humanizeApiError(userLookupQuery.error.value) : "",
  );

  function selectUser(userId: string) {
    selectedUserId.value = userId;
  }

  function formatWarningMessage(code: string, fallbackMessage: string) {
    if (code === "room_capacity_exceeded") {
      const match = fallbackMessage.match(/(\d+)\D+(\d+)/);
      if (match) {
        return t("notifications.warnings.room_capacity_exceeded", {
          count: match[1],
          capacity: match[2],
        });
      }
      return t("notifications.warnings.room_capacity_exceeded_generic");
    }
    return fallbackMessage;
  }

  function addSelectedUser() {
    if (!selectedUserId.value || isMutating.value || !canManageParticipants.value) return;
    addParticipantMutation.mutate(selectedUserId.value);
  }

  function startReschedule() {
    if (!booking.value) return;
    const start = dayjs(booking.value.start_time);
    const end = dayjs(booking.value.end_time);
    selectedReschedule.value = true;
    selectedRoomChange.value = false;
    rescheduleDraft.date = start.format("YYYY-MM-DD");
    rescheduleDraft.start = start.format("HH:mm");
    rescheduleDraft.end = end.format("HH:mm");
    rescheduleError.value = "";
  }

  function cancelReschedule() {
    selectedReschedule.value = false;
    rescheduleError.value = "";
  }

  async function submitReschedule() {
    if (!canManageBooking.value || !booking.value || isMutating.value) return;
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
    const ok = await confirm.ask({
      message: "Сохранить новые дату и время бронирования?",
      confirmText: "Сохранить",
      cancelText: "Отмена",
    });
    if (!ok) return;
    rescheduleMutation.mutate({ start: nextStart.toISOString(), end: nextEnd.toISOString() });
  }

  function startChangeRoom() {
    selectedRoomChange.value = true;
    selectedReschedule.value = false;
    selectedNewRoomId.value = "";
  }

  function cancelChangeRoom() {
    selectedRoomChange.value = false;
    selectedNewRoomId.value = "";
  }

  async function submitChangeRoom() {
    if (!canManageBooking.value || !booking.value || !selectedNewRoomId.value || isMutating.value) return;
    const nextRoom = availableRoomsForChange.value.find((room) => room.id === selectedNewRoomId.value);
    if (!nextRoom) return;
    const ok = await confirm.ask({
      message: `Сменить комнату на ${nextRoom.name}?`,
      confirmText: "Сменить",
      cancelText: "Отмена",
    });
    if (!ok) return;
    roomMutation.mutate(nextRoom.id);
  }

  async function cancelCurrentBooking() {
    if (!canManageBooking.value || !booking.value || isMutating.value) return;
    const ok = await confirm.ask({
      message: "Отменить это бронирование?",
      confirmText: "Отменить",
      cancelText: "Назад",
    });
    if (!ok) return;
    cancelMutation.mutate();
  }

  async function removeParticipant(userId: string, fullName: string, role: string) {
    if (role === "organizer" || isMutating.value || !canManageParticipants.value) return;
    const ok = await confirm.ask({
      message: `Удалить участника ${fullName} из бронирования?`,
      confirmText: "Удалить",
      cancelText: "Отмена",
    });
    if (!ok) return;
    removeParticipantMutation.mutate(userId);
  }

  return {
    bookingId,
    details,
    booking,
    room,
    office,
    participants,
    canManageParticipants,
    canManageBooking,
    userSearch,
    selectedUserId,
    suggestedUsers,
    selectedReschedule,
    rescheduleDraft,
    rescheduleError,
    selectedRoomChange,
    selectedNewRoomId,
    availableRoomsForChange,
    availableRoomsForChangeQuery,
    roomChangeError,
    isLoading,
    lookupLoading,
    isMutating,
    errorText,
    lookupErrorText,
    selectUser,
    addSelectedUser,
    removeParticipant,
    startReschedule,
    cancelReschedule,
    submitReschedule,
    startChangeRoom,
    cancelChangeRoom,
    submitChangeRoom,
    cancelCurrentBooking,
  };
}
