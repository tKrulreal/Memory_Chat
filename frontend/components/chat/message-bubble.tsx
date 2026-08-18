import { cn } from "@/lib/utils";
import { Undo2 } from "lucide-react";

type MessageBubbleProps = {
  content: string;
  outgoing: boolean;
  time: string;
  status?: "pending" | "sent" | "error";
  deleted_at?: string | null;
  onRecall?: () => void;
  isRecalling?: boolean;
};

export function MessageBubble({ 
  content, 
  outgoing, 
  time, 
  status = "sent",
  deleted_at,
  onRecall,
  isRecalling
}: MessageBubbleProps) {
  if (deleted_at) {
    return (
      <div className={cn("flex flex-col", outgoing ? "items-end" : "items-start")}>
        <div
          className={cn(
            "max-w-[70%] px-4 py-2.5 text-sm italic text-secondary",
            outgoing
              ? "rounded-bubble rounded-br-sm bg-accent/30"
              : "rounded-bubble rounded-bl-sm bg-elevated/50"
          )}
        >
          Tin nhắn đã được thu hồi
        </div>
        <span className="mt-1 flex items-center gap-1 text-[11px] text-secondary">
          {time}
        </span>
      </div>
    );
  }

  const handleRecall = () => {
    if (isRecalling) return;
    if (window.confirm("Thu hồi tin nhắn?\n\nTin nhắn này sẽ được thu hồi khỏi cuộc trò chuyện.")) {
      onRecall?.();
    }
  };

  return (
    <div
      className={cn("group flex flex-col relative", outgoing ? "items-end" : "items-start")}
    >
      <div className={cn("flex items-center gap-2", outgoing ? "flex-row-reverse" : "flex-row")}>
        <div
          className={cn(
            "max-w-[70%] px-4 py-2.5 text-sm",
            outgoing
              ? "rounded-bubble rounded-br-sm bg-accent text-black"
              : "rounded-bubble rounded-bl-sm bg-elevated text-primary",
            status === "pending" && "opacity-70",
            status === "error" && "border border-red-500",
            isRecalling && "opacity-50"
          )}
        >
          {content}
        </div>
        
        {outgoing && status === "sent" && onRecall && (
          <button
            type="button"
            onClick={handleRecall}
            disabled={isRecalling}
            className="hidden group-hover:flex items-center justify-center p-1.5 text-secondary hover:text-red-500 hover:bg-elevated rounded-full transition-colors"
            title="Thu hồi"
          >
            <Undo2 size={16} />
          </button>
        )}
      </div>
      <span className="mt-1 flex items-center gap-1 text-[11px] text-secondary">
        {time}
        {status === "pending" && <span>(sending...)</span>}
        {status === "error" && <span className="text-red-500">(failed)</span>}
        {isRecalling && <span>(recalling...)</span>}
      </span>
    </div>
  );
}
