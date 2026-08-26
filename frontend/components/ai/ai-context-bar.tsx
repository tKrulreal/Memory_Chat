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
      <section className="mx-3 my-3 rounded-xl border border-subtle bg-card/60 p-3 shadow-sm">
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
    <section className="mx-3 mt-3 mb-4 rounded-2xl bg-white p-4 shadow-sm hover:shadow-md transition-shadow duration-200">
      {/* Top bar header */}
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <div className="flex h-5 w-5 items-center justify-center rounded-md bg-accent/15 text-accent">
            <Sparkles size={12} />
          </div>
          <h2 className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
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
                className="h-7 text-xs px-2 text-muted-foreground hover:text-foreground"
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
              <Button variant="ghost"
                type="button"
                onClick={() => refreshMutation.mutate()}
                disabled={refreshMutation.isPending}
                className={cn(
                  "flex items-center gap-1 rounded-lg border border-subtle px-2 py-1 text-[11px] font-medium text-muted-foreground",
                  "hover:border-accent/40 hover:text-accent hover:bg-muted transition-colors cursor-pointer disabled:opacity-50"
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
              </Button>

              <Button variant="ghost"
                type="button"
                onClick={() => setIsEditing(true)}
                className="flex items-center gap-1 rounded-lg border border-subtle px-2 py-1 text-[11px] font-medium text-muted-foreground hover:border-subtle hover:text-foreground hover:bg-muted transition-colors cursor-pointer"
                title="Chỉnh sửa nội dung AI Context"
              >
                <Edit3 size={11} />
                <span>Sửa</span>
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Expanded Content Body */}
      {isExpanded && (
        <div className="mt-2.5 space-y-2">
          {/* Main Summary Box */}
          <div className="rounded-xl bg-gray-50/50 p-3 transition-all">
            <div className="flex items-center gap-1.5 mb-1 text-sm font-semibold uppercase tracking-wider text-accent">
              <UserCheck size={14} />
              <span>Tóm tắt về đối phương:</span>
            </div>
            {isEditing ? (
              <textarea
                value={editState.summary || ""}
                onChange={(e) => setEditState({ ...editState, summary: e.target.value })}
                placeholder="Nhập tóm tắt về đối tác..."
                rows={2}
                className="w-full rounded-lg bg-muted border border-subtle px-2.5 py-1.5 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-accent resize-none scrollbar-thin"
              />
            ) : (
              <p className="text-sm text-foreground leading-relaxed font-medium">
                {cleanedSummary || (
                  <span className="text-muted-foreground italic">
                    Chưa có tóm tắt. Hãy bấm &ldquo;Làm mới&rdquo; để AI phân tích cuộc hội thoại.
                  </span>
                )}
              </p>
            )}
          </div>

          {/* 3 Detail Cards Grid */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            {/* 1. Last Met / Context */}
            <div className="rounded-xl bg-slate-50 p-3 space-y-1">
              <div className="flex items-center gap-1.5 text-sm font-semibold text-slate-900">
                <Calendar size={14} className="text-slate-700" />
                <span>Lần gặp / Bối cảnh</span>
              </div>
              {isEditing ? (
                <input
                  value={editState.last_met || ""}
                  onChange={(e) => setEditState({ ...editState, last_met: e.target.value })}
                  placeholder="Bối cảnh quen biết..."
                  className="w-full rounded bg-white border border-slate-200 px-2 py-1 text-xs text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
              ) : (
                <p className="text-sm text-slate-700 truncate font-medium">
                  {cleanedLastMet || <span className="text-slate-400 italic font-normal">Chưa xác định</span>}
                </p>
              )}
            </div>

            {/* 2. Interested In */}
            <div className="rounded-xl bg-slate-50 p-3 space-y-1">
              <div className="flex items-center gap-1.5 text-sm font-semibold text-slate-900">
                <Hash size={14} className="text-slate-700" />
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
                  className="w-full rounded bg-white border border-slate-200 px-2 py-1 text-xs text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
              ) : cleanedInterests.length > 0 ? (
                <div className="flex flex-wrap gap-1">
                  {cleanedInterests.map((item, idx) => (
                    <span
                      key={idx}
                      className="rounded-md bg-purple-50 border border-purple-200 px-1.5 py-0.5 text-xs text-purple-900 font-medium"
                    >
                      #{item}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-slate-400 italic">Chưa có thông tin</p>
              )}
            </div>

            {/* 3. Follow-up / Next Step */}
            <div className="rounded-xl bg-slate-50 p-3 space-y-1">
              <div className="flex items-center gap-1.5 text-sm font-semibold text-slate-900">
                <ArrowRightCircle size={14} className="text-slate-700" />
                <span>Gợi ý việc tiếp theo</span>
              </div>
              {isEditing ? (
                <input
                  value={editState.follow_up || ""}
                  onChange={(e) => setEditState({ ...editState, follow_up: e.target.value })}
                  placeholder="Hành động tiếp theo..."
                  className="w-full rounded bg-white border border-slate-200 px-2 py-1 text-xs text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
              ) : (
                <p className="text-sm text-slate-700 truncate font-medium">
                  {cleanedFollowUp || <span className="text-slate-400 italic font-normal">Chưa có ghi chú</span>}
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Expand / Collapse toggle */}
      <div className="mt-1.5 flex justify-center">
        <Button variant="ghost"
          type="button"
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center gap-1 text-xs uppercase font-medium tracking-wider text-blue-600 hover:text-blue-700 transition-colors cursor-pointer py-0.5"
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
        </Button>
      </div>
    </section>
  );
}
