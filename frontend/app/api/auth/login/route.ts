import { NextResponse } from "next/server";
import { authConfig, backendFetch } from "@/lib/api/client";

export async function POST(request: Request) {
  const body = await request.json();

  const upstream = await backendFetch("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify(body),
  });

  if (!upstream.ok) {
    const error = await upstream.json().catch(() => ({ detail: "Login failed" }));
    return NextResponse.json(
      { error: error.detail ?? "Login failed" },
      { status: upstream.status },
    );
  }

  const data = await upstream.json();
  const response = NextResponse.json({ ok: true });
  response.cookies.set(authConfig.cookieName, data.access_token, authConfig.cookieOptions);
  return response;
}
