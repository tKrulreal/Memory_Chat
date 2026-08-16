"use client";

import { useState } from "react";
import {
  MessageSquare,
  X,
  Check,
  ChevronRight,
  Sparkles,
  Briefcase,
  MapPin,
  HelpCircle,
  Gift,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  ConnectionRecommendation,
  acceptConnection,
  rejectConnection,
  dismissConnection,
} from "@/lib/api/recommendations";
import { cn } from "@/lib/utils";
import { useRouter } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";
import { useConversationStore } from "@/lib/stores/conversation-store";

type Priority = "HIGH" | "MEDIUM" | "LOW";

interface ConnectionCardProps {
  recommendation: ConnectionRecommendation;
  isSelected?: boolean;
  onAccept?: (id: string) => void;
  onReject?: (id: string) => void;
  onDismiss?: (id: string) => void;
  onViewDetails?: (id: string) => void;
}

export function ConnectionCard({
  recommendation,
  isSelected = false,
  onAccept,
  onReject,
  onDismiss,
  onViewDetails,
}: ConnectionCardProps) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const setActiveConversation = useConversationStore((s) => s.setActiveConversation);
  const [isLoading, setIsLoading] = useState(false);
  const [action, setAction] = useState<"accept" | "reject" | null>(null);

  const priorityStyles: Record<Priority, string> = {
    HIGH: "bg-accent/15 border-accent/30 text-accent",
    MEDIUM: "bg-amber-500/15 border-amber-500/30 text-amber-400",
    LOW: "bg-elevated border-subtle text-secondary",
  };

  const handleAccept = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsLoading(true);
    setAction("accept");
    try {
      const res = await acceptConnection(recommendation.id);
      queryClient.invalidateQueries({ queryKey: ["conversations"] });
      queryClient.invalidateQueries({ queryKey: ["connection-recommendations"] });
      if (res?.conversation_id) {
        setActiveConversation(res.conversation_id);
      }
      onAccept?.(recommendation.id);
      router.push("/chats");
    } catch (error) {
      console.error("Failed to accept:", error);
    } finally {
      setIsLoading(false);
      setAction(null);
    }
  };

  const handleReject = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsLoading(true);
    setAction("reject");
    try {
      await rejectConnection(recommendation.id);
      queryClient.invalidateQueries({ queryKey: ["connection-recommendations"] });
      onReject?.(recommendation.id);
    } catch (error) {
      console.error("Failed to reject:", error);
    } finally {
      setIsLoading(false);
      setAction(null);
    }
  };

  const handleDismiss = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsLoading(true);
    try {
      await dismissConnection(recommendation.id);
      queryClient.invalidateQueries({ queryKey: ["connection-recommendations"] });
      onDismiss?.(recommendation.id);
    } catch (error) {
      console.error("Failed to dismiss:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const isProcessed = recommendation.status !== "PENDING";
  const targetName =
    recommendation.target_user_name ||
    recommendation.target_contact_name ||
    "Người dùng";
  const targetEmail = recommendation.target_user_email || "";
  const targetInitials =
    targetName
      .split(" ")
      .map((part) => part[0])
      .join("")
      .slice(0, 2)
      .toUpperCase() || "U";

  const matchPercent = Math.round((recommendation.confidence ?? 0.5) * 100);

  return (
    <div
      onClick={() => onViewDetails?.(recommendation.id)}
      className={cn(
        "group relative rounded-2xl border bg-surface p-5 transition-all cursor-pointer select-none",
        isSelected
          ? "border-accent bg-elevated/70 shadow-lg ring-1 ring-accent/40"
          : "border-subtle hover:border-accent/40 hover:bg-surface/80 hover:shadow-md",
        isProcessed && "opacity-65"
      )}
    >
      {/* Top Bar: Match Score Pill & Dismiss */}
      <div className="flex items-center justify-between gap-2 mb-3.5">
        <div className="flex items-center gap-2 flex-wrap">
          <span
            className={cn(
              "rounded-full border px-2.5 py-0.5 text-[11px] font-bold tracking-wide uppercase flex items-center gap-1",
              priorityStyles[recommendation.priority as Priority] ||
                priorityStyles.MEDIUM
            )}
          >
            <Sparkles size={11} />
            {matchPercent}% Match
          </span>
          <span className="text-[11px] font-medium text-secondary">
            {recommendation.priority === "HIGH"
              ? "Rất phù hợp"
              : recommendation.priority === "MEDIUM"
              ? "Tương thích tốt"
              : "Có tiềm năng"}
          </span>
        </div>

        {!isProcessed && (
          <button
            type="button"
            onClick={handleDismiss}
            disabled={isLoading}
            className="rounded-lg p-1 text-secondary/60 hover:bg-elevated hover:text-primary transition-colors cursor-pointer"
            title="Bỏ qua gợi ý này"
          >
            <X size={15} />
          </button>
        )}
      </div>

      {/* Main Candidate Card */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex items-center gap-3 min-w-0">
          <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-accent/20 text-accent font-bold text-sm uppercase">
            {targetInitials}
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-1.5 flex-wrap">
              <h3 className="truncate text-sm font-bold text-primary group-hover:text-accent transition-colors">
                {targetName}
              </h3>
              {recommendation.target_user_location && (
                <span className="rounded-full bg-elevated px-2 py-0.5 text-[10px] text-secondary flex items-center gap-1">
                  <MapPin size={9} className="text-accent" />
                  {recommendation.target_user_location}
                </span>
              )}
            </div>
            <p className="truncate text-xs text-secondary mt-0.5 flex items-center gap-1">
              <Briefcase size={11} className="shrink-0 text-accent/80" />
              <span className="font-medium text-primary/80">
                {recommendation.target_user_profession || "Chuyên môn"}
              </span>
              {recommendation.target_user_company && (
                <span className="text-secondary/70">
                  @ {recommendation.target_user_company}
                </span>
              )}
            </p>
          </div>
        </div>

        <ChevronRight
          size={18}
          className={cn(
            "text-secondary/40 shrink-0 transition-transform duration-200 mt-1",
            isSelected ? "text-accent translate-x-1" : "group-hover:text-primary group-hover:translate-x-0.5"
          )}
        />
      </div>

      {/* AI Reason Preview */}
      <div className="rounded-xl bg-elevated/40 border border-subtle/50 p-3 mb-3">
        <p className="text-xs text-primary/90 leading-relaxed line-clamp-2">
          {recommendation.reason}
        </p>
      </div>

      {/* Tags Matrix Preview */}
      <div className="flex flex-wrap items-center gap-1.5 mb-3">
        {recommendation.target_user_skills &&
          recommendation.target_user_skills.slice(0, 3).map((skill, idx) => (
            <span
              key={idx}
              className="rounded-md bg-surface border border-subtle px-2 py-0.5 text-[10px] font-medium text-accent"
            >
              {skill}
            </span>
          ))}
        {recommendation.target_user_interests &&
          recommendation.target_user_interests.slice(0, 2).map((interest, idx) => (
            <span
              key={idx}
              className="rounded-md bg-elevated px-2 py-0.5 text-[10px] text-secondary"
            >
              #{interest}
            </span>
          ))}
      </div>

      {/* Card Actions Footer */}
      {!isProcessed ? (
        <div className="flex items-center gap-2 pt-3 border-t border-subtle/60">
          <Button
            variant="primary"
            size="sm"
            onClick={handleAccept}
            disabled={isLoading}
            className="flex-1 text-xs"
          >
            <MessageSquare size={13} className="mr-1.5" />
            {action === "accept" ? "Đang kết nối..." : "Kết nối & Mở Chat"}
          </Button>

          <Button
            variant="secondary"
            size="sm"
            onClick={handleReject}
            disabled={isLoading}
            className="text-xs text-secondary hover:text-primary"
          >
            Để sau
          </Button>

          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              onViewDetails?.(recommendation.id);
            }}
            className="text-xs text-secondary hover:text-accent p-2"
          >
            Chi tiết
          </Button>
        </div>
      ) : (
        <div className="flex items-center justify-between pt-2 border-t border-subtle/60 text-xs text-secondary">
          <span className="flex items-center gap-1.5 font-medium">
            {recommendation.status === "ACCEPTED" ? (
              <span className="text-accent flex items-center gap-1">
                <Check size={13} /> Đã kết nối
              </span>
            ) : recommendation.status === "REJECTED" ? (
              <span className="text-secondary flex items-center gap-1">
                <X size={13} /> Đã từ chối
              </span>
            ) : (
              "Đã ẩn"
            )}
          </span>
          <span className="text-xs text-accent hover:underline flex items-center gap-0.5">
            Xem chi tiết
          </span>
        </div>
      )}
    </div>
  );
}
