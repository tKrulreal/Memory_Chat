import { Conversation, PaginatedResponse, User } from "@/types";

export async function getConversations(): Promise<Conversation[]> {
  const response = await fetch("/api/proxy/api/v1/direct-conversations");
  if (!response.ok) {
    throw new Error("Failed to fetch conversations");
  }
  const json = await response.json();
  return json.data;
}

export async function createConversation(userEmail: string): Promise<Conversation> {
  const response = await fetch("/api/proxy/api/v1/direct-conversations", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ peer_email: userEmail }),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Failed to create conversation");
  }
  return response.json();
}

export async function markAsRead(conversationId: string): Promise<void> {
  const response = await fetch(`/api/proxy/api/v1/direct-conversations/${conversationId}/read`, {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error("Failed to mark conversation as read");
  }
}

// Since BE User search is blocked, we will use a dummy endpoint or direct search via BFF if implemented later.
// Currently MVP: just search by exact email using the create conversation endpoint which should resolve it.
// If we need a dedicated search endpoint later:
// export async function searchUsers(email: string): Promise<User[]> { ... }
