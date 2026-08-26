import { NextResponse } from "next/server";
import { authConfig } from "@/lib/api/client";

export async function POST() {
  const response = NextResponse.json({ ok: true });
  response.cookies.set(authConfig.cookieName, "", {
    ...authConfig.cookieOptions,
    maxAge: 0,
  });
  return response;
}
