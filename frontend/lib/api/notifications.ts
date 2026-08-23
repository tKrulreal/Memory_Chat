import { Notification, PaginatedResponse } from "@/types";

export async function getNotifications(page: number = 1, limit: number = 20): Promise<PaginatedResponse<Notification>> {
  const response = await fetch(`/api/proxy/api/v1/notifications?page=${page}&limit=${limit}`);
  if (!response.ok) {
    throw new Error("Failed to fetch notifications");
  }
  return response.json();
}

export async function markNotificationRead(id: string): Promise<Notification> {
  const response = await fetch(`/api/proxy/api/v1/notifications/${id}/read`, {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error("Failed to mark notification as read");
  }
  return response.json();
}
