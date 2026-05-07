import type { Room } from "../types/api";
import { apiClient, unwrapData } from "./client";

export async function getRooms(params?: {
  office_id?: string;
  floor?: number;
  is_active?: boolean;
  capacity_gte?: number;
  capacity_lte?: number;
  limit?: number;
  offset?: number;
}) {
  if (params?.office_id) {
    return getRoomsByOffice(params.office_id, {
      is_active: params.is_active,
      floor: params.floor,
      capacity_gte: params.capacity_gte,
      capacity_lte: params.capacity_lte,
      limit: params.limit,
      offset: params.offset,
    });
  }

  const result = await apiClient.GET("/rooms/", {
    params: {
      query: {
        is_active: params?.is_active,
        capacity_gte: params?.capacity_gte,
        capacity_lte: params?.capacity_lte,
        limit: params?.limit,
        offset: params?.offset,
      },
    },
  });
  return unwrapData(result) as Promise<Room[]>;
}

export async function getRoomsByOffice(
  officeId: string,
  params?: {
    is_active?: boolean;
    floor?: number;
    capacity_gte?: number;
    capacity_lte?: number;
    limit?: number;
    offset?: number;
  },
) {
  const result = await apiClient.GET("/rooms/by-office/{office_id}", {
    params: {
      path: { office_id: officeId },
      query: {
        is_active: params?.is_active,
        floor: params?.floor,
        capacity_gte: params?.capacity_gte,
        capacity_lte: params?.capacity_lte,
        limit: params?.limit,
        offset: params?.offset,
      },
    },
  });
  return unwrapData(result) as Promise<Room[]>;
}

export async function getRoomById(roomId: string) {
  const result = await apiClient.GET("/rooms/{room_id}", {
    params: { path: { room_id: roomId } },
  });
  return unwrapData(result) as Promise<Room>;
}

export async function createRoom(payload: {
  office_id: string;
  name: string;
  floor: number;
  capacity: number;
  description: string;
  equipment: string[];
}) {
  const result = await apiClient.POST("/rooms/", { body: payload });
  return unwrapData(result) as Promise<Room>;
}

export async function updateRoom(roomId: string, payload: { name: string; description: string; equipment: string[] }) {
  const result = await apiClient.PATCH("/rooms/{room_id}", {
    params: { path: { room_id: roomId } },
    body: payload,
  });
  return unwrapData(result) as Promise<Room>;
}

export async function activateRoom(roomId: string) {
  const result = await apiClient.POST("/rooms/{room_id}/activate", {
    params: { path: { room_id: roomId } },
  });
  return unwrapData(result) as Promise<Room>;
}

export async function deactivateRoom(roomId: string) {
  const result = await apiClient.POST("/rooms/{room_id}/deactivate", {
    params: { path: { room_id: roomId } },
  });
  return unwrapData(result) as Promise<Room>;
}

export async function deleteRoomImage(roomId: string) {
  const result = await apiClient.DELETE("/rooms/{room_id}/image", {
    params: { path: { room_id: roomId } },
  });
  if (!result.response.ok) {
    await unwrapData(result);
  }
}

export async function setRoomImage(roomId: string, file: File) {
  const result = await apiClient.POST("/rooms/{room_id}/image", {
    params: { path: { room_id: roomId } },
    body: { image: file as unknown as string },
    bodySerializer(body) {
      const formData = new FormData();
      formData.append("image", body.image as unknown as Blob);
      return formData;
    },
  });
  if (!result.response.ok) {
    await unwrapData(result);
  }
}
