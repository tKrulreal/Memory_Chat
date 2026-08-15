import { NextResponse } from "next/server";
import { backendFetch } from "@/lib/api/client";

export async function POST(request: Request) {
  const body = await request.json();

  const upstream = await backendFetch("/api/v1/auth/register", {
    method: "POST",
    body: JSON.stringify(body),
  });

  if (!upstream.ok) {
    const error = await upstream.json().catch(() => ({ detail: "Registration failed" }));
    return NextResponse.json(
      { error: error.detail ?? "Registration failed" },
      { status: upstream.status },
    );
  }

  const user = await upstream.json();
  return NextResponse.json(user, { status: 201 });
}
