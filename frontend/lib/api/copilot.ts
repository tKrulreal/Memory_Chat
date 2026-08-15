import { backendFetch } from "./client";

export type CopilotRequest = {
  query: string;
  context?: {
    contact_id?: string;
    conversation_id?: string;
  };
};

export type CopilotResponse = {
  response: string;
  intent: string;
  tools_used: string[];
  sources: string[];
  is_valid: boolean;
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
