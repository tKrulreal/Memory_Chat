"use client";

import {
  MoreVertical,
  PanelRightClose,
  PanelRightOpen,
  Sparkles,
  User,
} from "lucide-react";
import { useEffect } from "react";
import { useInView } from "react-intersection-observer";
import { useSendMessage } from "@/hooks/use-send-message";
import { AIContextBar } from "@/components/ai/ai-context-bar";
import { useUIStore } from "@/lib/stores/ui-store";
import { useConversationStore } from "@/lib/stores/conversation-store";
import { useAuthStore } from "@/lib/stores/auth-store";
import { useInfiniteQuery, useMutation, useQueryClient, useQuery } from "@tanstack/react-query";
import { getMessages, deleteMessage } from "@/lib/api/messages";
import { getConversations } from "@/lib/api/conversations";
import { Composer } from "@/components/chat/composer";
import { MessageBubble } from "@/components/chat/message-bubble";
import { cn } from "@/lib/utils";
import type { Conversation } from "@/types";
import { Skeleton } from "@/components/ui/skeleton";
import { useAISettings } from "@/hooks/use-ai-settings";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

export function ChatWindow() {
  const infoPanelOpen = useUIStore((s) => s.infoPanelOpen);
  const toggleInfoPanel = useUIStore((s) => s.toggleInfoPanel);
  const toggleCopilot = useUIStore((s) => s.toggleCopilot);
  const connectionState = useUIStore((s) => s.connectionState);
  
  const user = useAuthStore((s) => s.user);
  const activeId = useConversationStore((s) => s.activeConversationId);
  const conversations = useConversationStore((s) => s.conversations);
  
  const sendMessageMutation = useSendMessage(activeId || "");
  const { features } = useAISettings();

  const { data: activeConversations = [] } = useQuery({
    queryKey: ["conversations"],
    queryFn: getConversations,
    enabled: !!user,
  });
  
  const queryClient = useQueryClient();

  const recallMutation = useMutation({
    mutationFn: (messageId: string) => deleteMessage(messageId),
    onSuccess: (_, messageId) => {
      // The websocket will handle updating the cache, but we could do it optimistically here too if wanted.
      // Since the prompt requested: "Do not optimistically mark the message as recalled before the backend confirms success."
      // We'll just let the websocket or the next fetch handle it.
    },
    onError: (error) => {
      console.error("Failed to recall message:", error);
      // Could show a toast here if a toast system was available
    }
  });
  
  // Actually, I should use queryClient or just use the data from useQuery for conversations
  // Alternatively, just grab it from query cache:
  const activeConversation = activeConversations.find(c => c.id === activeId);
  const isUserA = activeConversation && user?.id === activeConversation.user_a_id;
  const peerId = activeConversation 
    ? (isUserA ? activeConversation.user_b_id : activeConversation.user_a_id)
    : "Unknown";
  const peer = isUserA ? activeConversation?.user_b : activeConversation?.user_a;
  
  let peerName = activeConversation ? `User ${peerId.substring(0, 4)}` : "Unknown";
  let peerShort = activeConversation ? peerId.substring(0, 2).toUpperCase() : "UN";
  
  if (peer) {
    peerName = peer.full_name || peer.email.split('@')[0];
    peerShort = peer.email.substring(0, 2).toUpperCase();
  }

  const { 
    data: messagesResponse, 
    isLoading,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage
  } = useInfiniteQuery({
    queryKey: ["messages", activeId],
    queryFn: ({ pageParam }) => getMessages(activeId!, pageParam?.beforeCreatedAt, pageParam?.beforeId),
    getNextPageParam: (lastPage) => {
      if (!lastPage.pagination.has_next || lastPage.data.length === 0) return undefined;
      const lastMessage = lastPage.data[lastPage.data.length - 1];
      return {
        beforeCreatedAt: lastMessage.created_at,
        beforeId: lastMessage.id
      };
    },
    initialPageParam: undefined as { beforeCreatedAt: string, beforeId: string } | undefined,
    enabled: !!activeId,
  });

  const { ref, inView } = useInView();

  useEffect(() => {
    if (inView && hasNextPage && !isFetchingNextPage) {
      fetchNextPage();
    }
  }, [inView, hasNextPage, isFetchingNextPage, fetchNextPage]);

  // Mark as read when active conversation changes or new messages arrive
  useEffect(() => {
    if (activeId) {
      import('@/lib/api/conversations').then(({ markAsRead }) => {
        markAsRead(activeId).then(() => {
          // Invalidate conversations to update unread badge
          queryClient.invalidateQueries({ queryKey: ["conversations"] });
        }).catch(console.error);
      });
    }
  }, [activeId, queryClient, messagesResponse]);

  if (!activeId) {
    return (
      <section className="flex min-w-0 flex-1 flex-col items-center justify-center bg-background">
        <div className="text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-muted text-muted-foreground">
            <User size={32} />
          </div>
          <h2 className="text-xl font-bold">Your Conversations</h2>
          <p className="mt-2 text-sm text-muted-foreground">Select a chat or start a new one.</p>
        </div>
      </section>
    );
  }

  const messages = messagesResponse?.pages.flatMap((page) => page.data) ?? [];

  return (
    <section className="flex min-w-0 flex-1 flex-col bg-background min-h-0">
      <header className="flex shrink-0 items-center justify-between border-b border-slate-100/50 px-6 py-4 bg-white/80 backdrop-blur-sm z-10">
        <div
          className="flex items-center gap-3 cursor-pointer hover:opacity-90 transition-opacity"
          onClick={toggleInfoPanel}
          title="Xem thông tin đối phương"
        >
          <Avatar className="h-10 w-10 border border-slate-200 shadow-sm">
            <AvatarFallback className="bg-blue-50 text-blue-700 font-bold text-sm">
              {peerShort}
            </AvatarFallback>
          </Avatar>
          <div>
            <div className="flex items-center gap-2 mb-0.5">
              <h1 className="text-base font-semibold text-slate-900">{peerName}</h1>
              <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] uppercase tracking-wider font-semibold text-slate-500">
                Peer
              </span>
            </div>
            <p className="text-xs font-medium text-slate-500">Direct message</p>
          </div>
        </div>
        <div className="flex items-center gap-1">
          {features.copilot && (
            <Button variant="ghost"
              type="button"
              onClick={toggleCopilot}
              className="rounded-button p-2 text-muted-foreground hover:bg-muted hover:text-accent"
              aria-label="Open copilot"
              title="Mở AI Copilot"
            >
              <Sparkles size={18} />
            </Button>
          )}
          <Button variant="ghost"
            type="button"
            onClick={toggleInfoPanel}
            className="rounded-button p-2 text-muted-foreground hover:bg-muted hover:text-foreground"
            aria-label="View profile"
            title="Thông tin đối phương"
          >
            <User size={18} />
          </Button>
          <Button variant="ghost"
            type="button"
            onClick={toggleInfoPanel}
            className="rounded-button p-2 text-muted-foreground hover:bg-muted hover:text-foreground"
            aria-label={infoPanelOpen ? "Hide info panel" : "Show info panel"}
            title={infoPanelOpen ? "Đóng thanh thông tin" : "Mở thanh thông tin"}
          >
            {infoPanelOpen ? (
              <PanelRightClose size={18} />
            ) : (
              <PanelRightOpen size={18} />
            )}
          </Button>
          <Button variant="ghost"
            type="button"
            onClick={toggleInfoPanel}
            className="rounded-button p-2 text-muted-foreground hover:bg-muted hover:text-foreground"
            aria-label="Contact info"
            title="Tùy chọn & Thông tin đối phương"
          >
            <MoreVertical size={18} />
          </Button>
        </div>
      </header>


      {features.memory && <AIContextBar />}



      <div className="scrollbar-thin flex-1 min-h-0 overflow-y-auto px-6 lg:px-8 py-6 flex flex-col-reverse items-center">
        <div className="w-full max-w-5xl flex flex-col-reverse space-y-4 space-y-reverse">
          {isLoading && (
            <div className="flex flex-col-reverse gap-4 w-full">
              {[1, 2, 3].map((i) => (
                <div key={i} className={`flex ${i % 2 === 0 ? "justify-end" : "justify-start"}`}>
                  <Skeleton className={`h-12 w-2/3 ${i % 2 === 0 ? "rounded-l-2xl rounded-tr-2xl bg-accent/20" : "rounded-r-2xl rounded-tl-2xl bg-muted"}`} />
                </div>
              ))}
            </div>
          )}
          {!isLoading && messages.length === 0 && <p className="text-center text-sm text-muted-foreground w-full">No messages yet. Say hi!</p>}

          {hasNextPage && (
            <div ref={ref} className="flex justify-center w-full py-2">
              <span className="text-sm text-muted-foreground opacity-50">
                {isFetchingNextPage ? "Loading older messages..." : "Scroll for more"}
              </span>
            </div>
          )}

          {/* Messages are returned DESC from API (newest first). flex-col-reverse puts the first item at the bottom. */}
        {messages.map((message, index) => {
          const isConsecutive = index > 0 && messages[index - 1]?.sender_user_id === message.sender_user_id;
          return (
            <MessageBubble
              key={message.id}
              isConsecutive={isConsecutive}
              content={message.content}
              outgoing={message.sender_user_id === user?.id || message.sender_user_id === "optimistic"}
              time={new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              status={message.local_status === "failed" ? "error" : message.local_status === "sending" || message.sender_user_id === "optimistic" ? "pending" : "sent"}
              deleted_at={message.deleted_at}
              onRecall={() => recallMutation.mutate(message.id)}
              isRecalling={recallMutation.isPending && recallMutation.variables === message.id}
              onRetry={() => {
                if (message.client_message_id) {
                  sendMessageMutation.mutate({
                    content: message.content,
                    clientMessageId: message.client_message_id,
                  });
                }
              }}
            />
          );
        })}
        </div>
      </div>

      <footer className="shrink-0 border-t border-subtle p-4 bg-card flex justify-center">
        <div className="w-full max-w-5xl">
          <Composer conversationId={activeId} />
        </div>
      </footer>
    </section>
  );
}
