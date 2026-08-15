"use client";

import { useState } from "react";
import { Lightbulb } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useQuery } from "@tanstack/react-query";
import { useConversationStore } from "@/lib/stores/conversation-store";
import { getConversationContext } from "@/lib/api/context";

export function AIRecommendationCard() {
  const activeId = useConversationStore((s) => s.activeConversationId);
  const [dismissedText, setDismissedText] = useState<string | null>(null);

  const { data: context } = useQuery({
    queryKey: ["context", activeId],
    queryFn: () => getConversationContext(activeId!),
    enabled: !!activeId,
  });

  const followUp = context?.follow_up;
  
  // Reset dismissed state if follow_up changes
  if (followUp && dismissedText === followUp) {
    return (
      <div className="rounded-button border border-subtle bg-surface p-4 text-secondary text-sm text-center">
        No new recommendations.
      </div>
    );
  }

  if (!followUp) {
    return (
      <div className="rounded-button border border-subtle bg-surface p-4 text-secondary text-sm text-center">
        No recommendation yet. Chat more to get AI suggestions.
      </div>
    );
  }

  const handleSendReminder = () => {
    window.dispatchEvent(new CustomEvent("insert-composer", { detail: followUp }));
  };

  const handleDismiss = () => {
    setDismissedText(followUp);
  };

  return (
    <div className="rounded-button border border-subtle bg-ai-card p-4 text-black shadow-sm">
      <div className="mb-2 flex items-center gap-2">
        <Lightbulb size={16} className="text-orange-500" />
        <h4 className="text-sm font-semibold text-orange-950">AI Suggestion</h4>
      </div>
      <p className="text-sm leading-relaxed text-orange-900 mb-4">
        {followUp}
      </p>
      <div className="flex gap-2">
        <Button 
          variant="warning" 
          size="sm" 
          onClick={handleSendReminder}
          className="shadow-sm"
        >
          Send reminder
        </Button>
        <Button
          variant="secondary"
          size="sm"
          onClick={handleDismiss}
          className="bg-white/50 text-black hover:bg-white/80 shadow-sm border-transparent"
        >
          Dismiss
        </Button>
      </div>
    </div>
  );
}
