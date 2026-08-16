"use client";

import { useEffect, useRef, useState } from "react";
import { X, Send, Copy, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useUIStore } from "@/lib/stores/ui-store";
import { useCopilotStore } from "@/lib/stores/copilot-store";
import { useConversationStore } from "@/lib/stores/conversation-store";
import { askCopilot } from "@/lib/api/copilot";
import { cn } from "@/lib/utils";
import { v4 as uuidv4 } from "uuid";

import { renderCopilotMessageWithCards } from "@/components/ai/copilot-card";

const COPILOT_ACTIONS = [
  "Summarize",
  "Find information",
  "Suggest reply",
  "Follow-up",
] as const;

export function CopilotDrawer() {
  const open = useUIStore((s) => s.copilotOpen);
  const toggleCopilot = useUIStore((s) => s.toggleCopilot);
  
  const { messages, isLoading, addMessage, setLoading, clearMessages } = useCopilotStore();
  const activeConversationId = useConversationStore((s) => s.activeConversationId);

  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  // Clear messages when conversation changes
  useEffect(() => {
    clearMessages();
  }, [activeConversationId, clearMessages]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const handleAsk = async (text: string) => {
    const query = text.trim();
    if (!query || isLoading) return;

    setInput("");
    
    // Add user message
    addMessage({
      id: uuidv4(),
      role: "user",
      content: query,
    });

    setLoading(true);

    try {
      const res = await askCopilot({
        query,
        context: activeConversationId ? { conversation_id: activeConversationId } : undefined,
      });

      addMessage({
        id: uuidv4(),
        role: "assistant",
        content: res.response,
        intent: res.intent,
      });
    } catch (err) {
      addMessage({
        id: uuidv4(),
        role: "assistant",
        content: "Sorry, I encountered an error while processing your request.",
        intent: "ERROR",
      });
    } finally {
      setLoading(false);
    }
  };

  // Listen for copilot-query events from slash commands
  useEffect(() => {
    const handler = (e: any) => {
      const query = e.detail;
      if (query) {
        handleAsk(query);
      }
    };
    window.addEventListener("copilot-query", handler);
    return () => window.removeEventListener("copilot-query", handler);
  }, [activeConversationId, isLoading]);

  const handleCopy = (text: string) => {
    window.dispatchEvent(new CustomEvent("insert-composer", { detail: text }));
  };

  return (
    <>
      {open && (
        <button
          type="button"
          className="fixed inset-0 z-40 bg-black/50"
          onClick={toggleCopilot}
          aria-label="Close copilot"
        />
      )}
      <aside
        aria-labelledby="copilot-title"
        className={cn(
          "fixed right-0 top-0 z-50 flex h-full w-full max-w-md flex-col border-l border-subtle bg-surface shadow-2xl transition-transform duration-200",
          open ? "translate-x-0" : "translate-x-full",
        )}
      >
        <header className="flex items-center justify-between border-b border-subtle px-4 py-4">
          <div>
            <h2 id="copilot-title" className="text-lg font-semibold">AI Copilot</h2>
            <p className="text-sm text-secondary">What can I help with?</p>
          </div>
          <button
            type="button"
            onClick={toggleCopilot}
            className="rounded-button p-2 text-secondary hover:bg-elevated hover:text-primary"
            aria-label="Close copilot drawer"
          >
            <X size={18} />
          </button>
        </header>

        <div className="flex flex-wrap gap-2 border-b border-subtle p-4">
          {COPILOT_ACTIONS.map((action) => (
            <Button 
              key={action} 
              variant="secondary" 
              size="sm"
              onClick={() => handleAsk(action)}
              disabled={isLoading}
            >
              {action}
            </Button>
          ))}
        </div>

        <div ref={scrollRef} className="scrollbar-thin flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="rounded-button bg-elevated p-4 text-sm text-secondary">
              Ask a question about this conversation. Copilot will use scoped
              context from your private assistant memory.
            </div>
          ) : (
            messages.map((msg) => (
              <div 
                key={msg.id} 
                className={cn(
                  "flex flex-col gap-1 max-w-[95%]", 
                  msg.role === "user" ? "ml-auto items-end" : "mr-auto items-start w-full"
                )}
              >
                <div 
                  className={cn(
                    "rounded-2xl px-4 py-2.5 text-sm",
                    msg.role === "user" 
                      ? "bg-accent text-accent-foreground rounded-tr-sm"
                      : "bg-elevated text-primary rounded-tl-sm w-full"
                  )}
                >
                  {renderCopilotMessageWithCards(msg.content)}
                </div>

                
                {msg.role === "assistant" && (msg.intent === "REPLY_SUGGEST" || msg.intent === "MEMORY") && (
                  <button
                    onClick={() => handleCopy(msg.content)}
                    className="flex items-center gap-1 text-xs text-secondary hover:text-accent mt-1"
                  >
                    <Copy size={12} />
                    <span>Copy to composer</span>
                  </button>
                )}
              </div>
            ))
          )}
          
          {isLoading && (
            <div className="flex items-center gap-2 text-sm text-secondary mr-auto">
              <Loader2 size={14} className="animate-spin" />
              Thinking...
            </div>
          )}
        </div>

        <footer className="border-t border-subtle p-4">
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Ask Copilot..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleAsk(input)}
              disabled={isLoading}
              className="h-10 flex-1 rounded-composer bg-input px-4 text-sm outline-none ring-accent focus:ring-1 disabled:opacity-50"
            />
            <Button size="md" onClick={() => handleAsk(input)} disabled={!input.trim() || isLoading} aria-label="Send to copilot">
              <Send size={16} />
            </Button>
          </div>
        </footer>
      </aside>
    </>
  );
}
