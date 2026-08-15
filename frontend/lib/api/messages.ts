import { Message, PaginatedResponse } from "@/types";

export async function getMessages(
  conversationId: string,
  page: number = 1,
  limit: number = 50
): Promise<PaginatedResponse<Message>> {
  const response = await fetch(`/api/proxy/api/v1/direct-conversations/${conversationId}/messages?page=${page}&limit=${limit}`);
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
