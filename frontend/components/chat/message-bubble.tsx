"use client";

import { cn } from "@/lib/utils";
import { Undo2, RefreshCw, Check, CheckCheck, Clock, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

type MessageBubbleProps = {
  content: string;
  outgoing: boolean;
  time: string;
  status?: "pending" | "sent" | "read" | "error";
  deleted_at?: string | null;
  onRecall?: () => void;
  isRecalling?: boolean;
  onRetry?: () => void;
  isConsecutive?: boolean;
};

export function MessageBubble({ 
  content, 
  outgoing, 
  time, 
  status = "sent",
  deleted_at,
  onRecall,
  isRecalling,
  onRetry,
  isConsecutive = false
}: MessageBubbleProps) {
  if (deleted_at) {
    return (
      <div className={cn("flex flex-col w-full", outgoing ? "items-end" : "items-start", isConsecutive ? "mb-1" : "mb-6")}>
        <div
          className={cn(
            "max-w-[85%] md:max-w-[75%] w-fit px-5 py-3 text-sm italic text-slate-400 shadow-sm border border-slate-100",
            outgoing
              ? "rounded-3xl rounded-br-sm bg-slate-50/50"
              : "rounded-3xl rounded-bl-sm bg-slate-50/50"
          )}
        >
          Tin nhắn đã được thu hồi
        </div>
        <span className="mt-1 flex items-center gap-1 text-xs text-slate-400 font-medium">
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
    <div className={cn("group flex w-full", outgoing ? "justify-end" : "justify-start", isConsecutive ? "mb-1" : "mb-6")}>
      <div 
        className={cn(
          "relative max-w-[75%] px-5 py-3 w-fit rounded-3xl shadow-sm",
          outgoing 
            ? "bg-blue-600 text-white rounded-br-sm" 
            : "bg-white border border-slate-100 text-slate-800 rounded-bl-sm",
          status === "pending" && "opacity-70",
          status === "error" && "border-2 border-red-500 bg-red-50 text-red-600",
          isRecalling && "opacity-50"
        )}
      >
        <div className="flex flex-wrap items-end gap-x-2 gap-y-1">
          <span className={cn("text-[14px] whitespace-pre-wrap break-words leading-relaxed", outgoing ? "text-white" : "text-slate-800")}>{content}</span>
          <span className={cn("text-[10px] font-medium opacity-80 pt-1 whitespace-nowrap ml-1 inline-flex items-center gap-1", outgoing ? "text-blue-100" : "text-slate-400")}>
            {time}
            {outgoing && status === "pending" && (
              <span className="inline-flex items-center gap-0.5 ml-1">
                <Clock size={10} />
                <span>đang gửi</span>
              </span>
            )}
            {outgoing && status === "sent" && (
              <span className="inline-flex items-center gap-0.5 ml-1" title="Đã gửi">
                <Check size={11} />
                <span>Đã gửi</span>
              </span>
            )}
            {outgoing && status === "read" && (
              <span className="inline-flex items-center gap-0.5 ml-1 text-cyan-200 font-semibold" title="Đã xem">
                <CheckCheck size={12} className="text-cyan-200" />
                <span>Đã xem</span>
              </span>
            )}
            {outgoing && status === "error" && (
              <span className="inline-flex items-center gap-0.5 ml-1 text-red-200">
                <AlertCircle size={10} />
                <span>lỗi</span>
              </span>
            )}
            {isRecalling && <span className="ml-1">(đang thu hồi)</span>}
          </span>
        </div>
        
        {/* Absolute positioned action buttons to prevent layout shift */}
        <div className={cn("absolute hidden group-hover:flex items-center gap-1 top-1/2 -translate-y-1/2", outgoing ? "right-full mr-2" : "left-full ml-2")}>
          {outgoing && (status === "sent" || status === "read") && onRecall && (
            <Button variant="ghost"
              type="button"
              onClick={handleRecall}
              disabled={isRecalling}
              className="flex items-center justify-center p-2 text-slate-400 hover:text-red-500 hover:bg-slate-100 rounded-full transition-colors bg-white shadow-sm border border-slate-100"
              title="Thu hồi"
            >
              <Undo2 size={16} />
            </Button>
          )}
          
          {outgoing && status === "error" && onRetry && (
            <Button variant="ghost"
              type="button"
              onClick={onRetry}
              className="flex items-center justify-center p-2 text-red-500 hover:bg-slate-100 rounded-full transition-colors bg-white shadow-sm border border-slate-100"
              title="Thử lại"
            >
              <RefreshCw size={16} />
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
