"use client";

import { Search } from "lucide-react";
import { cn } from "@/lib/utils";
import { useConversationStore } from "@/lib/stores/conversation-store";

import { useState, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { getConversations } from "@/lib/api/conversations";
import { useAuthStore } from "@/lib/stores/auth-store";
import { Skeleton } from "@/components/ui/skeleton";

const FILTERS = ["All", "Unread", "Groups"] as const;

type ChatListPanelProps = {
  onSelect?: (conversationId: string) => void;
};

export function ChatListPanel({ onSelect }: ChatListPanelProps) {
  const router = useRouter();
  const pathname = usePathname();
  const user = useAuthStore((s) => s.user);
  const activeId = useConversationStore((s) => s.activeConversationId);
  const setActive = useConversationStore((s) => s.setActiveConversation);

  const handleSelect = (conversationId: string) => {
    setActive(conversationId);
    onSelect?.(conversationId);
    if (pathname !== "/chats") {
      router.push("/chats");
    }
  };


  const { data: conversations = [], isLoading } = useQuery({
    queryKey: ["conversations"],
    queryFn: getConversations,
    enabled: !!user,
  });

  const [searchQuery, setSearchQuery] = useState("");

  // Local filtering for the main list
  const items = conversations.filter(c => {
    if (!searchQuery) return true;
    const isUserA = user?.id === c.user_a_id;
    const peer = isUserA ? c.user_b : c.user_a;
    const name = peer?.full_name || peer?.email || "";
    return name.toLowerCase().includes(searchQuery.toLowerCase());
  });

  return (
    <section className="flex h-full w-chat-list shrink-0 flex-col border-r border-subtle bg-surface">
      <header className="border-b border-subtle px-4 py-4">
        <h2 className="text-lg font-semibold">Chats</h2>
        <div className="relative mt-3">
          <Search
            size={16}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-secondary"
          />
          <input
            type="search"
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
            }}
            placeholder="Search chats..."
            className="h-10 w-full rounded-composer bg-input pl-9 pr-3 text-sm text-primary placeholder:text-secondary outline-none ring-accent focus:ring-1"
          />
        </div>
        <div className="mt-3 flex gap-2">
          {FILTERS.map((filter) => (
            <button
              key={filter}
              type="button"
              className={cn(
                "rounded-full px-3 py-1 text-xs font-medium transition-colors",
                filter === "All"
                  ? "bg-accent/20 text-accent"
                  : "bg-elevated text-secondary hover:text-primary",
              )}
            >
              {filter}
            </button>
          ))}
        </div>
      </header>

      <ul className="scrollbar-thin flex-1 overflow-y-auto">
        {isLoading && (
          <div className="flex flex-col gap-4 p-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="flex gap-3 items-center">
                <Skeleton className="h-11 w-11 rounded-full shrink-0" />
                <div className="flex-1 space-y-2">
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-3 w-full" />
                </div>
              </div>
            ))}
          </div>
        )}
        {!isLoading && items.length === 0 && (
          <li className="p-4 text-center text-sm text-secondary">No chats found.</li>
        )}
        {!isLoading && items.map((conversation) => {
          const active = activeId === conversation.id;
          const isUserA = user?.id === conversation.user_a_id;
          const peerId = isUserA ? conversation.user_b_id : conversation.user_a_id;
          const peer = isUserA ? conversation.user_b : conversation.user_a;
          
          let peerName = `User ${peerId.substring(0, 4)}`;
          let peerShort = peerId.substring(0, 2).toUpperCase();
          
          if (peer) {
            peerName = peer.full_name || peer.email.split('@')[0];
            peerShort = peer.email.substring(0, 2).toUpperCase();
          }
          
          // Format date if needed
          const dateStr = conversation.last_message_at ? new Date(conversation.last_message_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : "";

          return (
            <li key={conversation.id}>
              <button
                type="button"
                onClick={() => {
                  handleSelect(conversation.id);
                }}
                className={cn(
                  "flex w-full gap-3 border-l-2 px-4 py-3 text-left transition-colors",
                  active
                    ? "border-accent bg-accent/10"
                    : "border-transparent hover:bg-elevated",
                )}
              >

                <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-blue-500/20 text-sm font-semibold text-blue-300 uppercase">
                  {peerShort}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between gap-2">
                    <span className="truncate text-sm font-medium">{peerName}</span>
                    <span className="shrink-0 text-xs text-secondary">{dateStr}</span>
                  </div>
                  <p className="truncate text-xs text-secondary">
                    {conversation.last_message ?? "No messages yet"}
                  </p>
                </div>
              </button>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
