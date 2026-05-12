import type { User } from "../types/api";
import { apiClient, unwrapData, ApiError } from "./client";

export async function login(email: string, password: string) {
  const result = await apiClient.POST("/auth/login", {
    body: { email, password },
  });
  try {
    return (await unwrapData(result)) as { access_token: string };
  } catch (error) {
    if (error instanceof ApiError) {
      throw new ApiError(error.status, "Ошибка входа", error.details, error.code);
    }
    throw error;
  }
}

export async function register(payload: { full_name: string; email: string; password: string }) {
  const result = await apiClient.POST("/users/register", { body: payload });
  return unwrapData(result) as Promise<User>;
}

export async function me() {
  const result = await apiClient.GET("/users/me");
  return unwrapData(result) as Promise<User>;
}

export async function updateMe(payload: { full_name: string; email: string }) {
  const result = await apiClient.PATCH("/users/me", { body: payload });
  return unwrapData(result) as Promise<User>;
}

export async function logout() {
  const result = await apiClient.POST("/auth/logout");
  if (!result.response.ok) {
    throw new ApiError(result.response.status, "Не удалось завершить сессию");
  }
}

export async function getSessions() {
  const result = await apiClient.GET("/auth/sessions", {
    params: { query: { isActive: true } },
  });
  return unwrapData(result) as Promise<
    {
      id: string;
      expires_at: string;
      revoked_at: string | null;
      created_at: string;
      user_agent: string | null;
      ip: string | null;
    }[]
  >;
}

export async function revokeSession(sessionId: string) {
  const result = await apiClient.POST("/auth/sessions/{session_id}/revoke", {
    params: { path: { session_id: sessionId } },
  });
  if (!result.response.ok) {
    throw new ApiError(result.response.status, "Не удалось отозвать сессию");
  }
}
