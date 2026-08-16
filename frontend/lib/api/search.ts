import { SearchResult } from "@/types";

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
