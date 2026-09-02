"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Send, Bot, User, Sparkles, Wrench, Lock, Trash2, RotateCcw } from "lucide-react";
import { cn } from "@/lib/utils";
import { renderCopilotMessageWithCards } from "@/components/ai/copilot-card";
import { useAISettings } from "@/hooks/use-ai-settings";
import {
  askCopilot,
  getCopilotMessages,
  clearCopilotMessages,
  CopilotMessageItem,
} from "@/lib/api/copilot";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

const DEFAULT_WELCOME_MESSAGE: CopilotMessageItem = {
  id: "welcome-default",
  role: "assistant",
  content:
    "Xin chào! Mình là Copilot AI. Mình có thể giúp bạn tìm kiếm thông tin về bạn bè, đối tác cũ trong các đoạn chat (theo tóm tắt, tag, sở thích...) hoặc tìm kiếm người dùng mới trên hệ thống dựa theo hồ sơ kỹ năng. Bạn cần mình giúp gì?",
  created_at: new Date().toISOString(),
};

export default function CopilotPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [input, setInput] = useState("");
  const [localMessages, setLocalMessages] = useState<CopilotMessageItem[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { features, isLoading: settingsLoading } = useAISettings();

  // Load chat history from backend database
  const { data: dbMessages, isLoading: historyLoading } = useQuery({
    queryKey: ["copilot-messages", "global"],
    queryFn: () => getCopilotMessages(100, null),
  });

  useEffect(() => {
    if (dbMessages) {
      if (dbMessages.length === 0) {
        setLocalMessages([DEFAULT_WELCOME_MESSAGE]);
      } else {
        setLocalMessages(dbMessages);
      }
    }
  }, [dbMessages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [localMessages]);

  // Mutation to clear history
  const clearMutation = useMutation({
    mutationFn: () => clearCopilotMessages(null),
    onSuccess: () => {
      setLocalMessages([DEFAULT_WELCOME_MESSAGE]);
      queryClient.setQueryData(["copilot-messages", "global"], []);
      toast.success("Đã xóa toàn bộ lịch sử trò chuyện Copilot");
    },
    onError: () => {
      toast.error("Không thể xóa lịch sử chat");
    },
  });

  // Mutation to send message
  const sendMutation = useMutation({
    mutationFn: async (userQuery: string) => {
      return askCopilot({ query: userQuery });
    },
    onSuccess: (data, userQuery) => {
      const assistantMsg: CopilotMessageItem = {
        id: data.id || `ai-${Date.now()}`,
        role: "assistant",
        content: data.response,
        tools_used: data.tools_used,
        sources: data.sources,
        intent: data.intent,
        conversation_id: null,
        created_at: new Date().toISOString(),
      };
      setLocalMessages((prev) => [...prev, assistantMsg]);
      queryClient.invalidateQueries({ queryKey: ["copilot-messages", "global"] });
    },
    onError: (err) => {
      console.error("Copilot error:", err);
      const errMsg: CopilotMessageItem = {
        id: `err-${Date.now()}`,
        role: "assistant",
        content: "Xin lỗi, đã xảy ra lỗi kết nối với máy chủ AI. Vui lòng thử lại sau.",
        created_at: new Date().toISOString(),
      };
      setLocalMessages((prev) => [...prev, errMsg]);
    },
  });

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    const query = input.trim();
    if (!query || sendMutation.isPending) return;

    setInput("");
    const userMsg: CopilotMessageItem = {
      id: `user-${Date.now()}`,
      role: "user",
      content: query,
      created_at: new Date().toISOString(),
    };

    setLocalMessages((prev) => [...prev, userMsg]);
    sendMutation.mutate(query);
  };

  const handleClearHistory = () => {
    if (confirm("Bạn có chắc chắn muốn xóa toàn bộ lịch sử trò chuyện với Copilot?")) {
      clearMutation.mutate();
    }
  };

  if (!settingsLoading && !features.copilot) {
    return (
      <main className="flex h-full w-full flex-col bg-slate-50 items-center justify-center">
        <div className="flex flex-col items-center gap-4 p-8 text-center bg-white border border-gray-200 rounded-2xl max-w-md shadow-sm">
          <Lock className="text-slate-400" size={48} />
          <h1 className="text-xl font-bold text-slate-800">Copilot Đã Bị Tắt</h1>
          <p className="text-sm text-slate-500">
            Tính năng AI Copilot hiện đang tắt trong cài đặt AI Hub. Bạn hãy bật lại để sử dụng.
          </p>
          <button
            onClick={() => router.push("/ai-hub")}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-xl text-sm font-semibold hover:bg-blue-700 transition-colors"
          >
            Đến Cài Đặt AI Hub
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className="flex h-full w-full flex-col bg-slate-50">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-200 bg-white px-6 py-4">
        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
            <Sparkles size={20} />
          </div>
          <div>
            <h1 className="text-lg font-bold text-slate-800">Copilot Chat</h1>
            <p className="text-xs text-slate-400">Trợ lý tìm kiếm tri thức & đối tác thông minh</p>
          </div>
        </div>

        {localMessages.length > 1 && (
          <Button
            size="sm"
            variant="ghost"
            onClick={handleClearHistory}
            disabled={clearMutation.isPending}
            className="text-xs font-semibold text-slate-500 hover:text-red-600 hover:bg-red-50 rounded-xl cursor-pointer"
            title="Xóa lịch sử trò chuyện"
          >
            <Trash2 size={14} className="mr-1.5" />
            Xóa lịch sử chat
          </Button>
        )}
      </div>

      {/* Message List */}
      <div className="flex-1 overflow-y-auto p-4 md:p-6">
        <div className="mx-auto flex max-w-3xl flex-col gap-5">
          {historyLoading ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-16 w-3/4 rounded-2xl bg-white border border-slate-100 animate-pulse" />
              ))}
            </div>
          ) : (
            localMessages.map((msg, i) => (
              <div
                key={msg.id || i}
                className={cn(
                  "flex w-full gap-3 md:gap-4",
                  msg.role === "user" ? "justify-end" : "justify-start"
                )}
              >
                {msg.role === "assistant" && (
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-100 text-blue-600">
                    <Bot size={18} />
                  </div>
                )}

                <div
                  className={cn(
                    "flex max-w-[85%] flex-col gap-1",
                    msg.role === "user" ? "items-end" : "items-start"
                  )}
                >
                  <div
                    className={cn(
                      "rounded-2xl px-4 py-3 text-sm leading-relaxed",
                      msg.role === "user"
                        ? "bg-blue-600 text-white rounded-tr-sm shadow-xs"
                        : "bg-white border border-slate-200/80 text-slate-800 rounded-tl-sm w-full shadow-xs"
                    )}
                  >
                    {renderCopilotMessageWithCards(msg.content)}
                  </div>

                  {msg.tools_used && msg.tools_used.length > 0 && (
                    <div className="flex items-center gap-1.5 mt-1 rounded-full bg-slate-100 px-2.5 py-0.5 text-[10px] font-medium text-slate-500">
                      <Wrench size={10} />
                      <span>Công cụ: {msg.tools_used.join(", ")}</span>
                    </div>
                  )}
                </div>

                {msg.role === "user" && (
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-white border border-slate-200 text-slate-700 shadow-xs">
                    <User size={16} />
                  </div>
                )}
              </div>
            ))
          )}

          {sendMutation.isPending && (
            <div className="flex w-full gap-3 md:gap-4 justify-start">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-100 text-blue-600">
                <Bot size={18} />
              </div>
              <div className="flex items-center gap-2 rounded-2xl rounded-tl-sm border border-slate-200 bg-white px-4 py-3 text-sm text-slate-500 shadow-xs">
                <div className="h-2 w-2 animate-bounce rounded-full bg-blue-600 [animation-delay:-0.3s]"></div>
                <div className="h-2 w-2 animate-bounce rounded-full bg-blue-600 [animation-delay:-0.15s]"></div>
                <div className="h-2 w-2 animate-bounce rounded-full bg-blue-600"></div>
                <span className="ml-1 text-xs font-medium">Copilot đang phân tích và tìm kiếm...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Bar */}
      <div className="border-t border-gray-200 bg-white p-4">
        <form onSubmit={handleSend} className="mx-auto flex max-w-3xl gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Tìm kiếm bạn bè, chủ đề quan tâm, kỹ năng hoặc người làm về AI, Robot..."
            className="flex-1 rounded-xl border border-gray-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-800 placeholder:text-slate-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 transition-all"
          />
          <button
            type="submit"
            disabled={!input.trim() || sendMutation.isPending}
            className="flex items-center justify-center rounded-xl bg-blue-600 px-4 py-2.5 text-white hover:bg-blue-700 disabled:bg-blue-300 disabled:cursor-not-allowed transition-colors shadow-xs cursor-pointer"
          >
            <Send size={18} />
          </button>
        </form>
      </div>
    </main>
  );
}
