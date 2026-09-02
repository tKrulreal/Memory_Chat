export type CopilotRequest = {
  query: string;
  context?: {
    contact_id?: string;
    conversation_id?: string;
  };
};

export type CopilotResponse = {
  id?: string;
  response: string;
  intent: string;
  tools_used: string[];
  sources: string[];
  is_valid: boolean;
};

export type CopilotMessageItem = {
  id: string;
  role: "user" | "assistant";
  content: string;
  tools_used?: string[];
  sources?: string[];
  intent?: string | null;
  conversation_id?: string | null;
  created_at?: string;
};

export async function askCopilot(req: CopilotRequest): Promise<CopilotResponse> {
  const res = await fetch("/api/proxy/api/v1/copilot", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });

  if (!res.ok) {
    throw new Error("Failed to ask Copilot");
  }

  return res.json();
}

export async function getCopilotMessages(
  limit: number = 100,
  conversationId?: string | null
): Promise<CopilotMessageItem[]> {
  const url = conversationId
    ? `/api/proxy/api/v1/copilot/messages?limit=${limit}&conversation_id=${encodeURIComponent(conversationId)}`
    : `/api/proxy/api/v1/copilot/messages?limit=${limit}`;

  const res = await fetch(url, {
    method: "GET",
  });

  if (!res.ok) {
    throw new Error("Failed to fetch Copilot messages");
  }

  return res.json();
}

export async function clearCopilotMessages(
  conversationId?: string | null
): Promise<{ status: string; deleted_count: number }> {
  const url = conversationId
    ? `/api/proxy/api/v1/copilot/messages?conversation_id=${encodeURIComponent(conversationId)}`
    : `/api/proxy/api/v1/copilot/messages`;

  const res = await fetch(url, {
    method: "DELETE",
  });

  if (!res.ok) {
    throw new Error("Failed to clear Copilot messages");
  }

  return res.json();
}
