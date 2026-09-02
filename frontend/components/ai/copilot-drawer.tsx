"use client";

import { useEffect, useRef, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  X,
  Send,
  Copy,
  Loader2,
  Sparkles,
  Trash2,
  Bot,
  MessageSquare,
  Lock,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useUIStore } from "@/lib/stores/ui-store";
import { useConversationStore } from "@/lib/stores/conversation-store";
import { useAuthStore } from "@/lib/stores/auth-store";
import {
  askCopilot,
  getCopilotMessages,
  clearCopilotMessages,
  CopilotMessageItem,
} from "@/lib/api/copilot";
import { cn } from "@/lib/utils";
import { renderCopilotMessageWithCards } from "@/components/ai/copilot-card";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";
import { useAISettings } from "@/hooks/use-ai-settings";

const IN_CHAT_QUICK_ACTIONS = [
  { id: "summary", label: "Tóm tắt đoạn chat", query: "Hãy tóm tắt ngắn gọn các ý chính và thỏa thuận trong cuộc trò chuyện này." },
  { id: "suggest", label: "Gợi ý trả lời", query: "Dựa vào các tin nhắn gần nhất, hãy gợi ý cho tôi 2-3 phương án trả lời lịch sự và phù hợp." },
  { id: "keypoints", label: "Điểm cần lưu ý", query: "Có những mốc thời gian, công việc hoặc cam kết nào quan trọng trong đoạn chat này cần lưu ý không?" },
  { id: "partner", label: "Thông tin đối tác", query: "Hãy cho tôi biết kỹ năng, công ty và các thông tin đã biết về người đang chat này." },
] as const;

export function CopilotDrawer() {
  const open = useUIStore((s) => s.copilotOpen);
  const toggleCopilot = useUIStore((s) => s.toggleCopilot);
  const queryClient = useQueryClient();

  const activeConversationId = useConversationStore((s) => s.activeConversationId);
  const conversations = useConversationStore((s) => s.conversations);
  const currentUser = useAuthStore((s) => s.user);
  const { features, chatCopilotSettings } = useAISettings();

  const activeConv = conversations.find((c) => c.id === activeConversationId);
  const isUserA = activeConv && currentUser?.id === activeConv.user_a_id;
  const peer = isUserA ? activeConv?.user_b : activeConv?.user_a;
  const peerName = peer?.full_name || (peer?.email ? peer.email.split("@")[0] : "đối tác");

  const [input, setInput] = useState("");
  const [localMessages, setLocalMessages] = useState<CopilotMessageItem[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Fetch in-chat copilot messages history for this specific conversation
  const { data: dbMessages, isLoading: historyLoading } = useQuery({
    queryKey: ["copilot-messages", activeConversationId],
    queryFn: () => getCopilotMessages(100, activeConversationId),
    enabled: !!activeConversationId && open,
  });

  useEffect(() => {
    if (dbMessages) {
      setLocalMessages(dbMessages);
    }
  }, [dbMessages]);

  // Clear local state when switching conversation
  useEffect(() => {
    if (!activeConversationId) {
      setLocalMessages([]);
    }
  }, [activeConversationId]);

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [localMessages, historyLoading]);

  // Clear in-chat Copilot messages mutation
  const clearMutation = useMutation({
    mutationFn: () => clearCopilotMessages(activeConversationId),
    onSuccess: () => {
      setLocalMessages([]);
      queryClient.setQueryData(["copilot-messages", activeConversationId], []);
      toast.success("Đã xóa lịch sử Copilot của cuộc trò chuyện này.");
    },
    onError: () => {
      toast.error("Không thể xóa lịch sử Copilot.");
    },
  });

  // Send message mutation
  const sendMutation = useMutation({
    mutationFn: async (query: string) => {
      return askCopilot({
        query,
        context: activeConversationId ? { conversation_id: activeConversationId } : undefined,
      });
    },
    onSuccess: (data, userQuery) => {
      const assistantMsg: CopilotMessageItem = {
        id: data.id || `ai-${Date.now()}`,
        role: "assistant",
        content: data.response,
        tools_used: data.tools_used,
        sources: data.sources,
        intent: data.intent,
        conversation_id: activeConversationId,
        created_at: new Date().toISOString(),
      };
      setLocalMessages((prev) => [...prev, assistantMsg]);
      queryClient.invalidateQueries({ queryKey: ["copilot-messages", activeConversationId] });
    },
    onError: (err: any) => {
      const errMsg: CopilotMessageItem = {
        id: `err-${Date.now()}`,
        role: "assistant",
        content: err?.message || "Xin lỗi, đã xảy ra lỗi trong quá trình phân tích cuộc hội thoại.",
        conversation_id: activeConversationId,
        created_at: new Date().toISOString(),
      };
      setLocalMessages((prev) => [...prev, errMsg]);
    },
  });

  const handleAsk = (text: string) => {
    const query = text.trim();
    if (!query || sendMutation.isPending) return;

    setInput("");
    const userMsg: CopilotMessageItem = {
      id: `user-${Date.now()}`,
      role: "user",
      content: query,
      conversation_id: activeConversationId,
      created_at: new Date().toISOString(),
    };

    setLocalMessages((prev) => [...prev, userMsg]);
    sendMutation.mutate(query);
  };

  // Listen for external copilot-query events
  useEffect(() => {
    const handler = (e: any) => {
      const query = e.detail;
      if (query && !sendMutation.isPending) {
        handleAsk(query);
      }
    };
    window.addEventListener("copilot-query", handler);
    return () => window.removeEventListener("copilot-query", handler);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeConversationId, sendMutation.isPending]);

  const handleCopy = (text: string) => {
    window.dispatchEvent(new CustomEvent("insert-composer", { detail: text }));
    toast.success("Đã sao chép vào khung soạn tin nhắn.");
  };

  const handleClearHistory = () => {
    if (confirm(`Bạn có chắc muốn xóa lịch sử Copilot của đoạn chat với ${peerName}?`)) {
      clearMutation.mutate();
    }
  };

  if (!open) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-40 bg-slate-900/30 backdrop-blur-xs transition-opacity animate-in fade-in-0 duration-200"
        onClick={toggleCopilot}
        aria-hidden="true"
      />

      <aside
        aria-labelledby="in-chat-copilot-title"
        className={cn(
          "fixed right-0 top-0 z-50 flex h-full w-full max-w-md flex-col border-l border-slate-200 bg-white shadow-2xl transition-transform duration-300 ease-out",
          open ? "translate-x-0" : "translate-x-full"
        )}
      >
        {/* Drawer Header */}
        <header className="flex items-center justify-between border-b border-slate-100 bg-slate-50/80 px-5 py-4 shrink-0">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-600 text-white shadow-sm shadow-blue-500/20">
              <Sparkles size={18} />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <h2 id="in-chat-copilot-title" className="text-sm font-bold text-slate-900">
                  Copilot Đoạn Chat
                </h2>
                <span className="rounded-full bg-blue-50 border border-blue-200 px-2 py-0.2 text-[10px] font-bold text-blue-700">
                  Riêng biệt
                </span>
              </div>
              <p className="text-[11px] text-slate-500 truncate max-w-[210px]">
                Ngữ cảnh: <span className="font-semibold text-slate-700">{peerName}</span>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-1">
            {localMessages.length > 0 && (
              <Button
                variant="ghost"
                size="icon-sm"
                onClick={handleClearHistory}
                disabled={clearMutation.isPending}
                className="h-8 w-8 rounded-xl text-slate-400 hover:text-red-600 hover:bg-red-50"
                title="Xóa lịch sử Copilot đoạn chat này"
              >
                <Trash2 size={15} />
              </Button>
            )}
            <Button
              variant="ghost"
              size="icon-sm"
              onClick={toggleCopilot}
              className="h-8 w-8 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-100"
              aria-label="Đóng Copilot"
            >
              <X size={16} />
            </Button>
          </div>
        </header>

        {/* Feature disabled warning */}
        {features.chat_copilot === false ? (
          <div className="flex flex-1 flex-col items-center justify-center p-6 text-center space-y-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100 text-slate-400">
              <Lock size={24} />
            </div>
            <h3 className="text-sm font-bold text-slate-800">In-Chat Copilot đang tắt</h3>
            <p className="text-xs text-slate-500 max-w-xs">
              Tính năng Copilot riêng cho đoạn chat đã được tắt trong phần Cài đặt AI Hub.
            </p>
          </div>
        ) : (
          <>
            {/* Quick Action Suggestions */}
            {chatCopilotSettings.quickActions && (
              <div className="border-b border-slate-100 bg-white p-3 shrink-0">
                <div className="flex flex-wrap gap-1.5">
                  {IN_CHAT_QUICK_ACTIONS.map((action) => (
                    <button
                      key={action.id}
                      onClick={() => handleAsk(action.query)}
                      disabled={sendMutation.isPending}
                      className="rounded-xl border border-blue-100 bg-blue-50/60 px-2.5 py-1 text-[11px] font-semibold text-blue-700 hover:bg-blue-100 hover:text-blue-800 transition-colors disabled:opacity-50 cursor-pointer text-left"
                    >
                      {action.label}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Messages Scroll Area */}
            <div
              ref={scrollRef}
              className="scrollbar-thin flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50/50"
            >
              {historyLoading ? (
                <div className="flex items-center justify-center py-12 text-xs text-slate-400 gap-2">
                  <Loader2 size={16} className="animate-spin text-blue-600" />
                  <span>Đang tải lịch sử Copilot đoạn chat...</span>
                </div>
              ) : localMessages.length === 0 ? (
                <div className="rounded-2xl border border-blue-100 bg-white p-5 text-center space-y-2.5 shadow-2xs">
                  <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-2xl bg-blue-50 text-blue-600">
                    <MessageSquare size={18} />
                  </div>
                  <h4 className="text-xs font-bold text-slate-800">
                    Copilot riêng cho đoạn chat này
                  </h4>
                  <p className="text-[11px] leading-relaxed text-slate-500">
                    Mọi câu hỏi và phân tích tại đây được <strong>giới hạn chính xác trong ngữ cảnh cuộc trò chuyện với {peerName}</strong>. Lịch sử trao đổi này tách biệt hoàn toàn so với trang AI Copilot tổng.
                  </p>
                </div>
              ) : (
                localMessages.map((msg) => (
                  <div
                    key={msg.id}
                    className={cn(
                      "flex flex-col gap-1 max-w-[95%]",
                      msg.role === "user" ? "ml-auto items-end" : "mr-auto items-start w-full"
                    )}
                  >
                    <div
                      className={cn(
                        "rounded-2xl px-4 py-2.5 text-xs shadow-2xs leading-relaxed",
                        msg.role === "user"
                          ? "bg-blue-600 text-white rounded-tr-xs font-medium"
                          : "bg-white border border-slate-200/80 text-slate-800 rounded-tl-xs w-full"
                      )}
                    >
                      {renderCopilotMessageWithCards(msg.content)}
                    </div>

                    {msg.role === "assistant" && (
                      <div className="flex items-center gap-1 mt-0.5">
                        <Button
                          variant="ghost"
                          size="xs"
                          onClick={() => handleCopy(msg.content)}
                          className="h-6 px-2 text-[10px] font-semibold text-slate-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg"
                        >
                          <Copy size={11} className="mr-1" />
                          <span>Dán vào ô chat</span>
                        </Button>
                      </div>
                    )}
                  </div>
                ))
              )}

              {sendMutation.isPending && (
                <div className="flex items-center gap-2 rounded-2xl bg-white border border-slate-200 px-4 py-3 text-xs text-slate-500 shadow-2xs mr-auto">
                  <Loader2 size={14} className="animate-spin text-blue-600" />
                  <span>AI đang đọc và phân tích đoạn chat...</span>
                </div>
              )}
            </div>

            {/* Input Composer */}
            <footer className="border-t border-slate-200 bg-white p-3 shrink-0">
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleAsk(input);
                }}
                className="flex items-center gap-2"
              >
                <Input
                  type="text"
                  placeholder={`Hỏi về cuộc trò chuyện với ${peerName}...`}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  disabled={sendMutation.isPending}
                  className="h-10 flex-1 rounded-2xl border-slate-200 bg-slate-50 px-3.5 text-xs focus:border-blue-500 focus:bg-white"
                />
                <Button
                  type="submit"
                  size="sm"
                  disabled={!input.trim() || sendMutation.isPending}
                  className="h-10 px-3 rounded-2xl bg-blue-600 hover:bg-blue-700 text-white shadow-xs cursor-pointer"
                  aria-label="Gửi câu hỏi"
                >
                  <Send size={15} />
                </Button>
              </form>
            </footer>
          </>
        )}
      </aside>
    </>
  );
}
