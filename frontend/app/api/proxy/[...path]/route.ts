import { NextRequest, NextResponse } from "next/server";
import { getSessionToken } from "@/lib/auth/session";
import { authConfig } from "@/lib/api/client";
export const dynamic = "force-dynamic";

async function proxyRequest(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  const targetPath = `/${path.join("/")}`;
  const token = await getSessionToken();

  const url = new URL(request.url);
  const targetUrl = `${authConfig.apiUrl}${targetPath}${url.search}`;

  const headers = new Headers(request.headers);
  headers.delete("host");
  headers.delete("cookie");

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const options: RequestInit = {
    method: request.method,
    headers,
    redirect: "manual",
    cache: "no-store",
  };

  if (request.method !== "GET" && request.method !== "HEAD") {
    options.body = await request.arrayBuffer();
  }

  try {
    const upstreamResponse = await fetch(targetUrl, options);
    
    const responseHeaders = new Headers(upstreamResponse.headers);
    responseHeaders.delete("content-encoding");

    return new NextResponse(upstreamResponse.body, {
      status: upstreamResponse.status,
      statusText: upstreamResponse.statusText,
      headers: responseHeaders,
    });
  } catch (error) {
    console.error("Proxy error:", error);
    return NextResponse.json({ detail: "Proxy error" }, { status: 502 });
  }
}

export const GET = proxyRequest;
export const POST = proxyRequest;
export const PUT = proxyRequest;
export const PATCH = proxyRequest;
export const DELETE = proxyRequest;
export const OPTIONS = proxyRequest;
