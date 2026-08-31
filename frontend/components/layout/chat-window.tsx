"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  MoreVertical,
  PanelRightClose,
  PanelRightOpen,
  Sparkles,
  User,
  UserMinus,
  ExternalLink,
  MessageSquare,
} from "lucide-react";
import { useInView } from "react-intersection-observer";
import { useSendMessage } from "@/hooks/use-send-message";
import { AIContextBar } from "@/components/ai/ai-context-bar";
import { useUIStore } from "@/lib/stores/ui-store";
import { useConversationStore } from "@/lib/stores/conversation-store";
import { useAuthStore } from "@/lib/stores/auth-store";
import { usePresenceStore } from "@/lib/stores/presence-store";
import { useInfiniteQuery, useMutation, useQueryClient, useQuery } from "@tanstack/react-query";
import { getMessages, deleteMessage } from "@/lib/api/messages";
import { getConversations } from "@/lib/api/conversations";
import { unfriendUser } from "@/lib/api/connection-requests";
import { Composer } from "@/components/chat/composer";
import { MessageBubble } from "@/components/chat/message-bubble";
import { cn, formatMessageTime, parseServerDate, getDateDividerLabel } from "@/lib/utils";
import type { Conversation } from "@/types";
import { Skeleton } from "@/components/ui/skeleton";
import { useAISettings } from "@/hooks/use-ai-settings";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { toast } from "sonner";
import { useLanguage } from "@/hooks/use-language";

export function ChatWindow() {
  const router = useRouter();
  const infoPanelOpen = useUIStore((s) => s.infoPanelOpen);
  const toggleInfoPanel = useUIStore((s) => s.toggleInfoPanel);
  const toggleCopilot = useUIStore((s) => s.toggleCopilot);

  const user = useAuthStore((s) => s.user);
  const activeId = useConversationStore((s) => s.activeConversationId);
  const setActiveConversation = useConversationStore((s) => s.setActiveConversation);

  const sendMessageMutation = useSendMessage(activeId || "");
  const { features } = useAISettings();
  const { language, t } = useLanguage();

  const { data: activeConversations = [] } = useQuery({
    queryKey: ["conversations"],
    queryFn: getConversations,
    enabled: !!user,
  });

  const queryClient = useQueryClient();

  const recallMutation = useMutation({
    mutationFn: (messageId: string) => deleteMessage(messageId),
    onSuccess: () => {},
    onError: (error) => {
      console.error("Failed to recall message:", error);
    },
  });

  const unfriendMutation = useMutation({
    mutationFn: (targetUserId: string) => unfriendUser(targetUserId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["conversations"] });
      queryClient.invalidateQueries({ queryKey: ["connection-requests"] });
      queryClient.invalidateQueries({ queryKey: ["connections"] });
      setActiveConversation(null);
      toast.success(t("unfriendSuccess"));
    },
    onError: (err: any) => {
      toast.error(err.message || t("unfriendError"));
    },
  });

  const activeConversation = activeConversations.find((c) => c.id === activeId);
  const isUserA = activeConversation && user?.id === activeConversation.user_a_id;
  const peerId = activeConversation
    ? isUserA
      ? activeConversation.user_b_id
      : activeConversation.user_a_id
    : "";
  const peer = isUserA ? activeConversation?.user_b : activeConversation?.user_a;
  const onlineUserIds = usePresenceStore((s) => s.onlineUserIds);
  const isPeerOnline = peerId ? onlineUserIds.has(peerId) : false;

  let peerName = activeConversation ? `User ${peerId.substring(0, 4)}` : "Unknown";
  let peerShort = activeConversation ? peerId.substring(0, 2).toUpperCase() : "UN";

  if (peer) {
    peerName = peer.full_name || peer.email.split("@")[0];
    peerShort = peer.email.substring(0, 2).toUpperCase();
  }

  const {
    data: messagesResponse,
    isLoading,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useInfiniteQuery({
    queryKey: ["messages", activeId],
    queryFn: ({ pageParam }) =>
      getMessages(activeId!, pageParam?.beforeCreatedAt, pageParam?.beforeId),
    getNextPageParam: (lastPage) => {
      if (!lastPage.pagination.has_next || lastPage.data.length === 0) return undefined;
      const lastMessage = lastPage.data[lastPage.data.length - 1];
      return {
        beforeCreatedAt: lastMessage.created_at,
        beforeId: lastMessage.id,
      };
    },
    initialPageParam: undefined as { beforeCreatedAt: string; beforeId: string } | undefined,
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
      import("@/lib/api/conversations").then(({ markAsRead }) => {
        markAsRead(activeId)
          .then(() => {
            queryClient.invalidateQueries({ queryKey: ["conversations"] });
          })
          .catch(console.error);
      });
    }
  }, [activeId, queryClient, messagesResponse]);

  if (!activeId) {
    return (
      <section className="flex min-w-0 flex-1 flex-col items-center justify-center bg-slate-50 p-8">
        <div className="text-center max-w-sm space-y-4">
          <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-3xl bg-white border border-slate-200 text-blue-600 shadow-sm">
            <MessageSquare size={36} />
          </div>
          <div className="space-y-1.5">
            <h2 className="text-lg font-bold text-slate-900">{t("yourConversations")}</h2>
            <p className="text-xs text-slate-500 leading-relaxed">
              {t("selectConversationHelp")}
            </p>
          </div>
        </div>
      </section>
    );
  }

  const messages = messagesResponse?.pages.flatMap((page) => page.data) ?? [];

  return (
    <section className="flex min-w-0 flex-1 flex-col bg-slate-50 min-h-0">
      {/* Top Chat Header */}
      <header className="flex shrink-0 items-center justify-between border-b border-slate-200/80 px-6 py-3.5 bg-white/90 backdrop-blur-md z-10">
        <div
          className="flex items-center gap-3 cursor-pointer hover:opacity-90 transition-opacity"
          onClick={toggleInfoPanel}
          title={t("viewPeerInfo")}
        >
          <div className="relative shrink-0">
            <Avatar className="h-10 w-10 border border-slate-200 shadow-2xs">
              {peer?.avatar && <AvatarImage src={peer.avatar} alt={peerName} />}
              <AvatarFallback className="bg-blue-50 text-blue-700 font-bold text-xs">
                {peerShort}
              </AvatarFallback>
            </Avatar>
            {isPeerOnline ? (
              <span className="absolute bottom-0 right-0 h-3 w-3 rounded-full bg-emerald-500 ring-2 ring-white" title={t("online")} />
            ) : (
              <span className="absolute bottom-0 right-0 h-3 w-3 rounded-full bg-slate-100 border-2 border-slate-400 ring-2 ring-white" title={t("offline")} />
            )}
          </div>
          <div>
            <div className="flex items-center gap-2 mb-0.5">
              <h1 className="text-sm font-bold text-slate-900">{peerName}</h1>
              <span className="rounded-full bg-slate-100 px-2 py-0.2 text-[9px] uppercase tracking-wider font-bold text-slate-500">
                Peer
              </span>
            </div>
            {isPeerOnline ? (
              <p className="flex items-center gap-1 text-[11px] font-medium text-emerald-600">
                <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                <span>{t("online")}</span>
              </p>
            ) : (
              <p className="flex items-center gap-1 text-[11px] font-medium text-slate-400">
                <span className="h-2 w-2 rounded-full border border-slate-400" />
                <span>{t("offline")}</span>
              </p>
            )}
          </div>
        </div>

        {/* Header Action Buttons */}
        <div className="flex items-center gap-1.5">
          {features.copilot && (
            <Button
              variant="ghost"
              type="button"
              onClick={toggleCopilot}
              className="h-9 w-9 p-0 rounded-xl text-blue-600 hover:bg-blue-50 cursor-pointer"
              title={t("openCopilot")}
            >
              <Sparkles size={17} />
            </Button>
          )}
          <Button
            variant="ghost"
            type="button"
            onClick={toggleInfoPanel}
            className="h-9 w-9 p-0 rounded-xl text-slate-600 hover:bg-slate-100 cursor-pointer"
            title={infoPanelOpen ? t("closeInfo") : t("openInfo")}
          >
            {infoPanelOpen ? <PanelRightClose size={17} /> : <PanelRightOpen size={17} />}
          </Button>

          <DropdownMenu>
            <DropdownMenuTrigger
              className="h-9 w-9 inline-flex items-center justify-center rounded-xl text-slate-600 hover:bg-slate-100 cursor-pointer transition-colors focus:outline-none"
              title={t("moreOptions")}
            >
              <MoreVertical size={17} />
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="rounded-2xl shadow-lg border-slate-200 p-1 min-w-[160px]">
              <DropdownMenuItem
                onClick={() => peerId && router.push(`/profile/${peerId}`)}
                className="text-xs font-semibold cursor-pointer rounded-xl"
              >
                <ExternalLink size={13} className="mr-2" />
                {t("viewProfile")}
              </DropdownMenuItem>
              <DropdownMenuSeparator className="my-1 bg-slate-100" />
              <DropdownMenuItem
                onClick={() => {
                  if (
                    peerId &&
                    confirm(language === "en"
                      ? `Are you sure you want to unfriend ${peerName}? This conversation will end.`
                      : `Bạn có chắc chắn muốn hủy kết bạn với ${peerName}? Cuộc trò chuyện này sẽ kết thúc.`)
                  ) {
                    unfriendMutation.mutate(peerId);
                  }
                }}
                disabled={unfriendMutation.isPending}
                className="text-xs font-semibold cursor-pointer text-red-600 hover:text-red-700 hover:bg-red-50 rounded-xl"
              >
                <UserMinus size={13} className="mr-2" />
                {t("unfriend")}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </header>

      {/* AI Context Bar */}
      {features.memory && <AIContextBar />}

      {/* Messages Scroll Area */}
      <div className="scrollbar-thin flex-1 min-h-0 overflow-y-auto px-6 lg:px-8 py-6 flex flex-col-reverse items-center">
        <div className="w-full max-w-4xl flex flex-col-reverse space-y-3 space-y-reverse">
          {isLoading && (
            <div className="flex flex-col-reverse gap-4 w-full">
              {[1, 2, 3].map((i) => (
                <div key={i} className={`flex ${i % 2 === 0 ? "justify-end" : "justify-start"}`}>
                  <Skeleton
                    className={`h-12 w-2/3 ${
                      i % 2 === 0
                        ? "rounded-2xl rounded-tr-none bg-blue-100/60"
                        : "rounded-2xl rounded-tl-none bg-white"
                    }`}
                  />
                </div>
              ))}
            </div>
          )}

          {!isLoading && messages.length === 0 && (
            <div className="text-center py-12 text-xs text-slate-400">
              {t("emptyConversation")}
            </div>
          )}

          {hasNextPage && (
            <div ref={ref} className="flex justify-center w-full py-2">
              <span className="text-xs text-slate-400 opacity-70">
                {isFetchingNextPage ? t("loadingMore") : t("scrollForMore")}
              </span>
            </div>
          )}

          {/* Render Messages */}
          {messages.map((message, index) => {
            const isConsecutive =
              index > 0 && messages[index - 1]?.sender_user_id === message.sender_user_id;
            const msgDate = parseServerDate(message.created_at);
            const olderMsgDate =
              index < messages.length - 1
                ? parseServerDate(messages[index + 1]?.created_at)
                : null;
            const isFirstOfNewDay =
              !olderMsgDate ||
              (msgDate &&
                olderMsgDate &&
                msgDate.toDateString() !== olderMsgDate.toDateString());

            const msgStatus =
              message.local_status === "failed"
                ? "error"
                : message.local_status === "sending" || message.sender_user_id === "optimistic"
                ? "pending"
                : message.is_read
                ? "read"
                : "sent";

            return (
              <div key={message.id} className="w-full flex flex-col items-center">
                {isFirstOfNewDay && msgDate && (
                  <div className="my-3 flex items-center justify-center">
                    <span className="rounded-full bg-white border border-slate-200 px-3.5 py-0.5 text-[10px] font-bold text-slate-500 shadow-2xs">
                      {getDateDividerLabel(msgDate, language)}
                    </span>
                  </div>
                )}
                <MessageBubble
                  isConsecutive={isConsecutive && !isFirstOfNewDay}
                  content={message.content}
                  outgoing={
                    message.sender_user_id === user?.id || message.sender_user_id === "optimistic"
                  }
                  time={formatMessageTime(message.created_at)}
                  status={msgStatus}
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
              </div>
            );
          })}
        </div>
      </div>

      {/* Footer Composer */}
      <footer className="shrink-0 border-t border-slate-200/80 p-4 bg-white flex justify-center shadow-xs">
        <div className="w-full max-w-4xl">
          <Composer conversationId={activeId} />
        </div>
      </footer>
    </section>
  );
}
