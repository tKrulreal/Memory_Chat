import { NextResponse } from "next/server";
import { backendFetch } from "@/lib/api/client";

export async function POST(request: Request) {
  const body = await request.json();
  const upstream = await backendFetch("/api/v1/auth/reset-password", {
    method: "POST",
    body: JSON.stringify(body),
  });

  const data = await upstream.json().catch(() => ({}));
  if (!upstream.ok) {
    return NextResponse.json(
      { error: data.detail ?? "Không thể đặt lại mật khẩu" },
      { status: upstream.status },
    );
  }
  return NextResponse.json(data);
}
