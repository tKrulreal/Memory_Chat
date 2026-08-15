import { backendFetch } from "./client";
import type { Participant } from "./conversations";

export type SearchResult = {
  conversation_id: string;
  peer: Participant;
  summary_snippet?: string;
  score: number;
};

export async function searchConversations(query: string, top_k: number = 5): Promise<SearchResult[]> {
  const params = new URLSearchParams({
    query,
    top_k: top_k.toString(),
  });
  return backendFetch(`/api/v1/search/conversations?${params.toString()}`);
}
