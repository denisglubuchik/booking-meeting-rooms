import createClient, { type Middleware } from "openapi-fetch";
import { i18n } from "../i18n";
import type { paths } from "./schema";

const API_VERSION = "v1";

const API_ROOT_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") ||
  "http://localhost:8000/api";

export const API_BASE_URL = `${API_ROOT_URL}/${API_VERSION}`;

let token = localStorage.getItem("booking_token") || "";
let refreshPromise: Promise<string | null> | null = null;

export class ApiError extends Error {
  status: number;
  details: string;
  code?: string;

  constructor(status: number, message: string, details = "", code?: string) {
    super(message);
    this.status = status;
    this.details = details;
    this.code = code;
  }
}

export function humanizeApiError(error: unknown) {
  if (error instanceof ApiError) return error.message;
  if (error instanceof Error) return error.message;
  return i18n.global.t("common.unknownError");
}

export function setApiToken(nextToken: string) {
  token = nextToken;
  if (nextToken) localStorage.setItem("booking_token", nextToken);
  else localStorage.removeItem("booking_token");
}

export function setAuthTokens(nextAccessToken: string) {
  setApiToken(nextAccessToken);
}

export function clearAuthTokens() {
  setApiToken("");
}

export const apiClient = createClient<paths>({
  baseUrl: API_BASE_URL,
});

const authMiddleware: Middleware = {
  async onRequest({ request }) {
    const requestWithCredentials = new Request(request, {
      credentials: "include",
    });
    if (token) request.headers.set("Authorization", `Bearer ${token}`);
    if (token) {
      requestWithCredentials.headers.set("Authorization", `Bearer ${token}`);
    }
    return requestWithCredentials;
  },
};

apiClient.use(authMiddleware);

async function refreshAccessToken(): Promise<string | null> {
  if (!refreshPromise) {
    refreshPromise = (async () => {
      const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: "POST",
        credentials: "include",
      });
      if (!response.ok) {
        clearAuthTokens();
        return null;
      }
      const payload = (await response.json()) as { access_token: string };
      setAuthTokens(payload.access_token);
      return payload.access_token;
    })().finally(() => {
      refreshPromise = null;
    });
  }
  return refreshPromise;
}

const refreshMiddleware = {
  async onResponse({ request, response }: { request: Request; response: Response }) {
    if (response.status !== 401 || request.headers.get("x-auth-retry") === "1") {
      return response;
    }
    const nextAccessToken = await refreshAccessToken();
    if (!nextAccessToken) return response;

    const headers = new Headers(request.headers);
    headers.set("Authorization", `Bearer ${nextAccessToken}`);
    headers.set("x-auth-retry", "1");

    return fetch(new Request(request, { headers, credentials: "include" }));
  },
} as Middleware;

apiClient.use(refreshMiddleware);

function parseErrorMessage(status: number, body: unknown) {
  if (body && typeof body === "object") {
    const code = (body as { error?: { code?: unknown } }).error?.code;
    if (typeof code === "string") {
      const i18nKey = `api.errors.${code}`;
      if (i18n.global.te(i18nKey)) return i18n.global.t(i18nKey);
    }
  }

  if (typeof body === "string" && body.trim()) return body;
  if (body && typeof body === "object") {
    const detail = (body as { detail?: unknown }).detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail) && detail.length > 0) return i18n.global.t("api.fallback.invalidFields");
  }

  if (status === 401) return i18n.global.t("api.fallback.unauthorized");
  if (status === 403) return i18n.global.t("api.fallback.forbidden");
  if (status === 404) return i18n.global.t("api.fallback.notFound");
  if (status >= 500) return i18n.global.t("api.fallback.serverError");
  return i18n.global.t("api.fallback.requestFailed", { status });
}

function parseErrorCode(body: unknown) {
  if (!body || typeof body !== "object") return undefined;
  const code = (body as { error?: { code?: unknown } }).error?.code;
  return typeof code === "string" ? code : undefined;
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

  const code = parseErrorCode(parsed);
  throw new ApiError(result.response.status, parseErrorMessage(result.response.status, parsed), raw, code);
}
