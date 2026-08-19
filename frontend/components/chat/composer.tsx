"use client";

import { useState } from "react";
import { Paperclip, Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useSendMessage } from "@/hooks/use-send-message";
import { v4 as uuidv4 } from "uuid";
import { useEffect } from "react";
import { useUIStore } from "@/lib/stores/ui-store";

type ComposerProps = {
  conversationId: string;
};

export function Composer({ conversationId }: ComposerProps) {
  const [content, setContent] = useState("");
  const mutation = useSendMessage(conversationId);
  const setCopilotOpen = useUIStore((s) => s.setCopilotOpen);

  useEffect(() => {
    const handleInsert = (e: any) => {
      if (e.detail) {
        setContent((prev) => (prev ? `${prev} ${e.detail}` : e.detail));
      }
    };
    window.addEventListener("insert-composer", handleInsert);
    return () => window.removeEventListener("insert-composer", handleInsert);
  }, []);



  const handleSend = () => {
    const text = content.trim();
    if (!text) return;
    
    // Slash commands -> Copilot
    if (text.startsWith("/")) {
      setCopilotOpen(true);
      window.dispatchEvent(new CustomEvent("copilot-query", { detail: text }));
      setContent("");
      return;
    }
    
    mutation.mutate({
      content: text,
      clientMessageId: uuidv4(),
    });
    
    setContent("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex items-end gap-2 rounded-composer bg-input px-3 py-2">
      <button
        type="button"
        className="rounded-button p-2 text-secondary hover:text-primary"
        aria-label="Attach file"
      >
        <Paperclip size={18} />
      </button>
      <textarea
        id="composer-input"
        rows={1}
        value={content}
        onChange={(e) => setContent(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Reply or type '/' for AI commands..."
        aria-label="Message composer"
        className="scrollbar-thin max-h-32 min-h-[40px] flex-1 resize-none bg-transparent py-2 text-sm text-primary placeholder:text-secondary outline-none"
      />
      <Button size="sm" className="rounded-full px-3" onClick={handleSend} disabled={!content.trim() || mutation.isPending} aria-label="Send message">
        <Send size={16} />
      </Button>
    </div>
  );
}
