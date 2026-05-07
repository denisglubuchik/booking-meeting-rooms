import type { Office } from "../types/api";
import { apiClient, unwrapData } from "./client";

export async function getOffices(params?: { is_active?: boolean; city?: string; limit?: number; offset?: number }) {
  const result = await apiClient.GET("/offices/", {
    params: {
      query: {
        is_active: params?.is_active,
        city: params?.city,
        limit: params?.limit,
        offset: params?.offset,
      },
    },
  });
  return unwrapData(result) as Promise<Office[]>;
}

export async function getOfficeById(officeId: string) {
  const result = await apiClient.GET("/offices/{office_id}", {
    params: { path: { office_id: officeId } },
  });
  return unwrapData(result) as Promise<Office>;
}

export async function createOffice(payload: { name: string; city: string; address: string }) {
  const result = await apiClient.POST("/offices/", { body: payload });
  return unwrapData(result) as Promise<Office>;
}

export async function updateOffice(officeId: string, payload: { name?: string; city?: string; address?: string }) {
  const result = await apiClient.PATCH("/offices/{office_id}", {
    params: { path: { office_id: officeId } },
    body: payload,
  });
  return unwrapData(result) as Promise<Office>;
}

export async function activateOffice(officeId: string) {
  const result = await apiClient.POST("/offices/{office_id}/activate", {
    params: { path: { office_id: officeId } },
  });
  return unwrapData(result) as Promise<Office>;
}

export async function deactivateOffice(officeId: string) {
  const result = await apiClient.POST("/offices/{office_id}/deactivate", {
    params: { path: { office_id: officeId } },
  });
  return unwrapData(result) as Promise<Office>;
}

export async function deleteOfficeImage(officeId: string) {
  const result = await apiClient.DELETE("/offices/{office_id}/image", {
    params: { path: { office_id: officeId } },
  });
  if (!result.response.ok) {
    await unwrapData(result);
  }
}

export async function setOfficeImage(officeId: string, file: File) {
  const result = await apiClient.POST("/offices/{office_id}/image", {
    params: { path: { office_id: officeId } },
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
