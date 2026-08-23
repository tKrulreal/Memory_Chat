"use client";

import { useState, useEffect, useRef } from "react";
import { Paperclip, Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useSendMessage } from "@/hooks/use-send-message";
import { v4 as uuidv4 } from "uuid";
import { useUIStore } from "@/lib/stores/ui-store";
import { Textarea } from "@/components/ui/textarea";

type ComposerProps = {
  conversationId: string;
};

export function Composer({ conversationId }: ComposerProps) {
  const [content, setContent] = useState("");
  const mutation = useSendMessage(conversationId);
  const setCopilotOpen = useUIStore((s) => s.setCopilotOpen);
  const isSendingRef = useRef(false);

  useEffect(() => {
    const handleInsert = (e: any) => {
      if (e.detail) {
        setContent((prev) => (prev ? `${prev} ${e.detail}` : e.detail));
      }
    };
    window.addEventListener("insert-composer", handleInsert);
    return () => window.removeEventListener("insert-composer", handleInsert);
  }, []);

  // Reset isSendingRef when mutation finishes
  useEffect(() => {
    if (!mutation.isPending) {
      isSendingRef.current = false;
    }
  }, [mutation.isPending]);

  const handleSend = () => {
    const text = content.trim();
    if (!text || isSendingRef.current) return;
    
    // Slash commands -> Copilot
    if (text.startsWith("/")) {
      setCopilotOpen(true);
      window.dispatchEvent(new CustomEvent("copilot-query", { detail: text }));
      setContent("");
      return;
    }
    
    isSendingRef.current = true;
    mutation.mutate({
      content: text,
      clientMessageId: uuidv4(),
    });
    
    setContent("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Ngăn lỗi bộ gõ tiếng Việt (IME) chèn lại text khi nhấn Enter để kết thúc gõ dấu
    if (e.nativeEvent.isComposing) return;

    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (mutation.isPending || isSendingRef.current) return;
      handleSend();
    }
  };

  return (
    <div className="flex items-end gap-2 rounded-[24px] bg-white border border-gray-200 px-4 py-3 shadow-sm">
      <Button variant="ghost"
        type="button"
        className="rounded-button p-2 text-muted-foreground hover:text-foreground"
        aria-label="Attach file"
      >
        <Paperclip size={18} />
      </Button>
      <Textarea
        id="composer-input"
        rows={1}
        value={content}
        onChange={(e) => setContent(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Reply or type '/' for AI commands..."
        aria-label="Message composer"
        className="scrollbar-thin max-h-32 min-h-[40px] flex-1 resize-none bg-transparent py-2 text-sm text-foreground placeholder:text-muted-foreground outline-none"
      />
      <Button size="sm" className="rounded-full px-3" onClick={handleSend} disabled={!content.trim() || mutation.isPending} aria-label="Send message">
        <Send size={16} />
      </Button>
    </div>
  );
}
