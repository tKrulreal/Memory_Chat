import { backendFetch } from "./client";

export type AIContext = {
  summary?: string;
  last_met?: string;
  interested_in?: string[];
  follow_up?: string;
  tags?: string[];
};

export type SuggestedReply = {
  peer_name: string;
  peer_last_message: string | null;
  suggested_reply: string;
  created_at: string | null;
};

export async function getConversationContext(conversationId: string): Promise<AIContext> {
  const res = await fetch(`/api/proxy/api/v1/direct-conversations/${conversationId}/assistant/context`, {
    method: "GET",
  });

  if (!res.ok) {
    if (res.status === 404) {
      // Return empty context if it doesn't exist yet
      return {};
    }
    throw new Error("Failed to fetch context");
  }

  return res.json();
}

export async function updateConversationContext(conversationId: string, context: AIContext): Promise<AIContext> {
  const res = await fetch(`/api/proxy/api/v1/direct-conversations/${conversationId}/assistant/context`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(context),
  });

  if (!res.ok) {
    if (res.status === 404) {
      return context;
    }
    throw new Error("Failed to update context");
  }

  return res.json();
}

export async function refreshConversationContext(conversationId: string): Promise<AIContext> {
  const res = await fetch(`/api/proxy/api/v1/direct-conversations/${conversationId}/assistant/context/refresh`, {
    method: "POST",
  });

  if (!res.ok) {
    throw new Error("Failed to trigger context refresh");
  }

  return res.json();
}

export async function refreshConversationTags(conversationId: string): Promise<{ tags: string[] }> {
  const res = await fetch(`/api/proxy/api/v1/direct-conversations/${conversationId}/assistant/tags/refresh`, {
    method: "POST",
  });

  if (!res.ok) {
    throw new Error("Failed to refresh tags");
  }

  return res.json();
}

export async function updateConversationTags(conversationId: string, tags: string[]): Promise<{ tags: string[] }> {
  const res = await fetch(`/api/proxy/api/v1/direct-conversations/${conversationId}/assistant/tags`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tags }),
  });

  if (!res.ok) {
    throw new Error("Failed to update tags");
  }

  return res.json();
}

export async function getSuggestedReply(conversationId: string): Promise<SuggestedReply> {
  const res = await fetch(`/api/proxy/api/v1/direct-conversations/${conversationId}/assistant/suggested-reply`, {
    method: "GET",
  });

  if (!res.ok) {
    throw new Error("Failed to fetch suggested reply");
  }

  return res.json();
}

export async function refreshSuggestedReply(conversationId: string): Promise<SuggestedReply> {
  const res = await fetch(`/api/proxy/api/v1/direct-conversations/${conversationId}/assistant/suggested-reply/refresh`, {
    method: "POST",
  });

  if (!res.ok) {
    throw new Error("Failed to refresh suggested reply");
  }

  return res.json();
}
