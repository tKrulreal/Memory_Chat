const IS_SERVER = typeof window === "undefined";
const API_URL = IS_SERVER
  ? (process.env.INTERNAL_API_URL || process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000")
  : (process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000");
const COOKIE_NAME = process.env.AUTH_COOKIE_NAME ?? "memorychat_session";

export const authConfig = {
  apiUrl: API_URL,
  cookieName: COOKIE_NAME,
  cookieOptions: {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax" as const,
    path: "/",
    maxAge: 60 * 60 * 24 * 7,
  },
};

export async function backendFetch(
  path: string,
  init?: RequestInit & { token?: string },
) {
  const { token, headers, ...rest } = init ?? {};
  return fetch(`${authConfig.apiUrl}${path}`, {
    ...rest,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
  });
}
