import type { User, UserLookup } from "../types/api";
import { apiClient, unwrapData } from "./client";

export async function getUsers(params?: {
  is_active?: boolean;
  role?: "employee" | "admin";
  created_at_gte?: string;
  created_at_lte?: string;
  limit?: number;
  offset?: number;
}) {
  const result = await apiClient.GET("/users/", {
    params: {
      query: {
        is_active: params?.is_active,
        role: params?.role,
        created_at_gte: params?.created_at_gte,
        created_at_lte: params?.created_at_lte,
        limit: params?.limit,
        offset: params?.offset,
      },
    },
  });
  return unwrapData(result) as Promise<User[]>;
}

export async function lookupUsers(query: string, limit = 20) {
  const result = await apiClient.GET("/users/lookup", {
    params: { query: { query, limit } },
  });
  return unwrapData(result) as Promise<UserLookup[]>;
}

export async function activateUser(userId: string) {
  const result = await apiClient.POST("/users/{user_id}/activate", {
    params: { path: { user_id: userId } },
  });
  return unwrapData(result) as Promise<User>;
}

export async function deactivateUser(userId: string) {
  const result = await apiClient.POST("/users/{user_id}/deactivate", {
    params: { path: { user_id: userId } },
  });
  return unwrapData(result) as Promise<User>;
}

export async function promoteToAdmin(userId: string) {
  const result = await apiClient.POST("/users/{user_id}/promote-to-admin", {
    params: { path: { user_id: userId } },
  });
  return unwrapData(result) as Promise<User>;
}

export async function demoteToEmployee(userId: string) {
  const result = await apiClient.POST("/users/{user_id}/demote-to-employee", {
    params: { path: { user_id: userId } },
  });
  return unwrapData(result) as Promise<User>;
}
