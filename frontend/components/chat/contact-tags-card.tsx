"use client";

import { useState } from "react";
import { Tag, RefreshCw, Plus, X, Sparkles, Check } from "lucide-react";
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

  const { data: context, isLoading } = useQuery({
    queryKey: ["context", activeId],
    queryFn: () => getConversationContext(activeId!),
    enabled: !!activeId,
  });

  const { data: systemTags } = useQuery({
    queryKey: ["systemTags"],
    queryFn: () => import("@/lib/api/tags").then(m => m.getSystemTags()),
  });

  const tags = context?.tags || [];
  const pendingTags = context?.pending_tags || [];

  // Mutation to refresh tags using AI Agent
  const refreshMutation = useMutation({
    mutationFn: () => refreshConversationTags(activeId!),
    onSuccess: (data: any) => {
      queryClient.setQueryData(["context", activeId], (old: any) => ({
        ...old,
        pending_tags: data.pending_tags || data.tags, // Fallback if API hasn't updated
      }));
    },
  });

  // Mutation to update tags manually
  const updateMutation = useMutation({
    mutationFn: (newTags: string[]) => updateConversationTags(activeId!, newTags),
    onSuccess: (data) => {
      queryClient.setQueryData(["context", activeId], (old: any) => ({
        ...old,
        tags: data.tags,
      }));
    },
  });

  const approveMutation = useMutation({
    mutationFn: (tag: string) => approveConversationTag(activeId!, tag),
    onSuccess: (data) => {
      queryClient.setQueryData(["context", activeId], (old: any) => ({
        ...old,
        tags: data.tags,
        pending_tags: data.pending_tags,
      }));
    },
  });

  const rejectMutation = useMutation({
    mutationFn: (tag: string) => rejectConversationTag(activeId!, tag),
    onSuccess: (data) => {
      queryClient.setQueryData(["context", activeId], (old: any) => ({
        ...old,
        tags: data.tags,
        pending_tags: data.pending_tags,
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
    <div className="rounded-2xl border border-subtle bg-card p-4 space-y-3 shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <Tag size={14} className="text-accent" />
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
          disabled={refreshMutation.isPending || updateMutation.isPending}
          className="text-[11px] font-medium text-muted-foreground hover:text-accent bg-transparent hover:bg-muted/50"
          title="Agent tự động quét lại đoạn chat và gắn tag"
        >
          <RefreshCw
            size={12}
            className={cn(
              "text-accent",
              refreshMutation.isPending && "animate-spin"
            )}
          />
          <span>{refreshMutation.isPending ? "Đang quét..." : "AI quét lại"}</span>
        </Button>
      </div>

      {/* Tags List */}
      <div className="flex flex-wrap items-center gap-1.5 min-h-[32px]">
        {isLoading ? (
          <div className="flex gap-1.5 py-1">
            <span className="h-6 w-16 animate-pulse rounded-lg bg-muted" />
            <span className="h-6 w-20 animate-pulse rounded-lg bg-muted" />
          </div>
        ) : (tags.length > 0 || pendingTags.length > 0) ? (
          <>
            {tags.map((tag, idx) => {
              // High-signal category visual styling
              const isRelationship = ["Bạn Bè", "Khách Hàng", "Đối Tác", "Đồng Nghiệp", "Mentor", "Nhà Đầu Tư", "Cố Vấn"].includes(tag);
              
              return (
                <Badge
                  key={idx}
                  variant={isRelationship ? "default" : "secondary"}
                  className="group pr-1"
                >
                  <span>{tag}</span>
                  <Button
                    variant="ghost"
                    size="icon-xs"
                    onClick={() => handleRemoveTag(tag)}
                    disabled={updateMutation.isPending}
                    className="ml-1 rounded-full text-muted-foreground hover:text-foreground"
                    title={`Xóa nhãn ${tag}`}
                  >
                    <X size={11} />
                  </Button>
                </Badge>
              );
            })}
            
            {pendingTags.map((tag, idx) => (
              <Badge
                key={`pending-${idx}`}
                variant="outline"
                className="group pr-1 border-dashed border-accent/60 text-accent bg-accent/5"
              >
                <Sparkles size={10} className="mr-1 text-accent/70" />
                <span>{tag}</span>
                <div className="ml-1 flex items-center gap-0.5">
                  <Button
                    variant="ghost"
                    size="icon-xs"
                    onClick={() => approveMutation.mutate(tag)}
                    disabled={approveMutation.isPending || rejectMutation.isPending}
                    className="h-4 w-4 rounded-full text-green-600 hover:text-green-700 hover:bg-green-100"
                    title={`Duyệt nhãn ${tag}`}
                  >
                    <Check size={10} />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon-xs"
                    onClick={() => rejectMutation.mutate(tag)}
                    disabled={approveMutation.isPending || rejectMutation.isPending}
                    className="h-4 w-4 rounded-full text-red-500 hover:text-red-600 hover:bg-red-100"
                    title={`Từ chối nhãn ${tag}`}
                  >
                    <X size={10} />
                  </Button>
                </div>
              </Badge>
            ))}
          </>
        ) : (
          <div className="w-full py-1 text-left">
            <p className="text-xs text-muted-foreground italic">
              Chưa có nhãn phân loại nào.
            </p>
          </div>
        )}

        {/* Add Tag Input or Button */}
        {isAdding ? (
          <div className="relative">
            <div className="inline-flex items-center gap-1 rounded-lg border border-accent bg-muted px-2 py-0.5 shadow-sm">
              <Input
                type="text"
                autoFocus
                value={newTagInput}
                onChange={(e) => setNewTagInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    const trimmed = newTagInput.trim();
                    const formatted = trimmed
                      .split(" ")
                      .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
                      .join(" ");
                    
                    if (systemTags?.some(t => t.name.toLowerCase() === formatted.toLowerCase())) {
                      setNewTagInput(formatted);
                      handleAddTag(formatted);
                    } else if (systemTags?.some(t => t.name.toLowerCase().includes(trimmed.toLowerCase()))) {
                       const match = systemTags.find(t => t.name.toLowerCase().includes(trimmed.toLowerCase()));
                       if (match) handleAddTag(match.name);
                    }
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
                   const formatted = newTagInput.trim()
                      .split(" ")
                      .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
                      .join(" ");
                   if (systemTags?.some(t => t.name.toLowerCase() === formatted.toLowerCase())) {
                      handleAddTag(formatted);
                   }
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
              <div className="absolute top-full left-0 mt-1 w-full max-h-32 overflow-y-auto rounded-md border border-subtle bg-muted shadow-md z-10 scrollbar-thin">
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
            className="border-dashed border-subtle text-muted-foreground hover:border-accent hover:text-accent bg-transparent"
          >
            <Plus size={12} />
            <span>Thêm nhãn</span>
          </Button>
        )}
      </div>

      <p className="text-[10px] text-muted-foreground/70 italic">
        Nhãn được AI tự động nhận diện theo mối quan hệ, ngành nghề & kỹ năng từ cuộc hội thoại.
      </p>
    </div>
  );
}
