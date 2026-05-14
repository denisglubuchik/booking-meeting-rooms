import type {
  AddBookingParticipantResult,
  Booking,
  BookingDetails,
  BookingHistory,
  BookingParticipant,
  Room,
} from "../types/api";
import { apiClient, unwrapData } from "./client";

export async function getAvailableRooms(params: {
  start_time: string;
  end_time: string;
  office_id?: string;
  floor?: number;
  capacity_gte?: number;
  capacity_lte?: number;
}) {
  const result = await apiClient.GET("/bookings/available-rooms", {
    params: {
      query: {
        start_time: params.start_time,
        end_time: params.end_time,
        office_id: params.office_id,
        floor: params.floor,
        capacity_gte: params.capacity_gte,
        capacity_lte: params.capacity_lte,
      },
    },
  });
  return unwrapData(result) as Promise<Room[]>;
}

export async function getRoomBookings(roomId: string) {
  const result = await apiClient.GET("/bookings/by-room/{room_id}", {
    params: { path: { room_id: roomId } },
  });
  return unwrapData(result) as Promise<Booking[]>;
}

export async function getMyBookings(params?: {
  room_id?: string;
  status?: "created" | "cancelled" | "completed";
  start_time_gte?: string;
  end_time_lte?: string;
  sort_by?: "start_time" | "end_time";
  sort_order?: "asc" | "desc";
  limit?: number;
  offset?: number;
}) {
  const result = await apiClient.GET("/bookings/my-bookings", {
    params: {
      query: {
        room_id: params?.room_id,
        status: params?.status,
        start_time_gte: params?.start_time_gte,
        end_time_lte: params?.end_time_lte,
        sort_by: params?.sort_by,
        sort_order: params?.sort_order,
        limit: params?.limit,
        offset: params?.offset,
      },
    },
  });
  return unwrapData(result) as Promise<Booking[]>;
}

export async function getBookingDetails(bookingId: string) {
  const result = await apiClient.GET("/bookings/{booking_id}", {
    params: { path: { booking_id: bookingId } },
  });
  return unwrapData(result) as Promise<BookingDetails>;
}

export async function getAllBookings(params?: {
  user_id?: string;
  room_id?: string;
  status?: "created" | "cancelled" | "completed";
  start_time_gte?: string;
  end_time_lte?: string;
  limit?: number;
  offset?: number;
}) {
  const result = await apiClient.GET("/bookings/", {
    params: {
      query: {
        user_id: params?.user_id,
        room_id: params?.room_id,
        status: params?.status,
        start_time_gte: params?.start_time_gte,
        end_time_lte: params?.end_time_lte,
        limit: params?.limit,
        offset: params?.offset,
      },
    },
  });
  return unwrapData(result) as Promise<Booking[]>;
}

export async function getBookingHistory(params?: {
  booking_id?: string;
  action?: "created" | "cancelled" | "completed" | "updated" | "rescheduled";
  performed_by?: string;
  created_at_gte?: string;
  created_at_lte?: string;
  limit?: number;
  offset?: number;
}) {
  const result = await apiClient.GET("/bookings/history", {
    params: {
      query: {
        booking_id: params?.booking_id,
        action: params?.action,
        performed_by: params?.performed_by,
        created_at_gte: params?.created_at_gte,
        created_at_lte: params?.created_at_lte,
        limit: params?.limit,
        offset: params?.offset,
      },
    },
  });
  return unwrapData(result) as Promise<BookingHistory[]>;
}

export async function createBooking(payload: {
  room_id: string;
  start_time: string;
  end_time: string;
  title?: string | null;
}) {
  const result = await apiClient.POST("/bookings/", { body: payload });
  return unwrapData(result) as Promise<Booking>;
}

export async function cancelBooking(bookingId: string) {
  const result = await apiClient.POST("/bookings/{booking_id}/cancel", {
    params: { path: { booking_id: bookingId } },
  });
  return unwrapData(result) as Promise<Booking>;
}

export async function rescheduleBooking(bookingId: string, new_start_time: string, new_end_time: string) {
  const result = await apiClient.PATCH("/bookings/{booking_id}/reschedule", {
    params: { path: { booking_id: bookingId } },
    body: { new_start_time, new_end_time },
  });
  return unwrapData(result) as Promise<Booking>;
}

export async function changeBookingRoom(bookingId: string, new_room_id: string) {
  const result = await apiClient.PATCH("/bookings/{booking_id}/change_room", {
    params: { path: { booking_id: bookingId } },
    body: { new_room_id },
  });
  return unwrapData(result) as Promise<Booking>;
}

export async function addBookingParticipant(bookingId: string, user_id: string) {
  const result = await apiClient.POST("/bookings/{booking_id}/participants", {
    params: { path: { booking_id: bookingId } },
    body: { user_id },
  });
  return unwrapData(result) as unknown as Promise<AddBookingParticipantResult>;
}

export async function removeBookingParticipant(bookingId: string, userId: string) {
  const result = await apiClient.DELETE("/bookings/{booking_id}/participants/{user_id}", {
    params: { path: { booking_id: bookingId, user_id: userId } },
  });
  if (!result.response.ok) {
    await unwrapData(result);
  }
}
