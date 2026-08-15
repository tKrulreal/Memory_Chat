import { backendFetch } from "./client";

export type AIContext = {
  summary?: string;
  last_met?: string;
  interested_in?: string[];
  follow_up?: string;
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
      // Mock success for MVP
      return context;
    }
    throw new Error("Failed to update context");
  }

  return res.json();
}

export async function refreshConversationContext(conversationId: string): Promise<void> {
  const res = await fetch(`/api/proxy/api/v1/direct-conversations/${conversationId}/assistant/context/refresh`, {
    method: "POST",
  });

  if (!res.ok) {
    throw new Error("Failed to trigger context refresh");
  }
}
