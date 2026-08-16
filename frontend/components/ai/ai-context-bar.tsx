"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  getConversationContext,
  updateConversationContext,
  refreshConversationContext,
  type AIContext,
} from "@/lib/api/context";
import { useConversationStore } from "@/lib/stores/conversation-store";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import {
  RefreshCw,
  ChevronUp,
  ChevronDown,
  Sparkles,
  UserCheck,
  Calendar,
  Hash,
  ArrowRightCircle,
  Edit3,
  Check,
  X,
} from "lucide-react";
import { cn } from "@/lib/utils";

// Hàm làm sạch triệt để các token rò rỉ như [PEER], {peer}, [USER] trên giao diện
function cleanContextDisplay(str?: string | null): string {
  if (!str) return "";
  return str
    .replace(/\[PEER\]|\{peer\}|\[peer\]|\bPEER\b/gi, "Đối tác")
    .replace(/\[USER\]|\{user\}|\[user\]|\bUSER\b/gi, "Bạn")
    .replace(/\s+/g, " ")
    .trim();
}

// Chuẩn hóa chủ đề quan tâm thành từ khóa ngắn gọn, trực quan (ví dụ: AI, LLM, Robot, Đá bóng)
function cleanInterestKeywordDisplay(item?: string | null): string {
  if (!item) return "";
  let cleaned = cleanContextDisplay(item).replace(/^#+/, "").trim();
  const words = cleaned.split(/\s+/);
  if (words.length > 4) {
    cleaned = words.slice(0, 3).join(" ");
  }
  return cleaned
    .split(" ")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}


export function AIContextBar() {
  const activeId = useConversationStore((s) => s.activeConversationId);
  const queryClient = useQueryClient();
  const [isEditing, setIsEditing] = useState(false);
  const [isExpanded, setIsExpanded] = useState(true);
  const [editState, setEditState] = useState<AIContext>({});

  const { data: context, isLoading } = useQuery({
    queryKey: ["context", activeId],
    queryFn: () => getConversationContext(activeId!),
    enabled: !!activeId,
  });

  const mutation = useMutation({
    mutationFn: (newContext: AIContext) => updateConversationContext(activeId!, newContext),
    onSuccess: (updated) => {
      queryClient.setQueryData(["context", activeId], updated);
      setIsEditing(false);
      toast.success("Đã cập nhật trí nhớ AI thành công");
    },
    onError: () => {
      toast.error("Không thể cập nhật trí nhớ AI");
    },
  });

  const refreshMutation = useMutation({
    mutationFn: () => refreshConversationContext(activeId!),
    onSuccess: (updatedContext) => {
      queryClient.setQueryData(["context", activeId], updatedContext);
      queryClient.invalidateQueries({ queryKey: ["context", activeId] });
      toast.success("AI đã tóm tắt lại ngữ cảnh thành công!", {
        description: "Toàn bộ thông tin đối phương và tiến trình trò chuyện đã được cập nhật.",
      });
    },
    onError: () => {
      toast.error("Không thể làm mới tóm tắt. Vui lòng thử lại sau.");
    },
  });

  // Sync edit state when context changes
  useEffect(() => {
    if (context && !isEditing) {
      setEditState(context);
    }
  }, [context, isEditing]);

  if (!activeId) return null;

  if (isLoading) {
    return (
      <section className="border-b border-subtle bg-surface/60 px-4 py-3">
        <div className="flex items-center gap-2 mb-2">
          <Skeleton className="h-4 w-4 rounded-full" />
          <Skeleton className="h-4 w-36 rounded" />
        </div>
        <Skeleton className="h-12 w-full rounded-xl mb-2" />
        <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-14 rounded-xl" />
          ))}
        </div>
      </section>
    );
  }

  const handleSave = () => {
    mutation.mutate(editState);
  };

  const handleCancel = () => {
    setEditState(context || {});
    setIsEditing(false);
  };

  const cleanedSummary = cleanContextDisplay(context?.summary);
  const cleanedLastMet = cleanContextDisplay(context?.last_met);
  const cleanedFollowUp = cleanContextDisplay(context?.follow_up);
  const cleanedInterests = (context?.interested_in || [])
    .map((i) => cleanInterestKeywordDisplay(i))
    .filter(Boolean)
    .slice(0, 6);


  return (
    <section className="border-b border-subtle bg-surface/80 backdrop-blur-sm px-4 py-2.5 transition-all">
      {/* Top bar header */}
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <div className="flex h-5 w-5 items-center justify-center rounded-md bg-accent/15 text-accent">
            <Sparkles size={12} />
          </div>
          <h2 className="text-xs font-bold uppercase tracking-wider text-secondary">
            AI Context · Trí nhớ về đối phương
          </h2>
        </div>

        <div className="flex items-center gap-1.5">
          {isEditing ? (
            <>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleCancel}
                disabled={mutation.isPending}
                className="h-7 text-xs px-2 text-secondary hover:text-primary"
              >
                <X size={13} className="mr-1" />
                Hủy
              </Button>
              <Button
                variant="primary"
                size="sm"
                onClick={handleSave}
                disabled={mutation.isPending}
                className="h-7 text-xs px-2.5 font-semibold"
              >
                <Check size={13} className="mr-1" />
                {mutation.isPending ? "Đang lưu..." : "Lưu"}
              </Button>
            </>
          ) : (
            <>
              {/* Refresh button with spinning animation */}
              <button
                type="button"
                onClick={() => refreshMutation.mutate()}
                disabled={refreshMutation.isPending}
                className={cn(
                  "flex items-center gap-1 rounded-lg border border-subtle px-2 py-1 text-[11px] font-medium text-secondary",
                  "hover:border-accent/40 hover:text-accent hover:bg-elevated transition-colors cursor-pointer disabled:opacity-50"
                )}
                title="AI phân tích lại toàn bộ tin nhắn trong DB để tóm tắt mới nhất"
              >
                <RefreshCw
                  size={12}
                  className={cn(
                    "text-accent",
                    refreshMutation.isPending && "animate-spin"
                  )}
                />
                <span>{refreshMutation.isPending ? "Đang tóm tắt..." : "Làm mới"}</span>
              </button>

              <button
                type="button"
                onClick={() => setIsEditing(true)}
                className="flex items-center gap-1 rounded-lg border border-subtle px-2 py-1 text-[11px] font-medium text-secondary hover:border-subtle hover:text-primary hover:bg-elevated transition-colors cursor-pointer"
                title="Chỉnh sửa nội dung AI Context"
              >
                <Edit3 size={11} />
                <span>Sửa</span>
              </button>
            </>
          )}
        </div>
      </div>

      {/* Expanded Content Body */}
      {isExpanded && (
        <div className="mt-2.5 space-y-2">
          {/* Main Summary Box */}
          <div className="rounded-xl border border-accent/20 bg-gradient-to-r from-accent/10 via-surface to-surface p-3 transition-all">
            <div className="flex items-center gap-1.5 mb-1 text-[11px] font-bold uppercase tracking-wider text-accent">
              <UserCheck size={13} />
              <span>Tóm tắt về đối phương:</span>
            </div>
            {isEditing ? (
              <textarea
                value={editState.summary || ""}
                onChange={(e) => setEditState({ ...editState, summary: e.target.value })}
                placeholder="Nhập tóm tắt về đối tác..."
                rows={2}
                className="w-full rounded-lg bg-elevated border border-subtle px-2.5 py-1.5 text-xs text-primary placeholder:text-secondary focus:outline-none focus:ring-1 focus:ring-accent resize-none scrollbar-thin"
              />
            ) : (
              <p className="text-xs text-primary leading-relaxed font-medium">
                {cleanedSummary || (
                  <span className="text-secondary italic">
                    Chưa có tóm tắt. Hãy bấm &ldquo;Làm mới&rdquo; để AI phân tích cuộc hội thoại.
                  </span>
                )}
              </p>
            )}
          </div>

          {/* 3 Detail Cards Grid */}
          <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
            {/* 1. Last Met / Context */}
            <div className="rounded-xl border border-blue-500/20 bg-blue-500/5 p-2.5 space-y-1">
              <div className="flex items-center gap-1.5 text-[11px] font-semibold text-blue-300">
                <Calendar size={12} className="text-blue-400" />
                <span>Lần gặp / Bối cảnh</span>
              </div>
              {isEditing ? (
                <input
                  value={editState.last_met || ""}
                  onChange={(e) => setEditState({ ...editState, last_met: e.target.value })}
                  placeholder="Bối cảnh quen biết..."
                  className="w-full rounded bg-elevated border border-subtle px-2 py-1 text-xs text-primary focus:outline-none focus:ring-1 focus:ring-accent"
                />
              ) : (
                <p className="text-xs text-blue-100/90 truncate font-medium">
                  {cleanedLastMet || <span className="text-secondary italic">Chưa xác định</span>}
                </p>
              )}
            </div>

            {/* 2. Interested In */}
            <div className="rounded-xl border border-purple-500/20 bg-purple-500/5 p-2.5 space-y-1">
              <div className="flex items-center gap-1.5 text-[11px] font-semibold text-purple-300">
                <Hash size={12} className="text-purple-400" />
                <span>Chủ đề quan tâm</span>
              </div>
              {isEditing ? (
                <input
                  value={editState.interested_in?.join(", ") || ""}
                  onChange={(e) =>
                    setEditState({
                      ...editState,
                      interested_in: e.target.value
                        .split(",")
                        .map((s) => s.trim())
                        .filter(Boolean),
                    })
                  }
                  placeholder="AI, Startup, Python..."
                  className="w-full rounded bg-elevated border border-subtle px-2 py-1 text-xs text-primary focus:outline-none focus:ring-1 focus:ring-accent"
                />
              ) : cleanedInterests.length > 0 ? (
                <div className="flex flex-wrap gap-1">
                  {cleanedInterests.map((item, idx) => (
                    <span
                      key={idx}
                      className="rounded-md bg-purple-500/15 border border-purple-500/30 px-1.5 py-0.5 text-[10px] text-purple-300 font-medium"
                    >
                      #{item}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-secondary italic">Chưa có thông tin</p>
              )}
            </div>

            {/* 3. Follow-up / Next Step */}
            <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-2.5 space-y-1">
              <div className="flex items-center gap-1.5 text-[11px] font-semibold text-emerald-300">
                <ArrowRightCircle size={12} className="text-emerald-400" />
                <span>Gợi ý việc tiếp theo</span>
              </div>
              {isEditing ? (
                <input
                  value={editState.follow_up || ""}
                  onChange={(e) => setEditState({ ...editState, follow_up: e.target.value })}
                  placeholder="Hành động tiếp theo..."
                  className="w-full rounded bg-elevated border border-subtle px-2 py-1 text-xs text-primary focus:outline-none focus:ring-1 focus:ring-accent"
                />
              ) : (
                <p className="text-xs text-emerald-100/90 truncate font-medium">
                  {cleanedFollowUp || <span className="text-secondary italic">Chưa có ghi chú</span>}
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Expand / Collapse toggle */}
      <div className="mt-1.5 flex justify-center">
        <button
          type="button"
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center gap-1 text-[10px] uppercase font-semibold tracking-wider text-secondary hover:text-primary transition-colors cursor-pointer py-0.5"
        >
          {isExpanded ? (
            <>
              Thu gọn <ChevronUp size={11} />
            </>
          ) : (
            <>
              Mở rộng ngữ cảnh <ChevronDown size={11} />
            </>
          )}
        </button>
      </div>
    </section>
  );
}
