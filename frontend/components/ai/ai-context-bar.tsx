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
        <h2 className="text-xs font-semibold uppercase tracking-wide text-secondary">
          AI Context
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
                title="Refresh AI Context"
              >
                <RefreshCw size={14} className={refreshMutation.isPending ? "animate-spin" : ""} />
                <span className="sr-only">Refresh AI Context</span>
              </Button>
              <Button variant="ghost" size="sm" onClick={() => setIsEditing(true)}>
                Edit
              </Button>
            </div>
          )}
        </div>
      </div>
      
      {isExpanded && (
        <>
          <div className="mb-2">
            <ContextCard
              label="Summary"
              value={editState.summary}
              isEditing={isEditing}
              onChange={(val) => setEditState({ ...editState, summary: val })}
              isTextArea
            />
          </div>
          <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
            <ContextCard
              label="Last met"
              value={editState.last_met}
              isEditing={isEditing}
              onChange={(val) => setEditState({ ...editState, last_met: val })}
            />
            <ContextCard
              label="Interested in"
              value={editState.interested_in?.join(", ")}
              isEditing={isEditing}
              onChange={(val) =>
                setEditState({
                  ...editState,
                  interested_in: val.split(",").map((s) => s.trim()).filter(Boolean),
                })
              }
            />
            <ContextCard
              label="Follow-up"
              value={editState.follow_up}
              isEditing={isEditing}
              onChange={(val) => setEditState({ ...editState, follow_up: val })}
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
}: {
  label: string;
  value?: string;
  isEditing: boolean;
  onChange: (val: string) => void;
  isAccent?: boolean;
  isTextArea?: boolean;
}) {
  return (
    <div className="rounded-button border border-subtle bg-surface px-3 py-2">
      <p className="mb-1 text-[11px] uppercase tracking-wide text-secondary">{label}</p>
      {isEditing ? (
        isTextArea ? (
          <textarea
            value={value || ""}
            onChange={(e) => onChange(e.target.value)}
            placeholder="No summary yet"
            rows={2}
            className="w-full bg-input px-2 py-1 text-sm outline-none ring-accent focus:ring-1 resize-none scrollbar-thin"
          />
        ) : (
          <input
            value={value || ""}
            onChange={(e) => onChange(e.target.value)}
            placeholder="No summary yet"
            className="w-full bg-input px-2 py-1 text-sm outline-none ring-accent focus:ring-1"
          />
        )
      ) : (
        <p
          className={`text-sm font-medium ${
            !value ? "text-secondary italic" : isAccent ? "text-accent" : ""
          }`}
        >
          {value || "No summary yet"}
        </p>
      )}
    </div>
  );
}
