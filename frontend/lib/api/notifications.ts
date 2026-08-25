import { Notification, PaginatedResponse } from "@/types";

export async function getNotifications(
  page: number = 1,
  limit: number = 50,
  type?: string,
  status?: string
): Promise<PaginatedResponse<Notification>> {
  const params = new URLSearchParams({
    page: page.toString(),
    limit: limit.toString(),
  });
  if (type) params.append("type", type);
  if (status) params.append("status", status);

  const response = await fetch(`/api/proxy/api/v1/notifications?${params.toString()}`);
  if (!response.ok) {
    throw new Error("Failed to fetch notifications");
  }
  return response.json();
}

export async function getUnreadNotificationsCount(): Promise<{ unread_count: number }> {
  const response = await fetch("/api/proxy/api/v1/notifications/unread-count");
  if (!response.ok) {
    return { unread_count: 0 };
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

export async function markAllNotificationsRead(): Promise<{ status: string; marked_read: number }> {
  const response = await fetch("/api/proxy/api/v1/notifications/read-all", {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error("Failed to mark all notifications as read");
  }
  return response.json();
}

export async function deleteNotification(id: string): Promise<{ status: string; deleted_id: string }> {
  const response = await fetch(`/api/proxy/api/v1/notifications/${id}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    throw new Error("Failed to delete notification");
  }
  return response.json();
}
