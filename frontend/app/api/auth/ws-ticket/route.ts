import { NextResponse } from "next/server";
import { backendFetch } from "@/lib/api/client";
import { getSessionToken } from "@/lib/auth/session";

export async function POST() {
  const token = await getSessionToken();
  if (!token) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const upstream = await backendFetch("/api/v1/auth/ws-ticket", {
    method: "POST",
    token,
  });

  if (!upstream.ok) {
    return NextResponse.json({ error: "Failed to get ticket" }, { status: upstream.status });
  }

  const data = await upstream.json();
  return NextResponse.json(data);
}
