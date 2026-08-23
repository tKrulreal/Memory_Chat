"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Send, Bot, User, Sparkles, Wrench, Lock } from "lucide-react";
import { cn } from "@/lib/utils";
import { renderCopilotMessageWithCards } from "@/components/ai/copilot-card";
import { useAISettings } from "@/hooks/use-ai-settings";

type Message = {
  role: "user" | "assistant";
  content: string;
  tools_used?: string[];
};

export default function CopilotPage() {
  const router = useRouter();

  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Xin chào! Mình là Copilot AI. Mình có thể giúp bạn tìm kiếm thông tin về bạn bè, đối tác cũ trong các đoạn chat (theo tóm tắt, tag, sở thích...) hoặc tìm kiếm người dùng mới trên hệ thống dựa theo hồ sơ kỹ năng. Bạn cần mình giúp gì?",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { features, isLoading: settingsLoading } = useAISettings();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  if (!settingsLoading && !features.copilot) {
    return (
      <main className="flex h-full w-full flex-col bg-slate-50 items-center justify-center">
        <div className="flex flex-col items-center gap-4 p-8 text-center bg-white border border-gray-200 rounded-2xl max-w-md shadow-sm">
          <Lock className="text-slate-400" size={48} />
          <h1 className="text-xl font-bold text-slate-800">Copilot Disabled</h1>
          <p className="text-sm text-slate-500">
            AI Copilot has been disabled in the AI Hub settings. Enable it to chat with Copilot.
          </p>
          <button onClick={() => router.push("/ai-hub")} className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-semibold hover:bg-blue-700 transition-colors">
            Go to AI Settings
          </button>
        </div>
      </main>
    );
  }

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setIsLoading(true);

    try {
      const res = await fetch("/api/proxy/api/v1/copilot", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: userMsg }),
      });

      if (!res.ok) throw new Error("API call failed");

      const data = await res.json();

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.response,
          tools_used: data.tools_used,
        },
      ]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Xin lỗi, đã xảy ra lỗi kết nối với máy chủ.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex h-full w-full flex-col bg-slate-50">
      <div className="flex items-center gap-2 border-b border-gray-200 bg-white px-6 py-4">
        <Sparkles className="text-blue-600" size={24} />
        <h1 className="text-xl font-semibold text-slate-800">Copilot Chat</h1>
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        <div className="mx-auto flex max-w-3xl flex-col gap-6">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={cn(
                "flex w-full gap-4",
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
                    "rounded-2xl px-4 py-3 text-sm",
                    msg.role === "user"
                      ? "bg-blue-600 text-white rounded-tr-sm"
                      : "bg-white border border-gray-200 text-slate-800 rounded-tl-sm w-full shadow-sm"
                  )}
                >
                  {renderCopilotMessageWithCards(msg.content)}
                </div>

                {msg.tools_used && msg.tools_used.length > 0 && (
                  <div className="flex items-center gap-1.5 mt-1 rounded-full bg-gray-100 px-2 py-1 text-[10px] font-medium text-slate-500">
                    <Wrench size={10} />
                    <span>Used tool: {msg.tools_used.join(", ")}</span>
                  </div>
                )}
              </div>

              {msg.role === "user" && (
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-white border border-gray-200 text-slate-800 shadow-sm">
                  <User size={18} />
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="flex w-full gap-4 justify-start">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-100 text-blue-600">
                <Bot size={18} />
              </div>
              <div className="flex items-center gap-2 rounded-2xl rounded-tl-sm border border-gray-200 bg-white px-4 py-3 text-sm text-slate-500">
                <div className="h-2 w-2 animate-bounce rounded-full bg-blue-600 [animation-delay:-0.3s]"></div>
                <div className="h-2 w-2 animate-bounce rounded-full bg-blue-600 [animation-delay:-0.15s]"></div>
                <div className="h-2 w-2 animate-bounce rounded-full bg-blue-600"></div>
                <span className="ml-1 text-xs">Copilot đang phân tích và tìm kiếm...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      <div className="border-t border-gray-200 bg-white p-4">
        <form onSubmit={handleSend} className="mx-auto flex max-w-3xl gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Tìm kiếm bạn bè, chủ đề quan tâm, kỹ năng hoặc người làm về AI, Robot..."
            className="flex-1 rounded-xl border border-gray-200 bg-gray-100 px-4 py-2.5 text-sm text-slate-800 placeholder:text-slate-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="flex items-center justify-center rounded-xl bg-blue-600 px-4 py-2.5 text-white hover:bg-blue-700 disabled:bg-blue-300 disabled:cursor-not-allowed transition-colors"
          >
            <Send size={18} />
          </button>
        </form>
      </div>
    </main>
  );
}
