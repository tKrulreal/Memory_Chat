"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getConversationContext, updateConversationContext, refreshConversationContext, type AIContext } from "@/lib/api/context";
import { useConversationStore } from "@/lib/stores/conversation-store";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { RefreshCw, ChevronUp, ChevronDown } from "lucide-react";

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
      toast.success("Context updated successfully");
    },
    onError: () => {
      toast.error("Failed to update context");
    }
  });

  const refreshMutation = useMutation({
    mutationFn: () => refreshConversationContext(activeId!),
    onSuccess: () => {
      toast.success("AI is synthesizing context in the background...");
    },
    onError: () => {
      toast.error("Failed to trigger context refresh");
    }
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
      <section className="border-b border-subtle bg-elevated/50 px-4 py-3">
        <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-secondary">
          AI Context
        </h2>
        <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-14 rounded-button" />
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

  return (
    <section className="border-b border-subtle bg-elevated/50 px-4 py-3">
      <div className="mb-2 flex items-center justify-between">
        <h2 className="text-xs font-semibold uppercase tracking-wide text-secondary flex items-center gap-1.5">
          <span>AI Context · Thông tin tóm tắt về đối phương</span>
        </h2>
        <div className="flex gap-2">
          {isEditing ? (
            <>
              <Button variant="ghost" size="sm" onClick={handleCancel} disabled={mutation.isPending}>
                Cancel
              </Button>
              <Button variant="secondary" size="sm" onClick={handleSave} disabled={mutation.isPending}>
                {mutation.isPending ? "Saving..." : "Save"}
              </Button>
            </>
          ) : (
            <div className="flex items-center gap-1">
              <Button 
                variant="ghost" 
                size="sm" 
                className="h-8 w-8 p-0 text-secondary hover:text-primary" 
                onClick={() => refreshMutation.mutate()} 
                disabled={refreshMutation.isPending}
                title="Làm mới AI Context"
              >
                <RefreshCw size={14} className={refreshMutation.isPending ? "animate-spin" : ""} />
                <span className="sr-only">Làm mới AI Context</span>
              </Button>
              <Button variant="ghost" size="sm" onClick={() => setIsEditing(true)}>
                Chỉnh sửa
              </Button>
            </div>
          )}
        </div>
      </div>
      
      {isExpanded && (
        <>
          <div className="mb-2">
            <ContextCard
              label="Tóm tắt về đối phương"
              value={editState.summary}
              isEditing={isEditing}
              onChange={(val) => setEditState({ ...editState, summary: val })}
              placeholder="Chưa có thông tin tóm tắt về đối phương"
              isTextArea
            />
          </div>
          <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
            <ContextCard
              label="Lần gặp / Bối cảnh"
              value={editState.last_met}
              isEditing={isEditing}
              onChange={(val) => setEditState({ ...editState, last_met: val })}
              placeholder="Chưa có thông tin"
            />
            <ContextCard
              label="Chủ đề đối phương quan tâm"
              value={editState.interested_in?.join(", ")}
              isEditing={isEditing}
              onChange={(val) =>
                setEditState({
                  ...editState,
                  interested_in: val.split(",").map((s) => s.trim()).filter(Boolean),
                })
              }
              placeholder="Chưa có thông tin"
            />
            <ContextCard
              label="Việc cần làm tiếp theo"
              value={editState.follow_up}
              isEditing={isEditing}
              onChange={(val) => setEditState({ ...editState, follow_up: val })}
              placeholder="Chưa có ghi chú"
              isAccent
            />
          </div>
        </>
      )}


      <div className="mt-2 flex justify-center">
        <Button 
          variant="ghost" 
          size="sm" 
          className="h-5 text-[10px] uppercase tracking-wider text-secondary hover:text-primary hover:bg-transparent" 
          onClick={() => setIsExpanded(!isExpanded)}
        >
          {isExpanded ? (
            <>
              Thu gọn <ChevronUp size={12} className="ml-1" />
            </>
          ) : (
            <>
              Mở rộng <ChevronDown size={12} className="ml-1" />
            </>
          )}
        </Button>
      </div>
    </section>
  );
}

function ContextCard({
  label,
  value,
  isEditing,
  onChange,
  isAccent,
  isTextArea,
  placeholder,
}: {
  label: string;
  value?: string;
  isEditing: boolean;
  onChange: (val: string) => void;
  isAccent?: boolean;
  isTextArea?: boolean;
  placeholder?: string;
}) {
  const defaultPlaceholder = placeholder || "Chưa có thông tin";

  return (
    <div className="rounded-button border border-subtle bg-surface px-3 py-2">
      <p className="mb-1 text-[11px] uppercase tracking-wide text-secondary">{label}</p>
      {isEditing ? (
        isTextArea ? (
          <textarea
            value={value || ""}
            onChange={(e) => onChange(e.target.value)}
            placeholder={defaultPlaceholder}
            rows={2}
            className="w-full bg-input px-2 py-1 text-sm outline-none ring-accent focus:ring-1 resize-none scrollbar-thin"
          />
        ) : (
          <input
            value={value || ""}
            onChange={(e) => onChange(e.target.value)}
            placeholder={defaultPlaceholder}
            className="w-full bg-input px-2 py-1 text-sm outline-none ring-accent focus:ring-1"
          />
        )
      ) : (
        <p
          className={`text-sm font-medium ${
            !value ? "text-secondary italic" : isAccent ? "text-accent" : ""
          }`}
        >
          {value || defaultPlaceholder}
        </p>
      )}
    </div>
  );
}

