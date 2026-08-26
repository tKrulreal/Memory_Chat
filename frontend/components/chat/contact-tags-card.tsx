"use client";

import { useState } from "react";
import { Tag, RefreshCw, Plus, X, Sparkles, Check, CheckCheck } from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useConversationStore } from "@/lib/stores/conversation-store";
import {
  getConversationContext,
  refreshConversationTags,
  updateConversationTags,
  approveConversationTag,
  rejectConversationTag
} from "@/lib/api/context";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";

export function ContactTagsCard() {
  const activeId = useConversationStore((s) => s.activeConversationId);
  const queryClient = useQueryClient();
  const [isAdding, setIsAdding] = useState(false);
  const [newTagInput, setNewTagInput] = useState("");

  const [scanFeedback, setScanFeedback] = useState<string | null>(null);

  const { data: context, isLoading } = useQuery({
    queryKey: ["context", activeId],
    queryFn: () => getConversationContext(activeId!),
    enabled: !!activeId,
  });

  const { data: systemTags = [] } = useQuery({
    queryKey: ["system-tags"],
    queryFn: () => import("@/lib/api/tags").then(m => m.getSystemTags()),
  });

  const tags = context?.tags || [];
  // Filter out any pending tags that are already in active tags
  const rawPendingTags = context?.pending_tags || [];
  const pendingTags = rawPendingTags.filter((t) => !tags.includes(t));

  // Mutation to refresh tags using AI Agent
  const refreshMutation = useMutation({
    mutationFn: () => refreshConversationTags(activeId!),
    onSuccess: (data: any) => {
      const newPending = (data.pending_tags || []).filter((t: string) => !tags.includes(t));
      queryClient.setQueryData(["context", activeId], (old: any) => ({
        ...old,
        tags: data.tags !== undefined ? data.tags : (old?.tags || []),
        pending_tags: data.pending_tags || [],
      }));
      queryClient.invalidateQueries({ queryKey: ["context", activeId] });

      if (newPending.length > 0) {
        setScanFeedback(`Đã tìm thấy ${newPending.length} nhãn gợi ý mới!`);
      } else if (systemTags.length === 0) {
        setScanFeedback("Chưa có nhãn nào trong AI Hub. Hãy thêm nhãn trong AI Hub trước.");
      } else {
        setScanFeedback("Đã quét xong: Chưa có thêm nhãn nào phù hợp từ AI Hub.");
      }
      setTimeout(() => setScanFeedback(null), 5000);
    },
    onError: () => {
      setScanFeedback("Lỗi khi kết nối Agent. Vui lòng thử lại.");
      setTimeout(() => setScanFeedback(null), 5000);
    },
  });

  // Mutation to update tags manually
  const updateMutation = useMutation({
    mutationFn: (newTags: string[]) => updateConversationTags(activeId!, newTags),
    onSuccess: (data) => {
      queryClient.setQueryData(["context", activeId], (old: any) => ({
        ...old,
        tags: data.tags,
        pending_tags: data.pending_tags || [],
      }));
      queryClient.invalidateQueries({ queryKey: ["system-tags"] });
    },
  });

  const approveMutation = useMutation({
    mutationFn: (tag: string) => approveConversationTag(activeId!, tag),
    onSuccess: (data) => {
      queryClient.setQueryData(["context", activeId], (old: any) => ({
        ...old,
        tags: data.tags,
        pending_tags: data.pending_tags || [],
      }));
      queryClient.invalidateQueries({ queryKey: ["system-tags"] });
    },
  });

  const approveAllMutation = useMutation({
    mutationFn: async () => {
      const merged = Array.from(new Set([...tags, ...pendingTags]));
      return updateConversationTags(activeId!, merged);
    },
    onSuccess: (data) => {
      queryClient.setQueryData(["context", activeId], (old: any) => ({
        ...old,
        tags: data.tags,
        pending_tags: [],
      }));
      queryClient.invalidateQueries({ queryKey: ["system-tags"] });
    },
  });

  const rejectMutation = useMutation({
    mutationFn: (tag: string) => rejectConversationTag(activeId!, tag),
    onSuccess: (data) => {
      queryClient.setQueryData(["context", activeId], (old: any) => ({
        ...old,
        tags: data.tags,
        pending_tags: data.pending_tags || [],
      }));
    },
  });

  const handleRemoveTag = (tagToRemove: string) => {
    const nextTags = tags.filter((t) => t !== tagToRemove);
    updateMutation.mutate(nextTags);
  };

  const handleAddTag = (tag?: string) => {
    const valToUse = tag !== undefined ? tag : newTagInput;
    const trimmed = valToUse.trim();
    if (!trimmed) {
      setIsAdding(false);
      return;
    }

    // Capitalize words
    const formatted = trimmed
      .split(" ")
      .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
      .join(" ");

    if (!tags.includes(formatted)) {
      const nextTags = [...tags, formatted];
      updateMutation.mutate(nextTags);
    }

    setNewTagInput("");
    setIsAdding(false);
  };

  if (!activeId) return null;

  return (
    <div className="rounded-2xl border border-subtle bg-card p-4 space-y-4 shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-subtle/60 pb-2.5">
        <div className="flex items-center gap-2">
          <div className="flex h-6 w-6 items-center justify-center rounded-md bg-blue-50 text-blue-600">
            <Tag size={13} />
          </div>
          <h4 className="text-xs font-bold uppercase tracking-wider text-foreground">
            Nhãn phân loại (Tags)
          </h4>
        </div>

        {/* Refresh Tag Button */}
        <Button
          type="button"
          variant="secondary"
          size="xs"
          onClick={() => refreshMutation.mutate()}
          disabled={refreshMutation.isPending || updateMutation.isPending || approveMutation.isPending}
          className="text-[11px] font-medium text-muted-foreground hover:text-accent bg-transparent hover:bg-muted/50 transition-colors"
          title="Agent tự động quét lại đoạn chat và gắn tag"
        >
          <RefreshCw
            size={12}
            className={cn(
              "text-accent mr-1",
              refreshMutation.isPending && "animate-spin"
            )}
          />
          <span>{refreshMutation.isPending ? "Đang quét..." : "AI quét lại"}</span>
        </Button>
      </div>

      {scanFeedback && (
        <div className="rounded-lg bg-blue-50/90 border border-blue-100 px-2.5 py-1.5 text-[11px] font-medium text-blue-800 flex items-center justify-between animate-in fade-in slide-in-from-top-1 duration-200">
          <span>{scanFeedback}</span>
          <button
            type="button"
            onClick={() => setScanFeedback(null)}
            className="text-blue-500 hover:text-blue-700 ml-2 cursor-pointer"
          >
            <X size={12} />
          </button>
        </div>
      )}

      {/* ============================================================ */}
      {/* PHẦN 1: NHÃN CỦA ĐỐI PHƯƠNG (Confirmed / Active Tags)        */}
      {/* ============================================================ */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            <span className="text-[11px] font-bold text-foreground">
              Nhãn của đối phương
            </span>
            {tags.length > 0 && (
              <span className="rounded-full bg-blue-100 px-1.5 py-0.2 text-[10px] font-bold text-blue-700">
                {tags.length}
              </span>
            )}
          </div>
          <span className="text-[10px] text-muted-foreground">Đã gắn</span>
        </div>

        <div className="flex flex-wrap items-center gap-1.5 min-h-[32px] p-2 rounded-xl bg-slate-50/70 border border-slate-100">
          {isLoading ? (
            <div className="flex gap-1.5 py-1">
              <span className="h-6 w-16 animate-pulse rounded-lg bg-muted" />
              <span className="h-6 w-20 animate-pulse rounded-lg bg-muted" />
            </div>
          ) : tags.length > 0 ? (
            tags.map((tag, idx) => {
              const isRelationship = ["Bạn Bè", "Khách Hàng", "Đối Tác", "Đồng Nghiệp", "Mentor", "Nhà Đầu Tư", "Cố Vấn"].includes(tag);
              return (
                <Badge
                  key={idx}
                  variant={isRelationship ? "default" : "secondary"}
                  className="group pr-1 pl-2.5 py-0.5 text-xs font-semibold shadow-xs"
                >
                  <span>{tag}</span>
                  <Button
                    variant="ghost"
                    size="icon-xs"
                    onClick={() => handleRemoveTag(tag)}
                    disabled={updateMutation.isPending}
                    className="ml-1 h-3.5 w-3.5 rounded-full text-muted-foreground hover:text-foreground hover:bg-black/10 transition-colors"
                    title={`Xóa nhãn ${tag}`}
                  >
                    <X size={10} />
                  </Button>
                </Badge>
              );
            })
          ) : (
            <p className="text-xs text-muted-foreground italic py-0.5">
              Chưa có nhãn nào được gắn cho đối phương.
            </p>
          )}

          {/* Add Tag Input or Button */}
          {isAdding ? (
            <div className="relative">
              <div className="inline-flex items-center gap-1 rounded-lg border border-accent bg-white px-2 py-0.5 shadow-sm">
                <Input
                  type="text"
                  autoFocus
                  value={newTagInput}
                  onChange={(e) => setNewTagInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      e.preventDefault();
                      const trimmed = newTagInput.trim();
                      if (!trimmed) return;
                      const formatted = trimmed
                        .split(" ")
                        .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
                        .join(" ");
                      handleAddTag(formatted);
                    } else if (e.key === "Escape") {
                      setIsAdding(false);
                      setNewTagInput("");
                    }
                  }}
                  placeholder="Nhập tên nhãn..."
                  className="w-28 bg-transparent text-xs text-foreground placeholder-secondary focus:outline-none"
                />
                <button
                  type="button"
                  onClick={() => {
                    const trimmed = newTagInput.trim();
                    if (!trimmed) return;
                    const formatted = trimmed
                      .split(" ")
                      .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
                      .join(" ");
                    handleAddTag(formatted);
                  }}
                  className="text-accent hover:text-foreground cursor-pointer"
                  title="Lưu nhãn"
                >
                  <Check size={13} />
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setIsAdding(false);
                    setNewTagInput("");
                  }}
                  className="text-muted-foreground hover:text-foreground cursor-pointer"
                  title="Hủy"
                >
                  <X size={13} />
                </button>
              </div>
              {newTagInput.trim().length > 0 && systemTags && (
                <div className="absolute top-full left-0 mt-1 w-full max-h-32 overflow-y-auto rounded-md border border-subtle bg-white shadow-md z-10 scrollbar-thin">
                  {systemTags
                    .filter(t => t.name.toLowerCase().includes(newTagInput.toLowerCase()) && !tags.includes(t.name))
                    .map(t => (
                      <button
                        key={t.id}
                        type="button"
                        className="w-full text-left px-2 py-1.5 text-xs text-foreground hover:bg-accent/10 transition-colors"
                        onClick={() => handleAddTag(t.name)}
                      >
                        {t.name}
                      </button>
                    ))}
                </div>
              )}
            </div>
          ) : (
            <Button
              type="button"
              variant="outline"
              size="xs"
              onClick={() => setIsAdding(true)}
              className="border-dashed border-subtle text-muted-foreground hover:border-accent hover:text-accent bg-transparent h-6 text-[11px]"
            >
              <Plus size={11} className="mr-0.5" />
              <span>Thêm</span>
            </Button>
          )}
        </div>
      </div>

      {/* ============================================================ */}
      {/* PHẦN 2: NHÃN AGENT GỢI Ý (AI Suggested / Pending Tags)       */}
      {/* ============================================================ */}
      <div className="space-y-2 pt-2 border-t border-subtle/60">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            <Sparkles size={12} className="text-amber-500" />
            <span className="text-[11px] font-bold text-foreground">
              Nhãn Agent gợi ý
            </span>
            {pendingTags.length > 0 && (
              <span className="rounded-full bg-amber-100 px-1.5 py-0.2 text-[10px] font-bold text-amber-800">
                {pendingTags.length}
              </span>
            )}
          </div>

          {pendingTags.length > 1 && (
            <Button
              type="button"
              variant="ghost"
              size="xs"
              onClick={() => approveAllMutation.mutate()}
              disabled={approveAllMutation.isPending}
              className="h-5 text-[10px] font-semibold text-blue-600 hover:text-blue-700 hover:bg-blue-50 p-1"
              title="Duyệt tất cả nhãn gợi ý"
            >
              <CheckCheck size={12} className="mr-1" />
              Duyệt tất cả
            </Button>
          )}
        </div>

        <div className="flex flex-wrap items-center gap-1.5 min-h-[32px] p-2 rounded-xl bg-amber-50/40 border border-dashed border-amber-200">
          {pendingTags.length > 0 ? (
            pendingTags.map((tag, idx) => (
              <Badge
                key={`pending-${idx}`}
                variant="outline"
                className="group pr-1 pl-2 py-0.5 text-xs border-amber-300 bg-white text-amber-900 shadow-xs hover:border-blue-400 hover:bg-blue-50/50 transition-all cursor-pointer"
                onClick={() => approveMutation.mutate(tag)}
                title={`Click để duyệt và chuyển '${tag}' lên nhãn đối phương`}
              >
                <Sparkles size={10} className="mr-1 text-amber-500" />
                <span className="font-semibold">{tag}</span>
                <div className="ml-1.5 flex items-center gap-0.5">
                  <Button
                    variant="ghost"
                    size="icon-xs"
                    onClick={(e) => {
                      e.stopPropagation();
                      approveMutation.mutate(tag);
                    }}
                    disabled={approveMutation.isPending || rejectMutation.isPending}
                    className="h-4 w-4 rounded-full bg-green-50 text-green-600 hover:text-green-700 hover:bg-green-100 border border-green-200"
                    title={`Tích chọn duyệt nhãn ${tag}`}
                  >
                    <Check size={10} />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon-xs"
                    onClick={(e) => {
                      e.stopPropagation();
                      rejectMutation.mutate(tag);
                    }}
                    disabled={approveMutation.isPending || rejectMutation.isPending}
                    className="h-4 w-4 rounded-full text-slate-400 hover:text-red-600 hover:bg-red-50"
                    title={`Từ chối nhãn ${tag}`}
                  >
                    <X size={10} />
                  </Button>
                </div>
              </Badge>
            ))
          ) : (
            <p className="text-xs text-muted-foreground italic py-0.5">
              Chưa có gợi ý mới (nhấn &ldquo;AI quét lại&rdquo; để Agent phân tích hội thoại).
            </p>
          )}
        </div>
      </div>

      <p className="text-[10px] text-muted-foreground/70 italic pt-1">
        Tích chọn nhãn Agent gợi ý để lưu trực tiếp vào nhãn đối phương.
      </p>
    </div>
  );
}
