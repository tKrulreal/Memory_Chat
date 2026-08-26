import { Setting, BlockedUser } from "@/types";

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

export async function changePassword(currentPassword: string, newPassword: string): Promise<{ message: string }> {
  const response = await fetch("/api/proxy/api/v1/auth/change-password", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      current_password: currentPassword,
      new_password: newPassword,
    }),
  });
  if (!response.ok) {
    const errData = await response.json().catch(() => ({ detail: "Đổi mật khẩu thất bại" }));
    throw new Error(errData.detail || "Đổi mật khẩu thất bại");
  }
  return response.json();
}

export async function getBlockedUsers(): Promise<BlockedUser[]> {
  const response = await fetch("/api/proxy/api/v1/me/blocked-users");
  if (!response.ok) {
    throw new Error("Failed to fetch blocked users");
  }
  return response.json();
}

export async function blockUser(targetUserId: string): Promise<{ message: string }> {
  const response = await fetch(`/api/proxy/api/v1/me/block/${targetUserId}`, {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error("Failed to block user");
  }
  return response.json();
}

export async function unblockUser(targetUserId: string): Promise<{ message: string }> {
  const response = await fetch(`/api/proxy/api/v1/me/unblock/${targetUserId}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    throw new Error("Failed to unblock user");
  }
  return response.json();
}
