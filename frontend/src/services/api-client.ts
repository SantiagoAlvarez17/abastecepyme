import type { ApiErrorBody } from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  code: string;
  details: NonNullable<ApiErrorBody["details"]>;

  constructor(status: number, code: string, message: string, details: ApiErrorBody["details"] = []) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.details = details ?? [];
  }
}

export async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_URL}${path}`, {
      method,
      headers: { "Content-Type": "application/json" },
      body: body === undefined ? undefined : JSON.stringify(body),
      cache: "no-store",
    });
  } catch {
    throw new ApiError(
      0,
      "ERR_NETWORK",
      `No se pudo conectar con la API en ${API_URL}. ¿Está corriendo el backend?`,
    );
  }

  const data = await res.json().catch(() => null);
  if (!res.ok) {
    throw new ApiError(
      res.status,
      data?.error_code ?? "ERR_UNKNOWN",
      data?.message ?? `Error ${res.status}`,
      data?.details,
    );
  }
  return data as T;
}