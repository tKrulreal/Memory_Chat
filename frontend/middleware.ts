import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

const PUBLIC_PATHS = ["/login", "/register"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get("memorychat_session")?.value;
  const isPublic = PUBLIC_PATHS.some((path) => pathname.startsWith(path));
  const isAuthApi = pathname.startsWith("/api/auth");

  if (isAuthApi || isPublic) {
    if (token && (pathname === "/login" || pathname === "/register")) {
      return NextResponse.redirect(new URL("/chats", request.url));
    }
    return NextResponse.next();
  }

  if (!token) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
