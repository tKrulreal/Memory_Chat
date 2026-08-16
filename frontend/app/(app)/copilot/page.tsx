"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Send, Bot, User, Sparkles, Wrench } from "lucide-react";
import { cn } from "@/lib/utils";
import { useConversationStore } from "@/lib/stores/conversation-store";

type Message = {
  role: "user" | "assistant";
  content: string;
  tools_used?: string[];
};

export default function CopilotPage() {
  const router = useRouter();
  const setActive = useConversationStore((s) => s.setActiveConversation);

  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Xin chào! Mình là Copilot AI. Mình có thể giúp bạn tìm kiếm thông tin về người dùng, lịch sử chat, hoặc giải đáp các thắc mắc khác. Bạn cần mình giúp gì?",
    }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg = input.trim();
    setInput("");
    setMessages(prev => [...prev, { role: "user", content: userMsg }]);
    setIsLoading(true);

    try {
      const res = await fetch("/api/proxy/api/v1/copilot", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userMsg }),
      });

      if (!res.ok) throw new Error("API call failed");

      const data = await res.json();
      
      setMessages(prev => [...prev, {
        role: "assistant",
        content: data.response,
        tools_used: data.tools_used
      }]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, {
        role: "assistant",
        content: "Xin lỗi, đã xảy ra lỗi kết nối với máy chủ."
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const renderMessageContent = (content: string) => {
    // Split by <card...>...</card>
    const parts = content.split(/(<card[^>]*>.*?<\/card>)/s);
    return parts.map((part, idx) => {
      if (part.startsWith("<card")) {
        const nameMatch = part.match(/name="([^"]+)"/);
        const emailMatch = part.match(/email="([^"]+)"/);
        const idMatch = part.match(/conversation_id="([^"]+)"/);
        const name = nameMatch ? nameMatch[1] : "Contact";
        const email = emailMatch ? emailMatch[1] : "";
        const id = idMatch ? idMatch[1] : "";
        const desc = part.replace(/<[^>]*>/g, "").trim();
        
        if (!id) return null;
        
        return (
          <button
            key={idx}
            type="button"
            onClick={() => {
              setActive(id);
              router.push("/chats");
            }}
            className="mt-3 mb-3 flex items-center gap-3 p-3 border border-subtle rounded-xl hover:bg-elevated transition-colors bg-app w-full cursor-pointer group text-left"
          >
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-accent text-white font-semibold shadow-sm">
              {name.substring(0, 2).toUpperCase()}
            </div>
            <div className="flex flex-col flex-1 min-w-0">
              <span className="font-semibold text-primary truncate group-hover:text-accent transition-colors">{name}</span>
              {email && <span className="text-xs font-medium text-accent truncate">{email}</span>}
              <span className="text-xs text-secondary line-clamp-2 mt-0.5">{desc}</span>
            </div>
          </button>
        );
      }
      return part.trim() ? <div key={idx} className="whitespace-pre-wrap mb-2 last:mb-0">{part}</div> : null;
    });
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
              
              <div className={cn(
                "flex max-w-[80%] flex-col gap-1",
                msg.role === "user" ? "items-end" : "items-start"
              )}>
                <div className={cn(
                  "rounded-2xl px-4 py-3 text-sm",
                  msg.role === "user" 
                    ? "bg-accent text-white rounded-tr-sm" 
                    : "bg-surface border border-subtle text-primary rounded-tl-sm w-full"
                )}>
                  {renderMessageContent(msg.content)}
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
              <div className="flex items-center rounded-2xl bg-surface border border-subtle px-4 py-3 rounded-tl-sm">
                <div className="flex gap-1">
                  <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-secondary"></span>
                  <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-secondary" style={{ animationDelay: "0.2s" }}></span>
                  <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-secondary" style={{ animationDelay: "0.4s" }}></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      <div className="border-t border-subtle bg-surface p-4">
        <form onSubmit={handleSubmit} className="mx-auto flex max-w-3xl items-end gap-2 relative">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
            placeholder="Ask Copilot anything..."
            className="w-full resize-none rounded-xl border border-subtle bg-elevated py-3 pl-4 pr-12 text-sm text-primary placeholder-secondary focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
            rows={1}
            style={{ minHeight: "44px", maxHeight: "120px" }}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="absolute right-2 bottom-2 rounded-lg p-1.5 text-white bg-accent transition-colors disabled:bg-surface disabled:text-subtle"
          >
            <Send size={18} />
          </button>
        </form>
      </div>
    </main>
  );
}
