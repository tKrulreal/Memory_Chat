"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Send, Bot, User, Sparkles, Wrench } from "lucide-react";
import { cn } from "@/lib/utils";
import { renderCopilotMessageWithCards } from "@/components/ai/copilot-card";

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

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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
    <main className="flex h-full w-full flex-col bg-app">
      <div className="flex items-center gap-2 border-b border-subtle bg-surface px-6 py-4">
        <Sparkles className="text-accent" size={24} />
        <h1 className="text-xl font-semibold text-primary">Copilot Chat</h1>
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
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-accent/20 text-accent">
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
                      ? "bg-accent text-white rounded-tr-sm"
                      : "bg-surface border border-subtle text-primary rounded-tl-sm w-full shadow-sm"
                  )}
                >
                  {renderCopilotMessageWithCards(msg.content)}
                </div>

                {msg.tools_used && msg.tools_used.length > 0 && (
                  <div className="flex items-center gap-1.5 mt-1 rounded-full bg-elevated px-2 py-1 text-[10px] font-medium text-secondary">
                    <Wrench size={10} />
                    <span>Used tool: {msg.tools_used.join(", ")}</span>
                  </div>
                )}
              </div>

              {msg.role === "user" && (
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-surface border border-subtle text-primary">
                  <User size={18} />
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="flex w-full gap-4 justify-start">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-accent/20 text-accent">
                <Bot size={18} />
              </div>
              <div className="flex items-center gap-2 rounded-2xl rounded-tl-sm border border-subtle bg-surface px-4 py-3 text-sm text-secondary">
                <div className="h-2 w-2 animate-bounce rounded-full bg-accent [animation-delay:-0.3s]"></div>
                <div className="h-2 w-2 animate-bounce rounded-full bg-accent [animation-delay:-0.15s]"></div>
                <div className="h-2 w-2 animate-bounce rounded-full bg-accent"></div>
                <span className="ml-1 text-xs">Copilot đang phân tích và tìm kiếm...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      <div className="border-t border-subtle bg-surface p-4">
        <form onSubmit={handleSend} className="mx-auto flex max-w-3xl gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Tìm kiếm bạn bè, chủ đề quan tâm, kỹ năng hoặc người làm về AI, Robot..."
            className="flex-1 rounded-xl border border-subtle bg-app px-4 py-2.5 text-sm text-primary placeholder-secondary focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="flex items-center justify-center rounded-xl bg-accent px-4 text-white hover:bg-accent/90 disabled:opacity-50 transition-colors"
          >
            <Send size={18} />
          </button>
        </form>
      </div>
    </main>
  );
}
