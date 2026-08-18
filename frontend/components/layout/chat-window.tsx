"use client";

import {
  MoreVertical,
  PanelRightClose,
  PanelRightOpen,
  Sparkles,
  User,
} from "lucide-react";
import { AIContextBar } from "@/components/ai/ai-context-bar";
import { useUIStore } from "@/lib/stores/ui-store";
import { useConversationStore } from "@/lib/stores/conversation-store";
import { useAuthStore } from "@/lib/stores/auth-store";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getMessages, deleteMessage } from "@/lib/api/messages";
import { getConversations } from "@/lib/api/conversations";
import { Composer } from "@/components/chat/composer";
import { MessageBubble } from "@/components/chat/message-bubble";
import { cn } from "@/lib/utils";
import type { Conversation } from "@/types";
import { Skeleton } from "@/components/ui/skeleton";

export function ChatWindow() {
  const infoPanelOpen = useUIStore((s) => s.infoPanelOpen);
  const toggleInfoPanel = useUIStore((s) => s.toggleInfoPanel);
  const toggleCopilot = useUIStore((s) => s.toggleCopilot);
  const connectionState = useUIStore((s) => s.connectionState);
  
  const user = useAuthStore((s) => s.user);
  const activeId = useConversationStore((s) => s.activeConversationId);
  const conversations = useConversationStore((s) => s.conversations);

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

  const { data: messagesResponse, isLoading } = useQuery({
    queryKey: ["messages", activeId],
    queryFn: () => getMessages(activeId!),
    enabled: !!activeId,
  });

  if (!activeId) {
    return (
      <section className="flex min-w-0 flex-1 flex-col items-center justify-center bg-app">
        <div className="text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-elevated text-secondary">
            <User size={32} />
          </div>
          <h2 className="text-xl font-bold">Your Conversations</h2>
          <p className="mt-2 text-sm text-secondary">Select a chat or start a new one.</p>
        </div>
      </section>
    );
  }

  const messages = messagesResponse?.data ?? [];

  return (
    <section className="flex min-w-0 flex-1 flex-col bg-app">
      <header className="flex items-center justify-between border-b border-subtle px-4 py-3">
        <div 
          className="flex items-center gap-3 cursor-pointer hover:opacity-90 transition-opacity"
          onClick={toggleInfoPanel}
          title="Xem thông tin đối phương"
        >
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-500/20 text-sm font-semibold text-blue-300 uppercase">
            {peerShort}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-semibold">{peerName}</h1>
              <span className="rounded-full bg-elevated px-2 py-0.5 text-xs text-secondary">
                Peer
              </span>
            </div>
            <p className="text-xs text-secondary">Direct message</p>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <button
            type="button"
            onClick={toggleCopilot}
            className="rounded-button p-2 text-secondary hover:bg-elevated hover:text-accent"
            aria-label="Open copilot"
            title="Mở AI Copilot"
          >
            <Sparkles size={18} />
          </button>
          <button
            type="button"
            onClick={toggleInfoPanel}
            className="rounded-button p-2 text-secondary hover:bg-elevated hover:text-primary"
            aria-label="View profile"
            title="Thông tin đối phương"
          >
            <User size={18} />
          </button>
          <button
            type="button"
            onClick={toggleInfoPanel}
            className="rounded-button p-2 text-secondary hover:bg-elevated hover:text-primary"
            aria-label={infoPanelOpen ? "Hide info panel" : "Show info panel"}
            title={infoPanelOpen ? "Đóng thanh thông tin" : "Mở thanh thông tin"}
          >
            {infoPanelOpen ? (
              <PanelRightClose size={18} />
            ) : (
              <PanelRightOpen size={18} />
            )}
          </button>
          <button
            type="button"
            onClick={toggleInfoPanel}
            className="rounded-button p-2 text-secondary hover:bg-elevated hover:text-primary"
            aria-label="Contact info"
            title="Tùy chọn & Thông tin đối phương"
          >
            <MoreVertical size={18} />
          </button>
        </div>
      </header>


      <AIContextBar />

      <div className="flex items-center gap-2 border-b border-subtle px-4 py-2">
        <span 
          className={cn(
            "h-2 w-2 rounded-full",
            connectionState === "connected" ? "bg-online" : connectionState === "reconnecting" ? "bg-yellow-500" : "bg-red-500"
          )} 
        />
        <span className="text-xs text-secondary">
          {connectionState === "connected" ? "Real-time connected" : connectionState === "reconnecting" ? "Reconnecting..." : "Offline"}
        </span>
      </div>

      <div className="scrollbar-thin flex-1 space-y-4 overflow-y-auto px-4 py-6 flex flex-col-reverse">
        {isLoading && (
          <div className="flex flex-col-reverse gap-4 w-full">
            {[1, 2, 3].map((i) => (
              <div key={i} className={`flex ${i % 2 === 0 ? "justify-end" : "justify-start"}`}>
                <Skeleton className={`h-12 w-2/3 ${i % 2 === 0 ? "rounded-l-2xl rounded-tr-2xl bg-accent/20" : "rounded-r-2xl rounded-tl-2xl bg-elevated"}`} />
              </div>
            ))}
          </div>
        )}
        {!isLoading && messages.length === 0 && <p className="text-center text-xs text-secondary w-full">No messages yet. Say hi!</p>}
        
        {/* Messages are returned DESC from API (newest first). flex-col-reverse puts the first item at the bottom. */}
        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            content={message.content}
            outgoing={message.sender_user_id === user?.id || message.sender_user_id === "optimistic"}
            time={new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            status={message.sender_user_id === "optimistic" ? "pending" : "sent"}
            deleted_at={message.deleted_at}
            onRecall={() => recallMutation.mutate(message.id)}
            isRecalling={recallMutation.isPending && recallMutation.variables === message.id}
          />
        ))}
      </div>

      <footer className="border-t border-subtle p-4">
        <Composer conversationId={activeId} />
      </footer>
    </section>
  );
}
