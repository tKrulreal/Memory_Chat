"use client";

import { useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Search, MessageSquare, Sparkles } from "lucide-react";
import { cn, formatChatListTime } from "@/lib/utils";
import { useConversationStore } from "@/lib/stores/conversation-store";
import { usePresenceStore } from "@/lib/stores/presence-store";
import { useAuthStore } from "@/lib/stores/auth-store";
import { getConversations } from "@/lib/api/conversations";
import { getMessages } from "@/lib/api/messages";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { useLanguage } from "@/hooks/use-language";

const FILTERS = ["all", "unread"] as const;

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
  const onlineUserIds = usePresenceStore((s) => s.onlineUserIds);
  const { language, t } = useLanguage();

  const [searchQuery, setSearchQuery] = useState("");
  const [activeFilter, setActiveFilter] = useState<typeof FILTERS[number]>("all");

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

  // Local filtering for conversation items
  const items = conversations.filter((c) => {
    if (activeFilter === "unread" && (!c.unread_count || c.unread_count === 0)) {
      return false;
    }
    if (!searchQuery) return true;
    const isUserA = user?.id === c.user_a_id;
    const peer = isUserA ? c.user_b : c.user_a;
    const name = peer?.full_name || peer?.email || "";
    return name.toLowerCase().includes(searchQuery.toLowerCase());
  });

  return (
    <section className="relative z-10 flex h-full w-[320px] md:w-[340px] shrink-0 flex-col border-r border-slate-200 bg-white">
      {/* Header */}
      <header className="border-b border-slate-100 px-5 py-4 bg-white space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
              <MessageSquare size={16} />
            </div>
            <h2 className="text-base font-bold text-slate-900">{t("chatsTitle")}</h2>
          </div>
          <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-bold text-slate-500">
            {conversations.length}
          </span>
        </div>

        {/* Search */}
        <div className="relative">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <Input
            type="search"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder={t("searchChats")}
            className="h-9 w-full rounded-2xl bg-slate-50 pl-9 pr-3 text-xs border-slate-200 focus:bg-white transition-colors"
          />
        </div>

        {/* Filters */}
        <div className="flex gap-1 p-1 bg-slate-100/80 rounded-xl">
          {FILTERS.map((filter) => (
            <button
              key={filter}
              type="button"
              onClick={() => setActiveFilter(filter)}
              className={cn(
                "flex-1 py-1 text-xs font-semibold rounded-lg transition-all text-center",
                filter === activeFilter
                  ? "bg-white text-slate-900 shadow-2xs"
                  : "text-slate-500 hover:text-slate-800"
              )}
            >
              {t(filter)}
            </button>
          ))}
        </div>
      </header>

      {/* Conversation List */}
      <ul className="scrollbar-thin flex-1 overflow-y-auto p-2 space-y-1">
        {isLoading && (
          <div className="flex flex-col gap-3 p-2">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="flex gap-3 items-center p-2 rounded-2xl">
                <Skeleton className="h-11 w-11 rounded-full shrink-0" />
                <div className="flex-1 space-y-2">
                  <Skeleton className="h-4 w-28 rounded-md" />
                  <Skeleton className="h-3 w-full rounded-md" />
                </div>
              </div>
            ))}
          </div>
        )}

        {!isLoading && items.length === 0 && (
          <li className="p-8 text-center text-xs text-slate-400">
            {activeFilter === "unread" ? t("noUnreadMessages") : t("noConversations")}
          </li>
        )}

        {!isLoading &&
          items.map((conversation) => {
            const active = activeId === conversation.id;
            const isUserA = user?.id === conversation.user_a_id;
            const peerId = isUserA ? conversation.user_b_id : conversation.user_a_id;
            const peer = isUserA ? conversation.user_b : conversation.user_a;
            const isOnline = onlineUserIds.has(peerId);

            let peerName = `User ${peerId.substring(0, 4)}`;
            let peerShort = peerId.substring(0, 2).toUpperCase();

            if (peer) {
              peerName = peer.full_name || peer.email.split("@")[0];
              peerShort = peer.email.substring(0, 2).toUpperCase();
            }

            const dateStr = formatChatListTime(conversation.last_message_at, language);

            return (
              <li key={conversation.id}>
                <div
                  onClick={() => handleSelect(conversation.id)}
                  onMouseEnter={() => {
                    if (!active) {
                      queryClient.prefetchInfiniteQuery({
                        queryKey: ["messages", conversation.id],
                        queryFn: ({ pageParam }) =>
                          getMessages(conversation.id, pageParam?.beforeCreatedAt, pageParam?.beforeId),
                        initialPageParam: undefined as { beforeCreatedAt: string; beforeId: string } | undefined,
                      });
                    }
                  }}
                  className={cn(
                    "flex items-center gap-3 p-3 rounded-2xl cursor-pointer transition-all border",
                    active
                      ? "bg-blue-50/90 border-blue-200 shadow-2xs ring-1 ring-blue-500/20"
                      : "bg-white hover:bg-slate-50 border-transparent hover:border-slate-100"
                  )}
                >
                  {/* Avatar with Presence Indicator */}
                  <div className="relative shrink-0">
                    <Avatar className="h-11 w-11 border border-slate-200 shadow-2xs">
                      {peer?.avatar && <AvatarImage src={peer.avatar} alt={peerName} />}
                      <AvatarFallback className="bg-blue-50 text-blue-700 font-bold text-xs">
                        {peerShort}
                      </AvatarFallback>
                    </Avatar>
                    {isOnline ? (
                      <span className="absolute bottom-0 right-0 h-3.5 w-3.5 rounded-full bg-emerald-500 ring-2 ring-white" title={t("online")} />
                    ) : (
                      <span className="absolute bottom-0 right-0 h-3.5 w-3.5 rounded-full bg-slate-100 border-2 border-slate-400 ring-2 ring-white" title={t("offline")} />
                    )}
                  </div>

                  {/* Content snippet */}
                  <div className="flex-1 min-w-0 flex flex-col gap-1">
                    {/* Row 1: Name & Timestamp */}
                    <div className="flex justify-between items-baseline">
                      <h4 className={cn(
                        "text-xs truncate pr-1",
                        active ? "font-bold text-blue-900" : "font-semibold text-slate-900"
                      )}>
                        {peerName}
                      </h4>
                      <span className="text-[10px] text-slate-400 shrink-0 font-medium">{dateStr}</span>
                    </div>

                    {/* Row 2: Tags */}
                    {conversation.tags && conversation.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {conversation.tags.slice(0, 2).map((tag: any, idx: number) => {
                          const tagName = typeof tag === "string" ? tag : tag.name;
                          const tagColor = typeof tag === "string" ? undefined : tag.color;
                          return (
                            <Badge
                              key={idx}
                              variant="secondary"
                              className="text-[9px] px-1.5 py-0 font-semibold h-4 border-none bg-blue-50 text-blue-600 rounded-md"
                              style={tagColor ? { backgroundColor: `${tagColor}15`, color: tagColor } : undefined}
                            >
                              #{tagName}
                            </Badge>
                          );
                        })}
                      </div>
                    )}

                    {/* Row 3: Last Message & Unread */}
                    <div className="flex justify-between items-center text-xs">
                      <p
                        className={cn(
                          "truncate text-[11px] max-w-[170px]",
                          conversation.unread_count && conversation.unread_count > 0
                            ? "font-bold text-slate-900"
                            : "text-slate-500"
                        )}
                      >
                        {conversation.last_message || t("noMessages")}
                      </p>
                      {conversation.unread_count && conversation.unread_count > 0 ? (
                        <span className="shrink-0 flex h-4 min-w-4 items-center justify-center rounded-full bg-blue-600 px-1 text-[10px] font-bold text-white shadow-xs">
                          {conversation.unread_count}
                        </span>
                      ) : null}
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
