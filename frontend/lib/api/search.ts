import { SearchResult } from "@/types";

// ── Conversation search (existing) ─────────────────────────────────────────
export async function searchConversations(query: string, top_k: number = 5): Promise<SearchResult[]> {
  const params = new URLSearchParams({
    query,
    top_k: top_k.toString(),
  });
  const response = await fetch(`/api/proxy/api/v1/search/conversations?${params.toString()}`);
  
  if (!response.ok) {
    throw new Error("Failed to search conversations");
  }
  
  return response.json();
}

// ── User / People search ────────────────────────────────────────────────────
export type UserRelation =
  | "none"
  | "pending_sent"
  | "pending_received"
  | "friend";

export interface SearchUser {
  id: string;
  full_name: string | null;
  email: string;
  avatar: string | null;
  relation: UserRelation;
  conversation_id: string | null;
}

export interface UserSearchResponse {
  items: SearchUser[];
  total: number;
  limit: number;
  offset: number;
}

export async function searchUsers(
  q: string,
  limit = 20,
  offset = 0
): Promise<UserSearchResponse> {
  const params = new URLSearchParams({
    q,
    limit: limit.toString(),
    offset: offset.toString(),
  });
  const res = await fetch(`/api/proxy/api/v1/search/users?${params.toString()}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to search users");
  }
  return res.json();
}
