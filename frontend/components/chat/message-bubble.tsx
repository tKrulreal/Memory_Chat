import { cn } from "@/lib/utils";

type MessageBubbleProps = {
  content: string;
  outgoing: boolean;
  time: string;
  status?: "pending" | "sent" | "error";
};

export function MessageBubble({ content, outgoing, time, status = "sent" }: MessageBubbleProps) {
  return (
    <div
      className={cn("flex flex-col", outgoing ? "items-end" : "items-start")}
    >
      <div
        className={cn(
          "max-w-[70%] px-4 py-2.5 text-sm",
          outgoing
            ? "rounded-bubble rounded-br-sm bg-accent text-black"
            : "rounded-bubble rounded-bl-sm bg-elevated text-primary",
          status === "pending" && "opacity-70",
          status === "error" && "border border-red-500",
        )}
      >
        {content}
      </div>
      <span className="mt-1 flex items-center gap-1 text-[11px] text-secondary">
        {time}
        {status === "pending" && <span>(sending...)</span>}
        {status === "error" && <span className="text-red-500">(failed)</span>}
      </span>
    </div>
  );
}
