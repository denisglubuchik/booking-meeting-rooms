import createClient, { type Middleware } from "openapi-fetch";
import type { paths } from "./schema";

export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") || "http://localhost:8000";

let token = localStorage.getItem("booking_token") || "";

export class ApiError extends Error {
  status: number;
  details: string;

  constructor(status: number, message: string, details = "") {
    super(message);
    this.status = status;
    this.details = details;
  }
}

export function humanizeApiError(error: unknown) {
  if (error instanceof ApiError) return error.message;
  if (error instanceof Error) return error.message;
  return "Неизвестная ошибка";
}

export function setApiToken(nextToken: string) {
  token = nextToken;
  if (nextToken) localStorage.setItem("booking_token", nextToken);
  else localStorage.removeItem("booking_token");
}

export const apiClient = createClient<paths>({
  baseUrl: API_BASE_URL,
});

const authMiddleware: Middleware = {
  async onRequest({ request }) {
    if (token) request.headers.set("Authorization", `Bearer ${token}`);
    return request;
  },
};

apiClient.use(authMiddleware);

function parseErrorMessage(status: number, body: unknown) {
  if (typeof body === "string" && body.trim()) return body;
  if (body && typeof body === "object") {
    const detail = (body as { detail?: unknown }).detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail) && detail.length > 0) return "Проверьте корректность заполненных полей.";
  }

  if (status === 401) return "Сессия истекла или неверные учетные данные.";
  if (status === 403) return "Недостаточно прав для выполнения действия.";
  if (status === 404) return "Ресурс не найден.";
  if (status >= 500) return "Внутренняя ошибка сервера.";
  return `Запрос завершился с ошибкой (${status}).`;
}

export async function unwrapData<T>(result: { data?: T; error?: unknown; response: Response }) {
  if (result.response.ok && result.data !== undefined) return result.data;

  let raw = "";
  let parsed: unknown = result.error;

  if (result.error === undefined && !result.response.bodyUsed) {
    raw = await result.response.text();
    parsed = raw;
    try {
      parsed = raw ? JSON.parse(raw) : "";
    } catch {
      // keep raw text
    }
  }

  throw new ApiError(result.response.status, parseErrorMessage(result.response.status, parsed), raw);
}
