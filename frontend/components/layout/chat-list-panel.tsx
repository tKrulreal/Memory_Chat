"use client";

import { Search } from "lucide-react";
import { cn } from "@/lib/utils";
import { useConversationStore } from "@/lib/stores/conversation-store";

import { useState, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { getConversations } from "@/lib/api/conversations";
import { getMessages } from "@/lib/api/messages";
import { useAuthStore } from "@/lib/stores/auth-store";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";

const FILTERS = ["All", "Unread"] as const;

type ChatListPanelProps = {
  onSelect?: (conversationId: string) => void;
};

export function ChatListPanel({ onSelect }: ChatListPanelProps) {
  const router = useRouter();
  const pathname = usePathname();
  const user = useAuthStore((s) => s.user);
  const activeId = useConversationStore((s) => s.activeConversationId);
  const setActive = useConversationStore((s) => s.setActiveConversation);
  const queryClient = useQueryClient();

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
  const [activeFilter, setActiveFilter] = useState<typeof FILTERS[number]>("All");

  // Local filtering for the main list
  const items = conversations.filter(c => {
    // Apply Unread filter
    if (activeFilter === "Unread" && (!c.unread_count || c.unread_count === 0)) {
      return false;
    }

    // Apply Search filter
    if (!searchQuery) return true;
    const isUserA = user?.id === c.user_a_id;
    const peer = isUserA ? c.user_b : c.user_a;
    const name = peer?.full_name || peer?.email || "";
    return name.toLowerCase().includes(searchQuery.toLowerCase());
  });

  return (
    <section className="relative z-10 flex h-full w-[320px] shrink-0 flex-col border-r border-slate-200 bg-slate-50/50">
      <header className="border-b border-slate-200/50 px-6 py-6 bg-white">
        <h2 className="text-xl font-bold text-slate-900">Chats</h2>
        <div className="relative mt-4">
          <Search
            size={18}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
          />
          <Input
            type="search"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search chats..."
            className="h-11 w-full rounded-2xl bg-slate-100/80 pl-10 pr-4 text-sm text-slate-900 placeholder:text-slate-500 outline-none focus:ring-2 focus:ring-blue-500/50 border-none shadow-inner"
          />
        </div>
        <div className="mt-4 flex gap-1 p-1 bg-slate-100 rounded-lg">
          {FILTERS.map((filter) => (
            <Button
              variant="ghost"
              key={filter}
              type="button"
              onClick={() => setActiveFilter(filter)}
              className={cn(
                "flex-1 rounded-md px-4 py-1.5 text-xs font-semibold transition-all duration-200 h-8",
                filter === activeFilter
                  ? "bg-white text-slate-900 shadow-sm"
                  : "bg-transparent text-slate-500 hover:text-slate-700 hover:bg-transparent",
              )}
            >
              {filter}
            </Button>
          ))}
        </div>
      </header>

      <ul className="scrollbar-thin flex-1 overflow-y-auto flex flex-col gap-1 p-2">
        {isLoading && (
          <div className="flex flex-col gap-4 p-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="flex gap-4 items-center">
                <Skeleton className="h-12 w-12 rounded-full shrink-0" />
                <div className="flex-1 space-y-2">
                  <Skeleton className="h-5 w-24" />
                  <Skeleton className="h-4 w-full" />
                </div>
              </div>
            ))}
          </div>
        )}
        {!isLoading && items.length === 0 && (
          <li className="p-6 text-center text-sm text-slate-500">No chats found.</li>
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
            <li key={conversation.id} className="mb-1">
              <div
                onClick={() => handleSelect(conversation.id)}
                onMouseEnter={() => {
                  if (!active) {
                    queryClient.prefetchInfiniteQuery({
                      queryKey: ["messages", conversation.id],
                      queryFn: ({ pageParam }) => getMessages(conversation.id, pageParam?.beforeCreatedAt, pageParam?.beforeId),
                      initialPageParam: undefined as { beforeCreatedAt: string, beforeId: string } | undefined,
                    });
                  }
                }}
                className={cn(
                  "flex items-center gap-3 p-3 rounded-xl cursor-pointer transition-colors",
                  active
                    ? "bg-blue-50 border-l-4 border-blue-600 rounded-l-none"
                    : "bg-transparent hover:bg-slate-100"
                )}
              >
                {/* Avatar */}
                <div className="flex-shrink-0">
                  <Avatar className="h-10 w-10 border border-slate-200 shadow-sm">
                    <AvatarFallback className="bg-blue-50 text-blue-700 font-bold text-xs">
                      {peerShort}
                    </AvatarFallback>
                  </Avatar>
                </div>

                {/* Khối Nội Dung */}
                <div className="flex-1 min-w-0 flex flex-col gap-1">
                  
                  {/* Dòng 1: Tên & Thời gian */}
                  <div className="flex justify-between items-baseline">
                    <h4 className="font-semibold text-sm text-slate-900 truncate pr-2">
                      {peerName}
                    </h4>
                    <span className="text-xs text-slate-500 flex-shrink-0">
                      {dateStr}
                    </span>
                  </div>

                  {/* Dòng 2 (MỚI): Tags phân loại */}
                  {conversation.tags && conversation.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {conversation.tags.map((tag: any, idx: number) => {
                        const tagName = typeof tag === 'string' ? tag : tag.name;
                        const tagColor = typeof tag === 'object' && tag.color ? tag.color : "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300";
                        return (
                          <Badge 
                            key={idx} 
                            variant="secondary" 
                            className={cn("text-[10px] py-0 px-1.5 h-4 font-normal", tagColor)}
                          >
                            {tagName}
                          </Badge>
                        );
                      })}
                    </div>
                  )}

                  {/* Dòng 3: Nội dung preview & Badge Unread */}
                  <div className="flex justify-between items-center">
                    <p className={cn(
                      "text-xs truncate pr-2",
                      active ? "text-slate-900 font-medium" : "text-muted-foreground text-slate-500"
                    )}>
                      {conversation.last_message ?? "No messages yet"}
                    </p>
                    {!!conversation.unread_count && conversation.unread_count > 0 && (
                      <span className="flex-shrink-0 flex h-5 min-w-[20px] items-center justify-center rounded-full bg-blue-600 px-1.5 text-[10px] font-bold text-white shadow-sm">
                        {conversation.unread_count > 99 ? '99+' : conversation.unread_count}
                      </span>
                    )}
                  </div>

                </div>
              </div>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
