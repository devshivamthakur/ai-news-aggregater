import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface ApiResponse<T = unknown> {
  data: T;
  status: number;
}

/**
 * Window event fired when a refresh attempt fails and the session is really
 * over. The app listens for it and navigates in-app instead of hard-loading
 * the page — which would throw away whatever error the user was about to read.
 */
export const SESSION_EXPIRED_EVENT = "ai-pulse:session-expired";

/**
 * Endpoints where a 401 is the answer itself ("wrong password", "token
 * rejected"), not a dead-session signal. Never refresh, redirect or clear
 * tokens for these — the calling screen needs to show the message.
 */
const AUTH_ENDPOINT_RE = /\/(login|register|refresh|logout)(?:[/?#]|$)/;

/** Request config flagged so a retried call can't loop through refresh. */
type RetriableConfig = InternalAxiosRequestConfig & { _retried?: boolean };

export interface ApiError {
  detail: string;
  status: number;
}

interface PydanticValidationError {
  type?: string;
  loc?: Array<string | number>;
  msg?: string;
  input?: unknown;
  ctx?: unknown;
}

/**
 * Normalizes a FastAPI error payload into a human-readable message.
 * `detail` can be a string (HTTPException) or an array of Pydantic v2
 * validation error objects — never render the raw value as a React child.
 */
function extractErrorMessage(error: AxiosError<{ detail?: unknown }>): string {
  const body = error.response?.data as { detail?: unknown } | PydanticValidationError[] | undefined;
  // FastAPI sends validation failures (422) as a *bare array* of error objects,
  // while HTTPException-style failures wrap the same shapes in `detail`.
  const detail = Array.isArray(body) ? body : body?.detail;

  if (typeof detail === "string" && detail.trim()) {
    return detail;
  }

  if (Array.isArray(detail)) {
    return (detail as PydanticValidationError[])
      .map((e) => {
        const field = Array.isArray(e?.loc)
          ? e.loc.filter((s) => s !== "body").join(".")
          : "request";
        const msg = e?.msg ?? "Invalid value";
        return field ? `${field}: ${msg}` : msg;
      })
      .join("; ");
  }

  if (detail && typeof detail === "object" && typeof (detail as { msg?: string }).msg === "string") {
    return (detail as { msg: string }).msg;
  }

  return error.message || "An error occurred";
}

class ApiClient {
  private client: AxiosInstance;
  private refreshPromise: Promise<string | null> | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE_URL}/api/v1`,
      timeout: 30000,
      headers: {
        "Content-Type": "application/json",
      },
    });

    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        const token = localStorage.getItem("access_token");
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError<{ detail?: unknown }>) => {
        const reject = () =>
          Promise.reject({
            detail: extractErrorMessage(error),
            status: error.response?.status || 500,
          } as ApiError);

        const status = error.response?.status;
        const config = error.config as RetriableConfig | undefined;

        // Bad credentials / rejected token on an auth endpoint: this 401 *is*
        // the message. Hand it straight back so the form can render it — the
        // old code hard-navigated to /login here, reloading the SPA and wiping
        // the error before anyone could read it.
        if (status !== 401 || !config || AUTH_ENDPOINT_RE.test(config.url ?? "")) {
          return reject();
        }

        // Already refreshed once for this exact request: give up quietly
        // rather than looping (an authorization failure must not sign the
        // user out either).
        if (config._retried) {
          return reject();
        }

        const hadSession = this.isAuthenticated() || !!localStorage.getItem("refresh_token");

        if (hadSession) {
          // One silent refresh, then replay the original request.
          const newToken = await this.refreshToken();
          if (newToken) {
            config._retried = true;
            if (config.headers) {
              config.headers.Authorization = `Bearer ${newToken}`;
            }
            return this.client(config);
          }

          // Refresh token is dead: the session really is over. Clear it and
          // tell the app (see SessionExpiryWatcher) — still no page reload.
          this.clearTokens();
          if (typeof window !== "undefined") {
            window.dispatchEvent(new Event(SESSION_EXPIRED_EVENT));
          }
        }

        return reject();
      }
    );
  }

  private async refreshToken(): Promise<string | null> {
    // Prevent multiple simultaneous refresh requests
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    const refreshToken = localStorage.getItem("refresh_token");
    if (!refreshToken) {
      return null;
    }

    this.refreshPromise = this.client
      .post("/refresh", { refresh_token: refreshToken })
      .then((response) => {
        const { access_token, refresh_token } = response.data;
        localStorage.setItem("access_token", access_token);
        localStorage.setItem("refresh_token", refresh_token);
        return access_token;
      })
      .catch(() => {
        this.clearTokens();
        return null;
      })
      .finally(() => {
        this.refreshPromise = null;
      });

    return this.refreshPromise;
  }

  async get<T>(url: string, params?: Record<string, unknown>, config?: { signal?: AbortSignal }): Promise<T> {
    const response = await this.client.get<T>(url, { params, signal: config?.signal });
    return response.data;
  }

  async post<T>(url: string, data?: unknown, extraHeaders?: Record<string, string>): Promise<T> {
    const response = await this.client.post<T>(url, data, { headers: extraHeaders });
    return response.data;
  }

  async patch<T>(url: string, data?: unknown): Promise<T> {
    const response = await this.client.patch<T>(url, data);
    return response.data;
  }

  async delete<T>(url: string): Promise<T> {
    const response = await this.client.delete<T>(url);
    return response.data;
  }

  setTokens(accessToken: string, refreshToken: string) {
    localStorage.setItem("access_token", accessToken);
    localStorage.setItem("refresh_token", refreshToken);
  }

  setToken(token: string | null) {
    if (token) {
      localStorage.setItem("access_token", token);
    } else {
      localStorage.removeItem("access_token");
    }
  }

  getToken(): string | null {
    if (typeof window !== "undefined") {
      return localStorage.getItem("access_token");
    }
    return null;
  }

  clearTokens() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }
}

export const api = new ApiClient();
