"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Search, Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";

import { searchConversations } from "@/lib/api/search";
import { useConversationStore } from "@/lib/stores/conversation-store";
import { cn } from "@/lib/utils";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [submittedQuery, setSubmittedQuery] = useState("");
  
  const router = useRouter();
  const setActiveConversation = useConversationStore((s) => s.setActiveConversation);

  const { data: results, isLoading, isError } = useQuery({
    queryKey: ["semantic_search", submittedQuery],
    queryFn: () => searchConversations(submittedQuery, 10),
    enabled: !!submittedQuery,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      setSubmittedQuery(query.trim());
    }
  };

  const handleSelect = (conversationId: string) => {
    setActiveConversation(conversationId);
    router.push("/");
  };

  return (
    <main className="flex h-full flex-col bg-app">
      <header className="border-b border-subtle px-6 py-6">
        <h1 className="mb-4 text-2xl font-semibold">Semantic Search</h1>
        <form onSubmit={handleSubmit} className="relative max-w-2xl">
          <Search
            size={20}
            className="absolute left-4 top-1/2 -translate-y-1/2 text-secondary"
          />
          <input
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search your past conversations by context, e.g. 'the person I talked to about robotics'..."
            className="h-12 w-full rounded-full bg-input pl-12 pr-4 text-sm text-primary placeholder:text-secondary outline-none ring-accent focus:ring-1"
          />
          <button
            type="submit"
            disabled={!query.trim() || isLoading}
            className="absolute right-2 top-1/2 -translate-y-1/2 rounded-full bg-accent px-4 py-1.5 text-xs font-medium text-white transition-opacity hover:opacity-90 disabled:opacity-50"
          >
            Search
          </button>
        </form>
      </header>

      <div className="flex-1 overflow-y-auto p-6">
        <div className="mx-auto max-w-2xl">
          {isLoading && (
            <div className="flex items-center justify-center p-8 text-secondary">
              <Loader2 className="mr-2 h-6 w-6 animate-spin" />
              Searching memories...
            </div>
          )}

          {isError && (
            <div className="p-4 text-center text-red-500 bg-red-500/10 rounded-button">
              Failed to perform search. Please try again later.
            </div>
          )}

          {!isLoading && submittedQuery && results?.length === 0 && (
            <div className="p-8 text-center text-secondary">
              No matching conversations found for &quot;{submittedQuery}&quot;.
            </div>
          )}

          {!isLoading && results && results.length > 0 && (
            <ul className="space-y-4">
              {results.map((result) => {
                const peerName = result.peer.full_name || result.peer.email.split('@')[0];
                const peerShort = result.peer.email.substring(0, 2).toUpperCase();

                return (
                  <li key={result.conversation_id}>
                    <button
                      type="button"
                      onClick={() => handleSelect(result.conversation_id)}
                      className="flex w-full flex-col gap-3 rounded-button border border-subtle bg-surface p-4 text-left transition-colors hover:border-accent hover:bg-elevated"
                    >
                      <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-blue-500/20 text-sm font-semibold text-blue-300 uppercase">
                          {peerShort}
                        </div>
                        <div className="min-w-0 flex-1">
                          <span className="text-sm font-semibold">{peerName}</span>
                          {/* <div className="text-xs text-secondary mt-0.5">Match score: {Math.round(result.score * 100)}%</div> */}
                        </div>
                      </div>
                      
                      {result.summary_snippet && (
                        <div className="mt-2 rounded-md bg-input/50 p-3 text-sm text-secondary">
                          <p className="line-clamp-3 leading-relaxed">
                            {result.summary_snippet}
                          </p>
                        </div>
                      )}
                    </button>
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      </div>
    </main>
  );
}
