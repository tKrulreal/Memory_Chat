import { cookies } from "next/headers";
import { authConfig } from "@/lib/api/client";

export async function getSessionToken(): Promise<string | undefined> {
  const cookieStore = await cookies();
  return cookieStore.get(authConfig.cookieName)?.value;
}
