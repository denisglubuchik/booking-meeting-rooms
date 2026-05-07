import type { User } from "../types/api";
import { apiClient, unwrapData } from "./client";

export async function login(email: string, password: string) {
  const result = await apiClient.POST("/users/login", { body: { email, password } });
  return unwrapData(result) as Promise<{ access_token: string }>;
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
