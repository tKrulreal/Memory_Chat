import { Message, PaginatedResponse } from "@/types";

export type CursorPagination = {
  has_next: boolean;
  limit: number;
};

export type CursorPaginatedResponse<T> = {
  data: T[];
  pagination: CursorPagination;
};

export async function getMessages(
  conversationId: string,
  beforeCreatedAt?: string,
  beforeId?: string,
  limit: number = 50
): Promise<CursorPaginatedResponse<Message>> {
  let url = `/api/proxy/api/v1/direct-conversations/${conversationId}/messages?limit=${limit}`;
  if (beforeCreatedAt && beforeId) {
    url += `&before_created_at=${encodeURIComponent(beforeCreatedAt)}&before_id=${encodeURIComponent(beforeId)}`;
  }
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error("Failed to fetch messages");
  }
  return response.json();
}

export async function sendMessage(
  conversationId: string,
  content: string,
  clientMessageId: string
): Promise<Message> {
  const response = await fetch(`/api/proxy/api/v1/direct-conversations/${conversationId}/messages`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      content,
      client_message_id: clientMessageId,
    }),
  });
  if (!response.ok && response.status !== 409) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Failed to send message");
  }
  return response.json();
}

export async function deleteMessage(messageId: string): Promise<void> {
  const response = await fetch(`/api/proxy/api/v1/messages/${messageId}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Failed to recall message");
  }
}
