import { NextResponse } from "next/server";
import { backendFetch, authConfig } from "@/lib/api/client";
import { getSessionToken } from "@/lib/auth/session";

export async function GET() {
  const token = await getSessionToken();
  if (!token) {
    return NextResponse.json({ user: null }, { status: 401 });
  }

  const upstream = await backendFetch("/api/v1/auth/me", { token });
  if (!upstream.ok) {
    const response = NextResponse.json({ user: null }, { status: 401 });
    response.cookies.delete(authConfig.cookieName);
    return response;
  }

  const user = await upstream.json();
  return NextResponse.json({ user });
}
