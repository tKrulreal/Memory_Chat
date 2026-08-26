import type { PaginatedResponse } from "@/types";
import type { User } from "@/types";

export interface ConnectionRequest {
  id: string;
  sender_id: string;
  receiver_id: string;
  status: "PENDING" | "ACCEPTED" | "REJECTED" | "CANCELLED";
  created_at: string;
  updated_at: string;
  sender: User;
  receiver: User;
}

export const getConnectionRequests = async (
  direction: "all" | "incoming" | "outgoing" = "all",
  status: string = "PENDING",
  page: number = 1,
  limit: number = 20
): Promise<PaginatedResponse<ConnectionRequest>> => {
  const query = new URLSearchParams({
    direction,
    status,
    page: page.toString(),
    limit: limit.toString(),
  });
  const res = await fetch(`/api/proxy/api/v1/connection-requests?${query.toString()}`);
  if (!res.ok) {
    const error = await res.json().catch(() => ({}));
    throw new Error(error.detail || error.message || "Failed to fetch connection requests");
  }
  return res.json();
};

export const sendConnectionRequest = async (target_user_id?: string, peer_email?: string): Promise<ConnectionRequest> => {
  const res = await fetch("/api/proxy/api/v1/connection-requests", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ target_user_id, peer_email }),
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({}));
    throw new Error(error.detail || error.message || "Failed to send connection request");
  }
  return res.json();
};

export const acceptConnectionRequest = async (id: string): Promise<ConnectionRequest> => {
  const res = await fetch(`/api/proxy/api/v1/connection-requests/${id}/accept`, { method: "POST" });
  if (!res.ok) {
    const error = await res.json().catch(() => ({}));
    throw new Error(error.detail || error.message || "Failed to accept connection request");
  }
  return res.json();
};

export const rejectConnectionRequest = async (id: string): Promise<ConnectionRequest> => {
  const res = await fetch(`/api/proxy/api/v1/connection-requests/${id}/reject`, { method: "POST" });
  if (!res.ok) {
    const error = await res.json().catch(() => ({}));
    throw new Error(error.detail || error.message || "Failed to reject connection request");
  }
  return res.json();
};

export const cancelConnectionRequest = async (id: string): Promise<ConnectionRequest> => {
  const res = await fetch(`/api/proxy/api/v1/connection-requests/${id}/cancel`, { method: "POST" });
  if (!res.ok) {
    const error = await res.json().catch(() => ({}));
    throw new Error(error.detail || error.message || "Failed to cancel connection request");
  }
  return res.json();
};

export const unfriendUser = async (targetUserId: string): Promise<{ message: string; target_user_id: string }> => {
  const res = await fetch(`/api/proxy/api/v1/connection-requests/friends/${targetUserId}`, { method: "DELETE" });
  if (!res.ok) {
    const error = await res.json().catch(() => ({}));
    throw new Error(error.detail || error.message || "Failed to unfriend user");
  }
  return res.json();
};
