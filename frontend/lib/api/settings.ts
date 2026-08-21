import { Setting } from "@/types";

export async function getSettings(): Promise<Setting> {
  const response = await fetch("/api/proxy/api/v1/me/settings");
  if (!response.ok) {
    throw new Error("Failed to fetch settings");
  }
  return response.json();
}

export async function updateSettings(data: Partial<Setting>): Promise<Setting> {
  const response = await fetch("/api/proxy/api/v1/me/settings", {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error("Failed to update settings");
  }
  return response.json();
}
