"use client";

import { MessageSquare, Sparkles, RefreshCw, Send, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useConversationStore } from "@/lib/stores/conversation-store";
import { getSuggestedReply, refreshSuggestedReply } from "@/lib/api/context";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

export function AIRecommendationCard() {
  const activeId = useConversationStore((s) => s.activeConversationId);
  const queryClient = useQueryClient();

  const {
    data: replyData,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["suggested-reply", activeId],
    queryFn: () => getSuggestedReply(activeId!),
    enabled: !!activeId,
  });

  const refreshMutation = useMutation({
    mutationFn: () => refreshSuggestedReply(activeId!),
    onSuccess: (data) => {
      queryClient.setQueryData(["suggested-reply", activeId], data);
      toast.success("Đã làm mới gợi ý trả lời từ AI!");
    },
    onError: () => {
      toast.error("Không thể làm mới gợi ý trả lời.");
    },
  });

  if (!activeId) return null;

  const handleUseReply = () => {
    if (!replyData?.suggested_reply) return;
    window.dispatchEvent(
      new CustomEvent("insert-composer", { detail: replyData.suggested_reply })
    );
    const composerInput = document.getElementById("composer-input");
    if (composerInput) {
      composerInput.focus();
    }
    toast.info("Đã chèn câu trả lời vào khung soạn tin!");
  };

  return (
    <div className="rounded-2xl border border-accent/25 bg-gradient-to-b from-accent/10 to-surface p-4 space-y-3 shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <Sparkles size={14} className="text-accent" />
          <h4 className="text-xs font-bold uppercase tracking-wider text-accent">
            AI Gợi ý trả lời (Smart Reply)
          </h4>
        </div>

        {/* Refresh Button */}
        <button
          type="button"
          onClick={() => refreshMutation.mutate()}
          disabled={refreshMutation.isPending || isLoading}
          className="flex items-center gap-1 rounded-lg px-2 py-1 text-[11px] font-medium text-secondary hover:text-accent hover:bg-elevated transition-colors cursor-pointer disabled:opacity-50"
          title="Tạo lại câu trả lời gợi ý mới cho tin nhắn này"
        >
          <RefreshCw
            size={12}
            className={cn(
              "text-accent",
              refreshMutation.isPending && "animate-spin"
            )}
          />
          <span>{refreshMutation.isPending ? "Đang tạo..." : "Làm mới"}</span>
        </button>
      </div>

      {isLoading ? (
        <div className="space-y-2 py-1">
          <div className="h-8 animate-pulse rounded-xl bg-elevated/70" />
          <div className="h-12 animate-pulse rounded-xl bg-elevated/70" />
        </div>
      ) : isError || !replyData ? (
        <div className="py-2 text-left text-xs text-secondary italic">
          Chưa có gợi ý trả lời nào cho cuộc trò chuyện này.
        </div>
      ) : (
        <>
          {/* Peer's Latest Message Box */}
          {replyData.peer_last_message && (
            <div className="rounded-xl bg-elevated/80 border border-subtle p-2.5 text-xs">
              <p className="text-[10px] font-semibold uppercase tracking-wider text-secondary flex items-center gap-1 mb-1">
                <MessageSquare size={11} className="text-blue-400" />
                Tin nhắn gần nhất từ {replyData.peer_name}:
              </p>
              <p className="text-primary text-xs italic line-clamp-2">
                &ldquo;{replyData.peer_last_message}&rdquo;
              </p>
            </div>
          )}

          {/* AI Suggested Response Box */}
          <div className="rounded-xl bg-surface border border-accent/20 p-3 space-y-1.5 shadow-inner">
            <p className="text-[10px] font-bold uppercase tracking-wider text-accent flex items-center gap-1">
              <ArrowRight size={11} />
              Gợi ý phản hồi từ AI:
            </p>
            <p className="text-xs text-primary leading-relaxed font-medium">
              {replyData.suggested_reply}
            </p>
          </div>

          {/* Action Button: Insert to composer */}
          <Button
            variant="primary"
            size="sm"
            onClick={handleUseReply}
            className="w-full text-xs font-semibold shadow-sm shadow-accent/20"
          >
            <Send size={12} className="mr-1.5" />
            Dùng câu trả lời này & Soạn tin
          </Button>
        </>
      )}
    </div>
  );
}
