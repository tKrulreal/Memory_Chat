"use client";

import { useState } from "react";
import { MessageSquare, X, Check, ChevronRight, Sparkles, Briefcase, MapPin, ArrowRight } from "lucide-react";
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

type Priority = "HIGH" | "MEDIUM" | "LOW";

interface ConnectionCardProps {
  recommendation: ConnectionRecommendation;
  onAccept?: (id: string) => void;
  onReject?: (id: string) => void;
  onDismiss?: (id: string) => void;
  onViewDetails?: (id: string) => void;
}

export function ConnectionCard({
  recommendation,
  onAccept,
  onReject,
  onDismiss,
  onViewDetails,
}: ConnectionCardProps) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [isLoading, setIsLoading] = useState(false);
  const [action, setAction] = useState<"accept" | "reject" | null>(null);

  const priorityStyles: Record<Priority, string> = {
    HIGH: "bg-red-500/10 border-red-500/30 text-red-400",
    MEDIUM: "bg-amber-500/10 border-amber-500/30 text-amber-400",
    LOW: "bg-accent/10 border-accent/30 text-accent",
  };

  const handleAccept = async () => {
    setIsLoading(true);
    setAction("accept");
    try {
      await acceptConnection(recommendation.id);
      queryClient.invalidateQueries({ queryKey: ["conversations"] });
      onAccept?.(recommendation.id);
      router.push("/chats");
    } catch (error) {
      console.error("Failed to accept:", error);
    } finally {
      setIsLoading(false);
      setAction(null);
    }
  };


  const handleReject = async () => {
    setIsLoading(true);
    setAction("reject");
    try {
      await rejectConnection(recommendation.id);
      onReject?.(recommendation.id);
    } catch (error) {
      console.error("Failed to reject:", error);
    } finally {
      setIsLoading(false);
      setAction(null);
    }
  };

  const handleDismiss = async () => {
    setIsLoading(true);
    try {
      await dismissConnection(recommendation.id);
      onDismiss?.(recommendation.id);
    } catch (error) {
      console.error("Failed to dismiss:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const isProcessed = recommendation.status !== "PENDING";
  const targetName = recommendation.target_user_name || recommendation.target_contact_name || "Người dùng";
  const targetEmail = recommendation.target_user_email || "";
  const targetInitials = targetName
    .split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase() || "U";

  return (
    <div
      className={cn(
        "rounded-button border border-subtle bg-surface p-5 transition-all",
        isProcessed ? "opacity-60" : "hover:border-neutral-700 shadow-sm"
      )}
    >
      {/* Header bar */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2.5 flex-wrap">
          <div className="flex h-7 w-7 items-center justify-center rounded-button bg-elevated text-accent">
            <Sparkles size={14} />
          </div>
          <span
            className={cn(
              "rounded-full border px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wider",
              priorityStyles[recommendation.priority as Priority] || priorityStyles.MEDIUM
            )}
          >
            {recommendation.priority} MATCH
          </span>
          <span className="text-xs text-secondary">
            {Math.round(recommendation.confidence * 100)}% độ phù hợp
          </span>
        </div>
        {!isProcessed && (
          <button
            type="button"
            onClick={handleDismiss}
            disabled={isLoading}
            className="rounded-button p-1 text-secondary hover:bg-elevated hover:text-primary transition-colors"
            title="Bỏ qua gợi ý"
          >
            <X size={16} />
          </button>
        )}
      </div>

      {/* Recommended User Hero Box */}
      <div className="rounded-button bg-elevated/40 border border-subtle/80 p-4 mb-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3.5 min-w-0">
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-accent/20 text-accent text-base font-bold uppercase">
              {targetInitials}
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2 flex-wrap">
                <h3 className="truncate text-base font-semibold text-primary">{targetName}</h3>
                <span className="rounded-full bg-surface border border-subtle px-2 py-0.5 text-[10px] text-secondary">
                  Real User
                </span>
                {recommendation.target_user_location && (
                  <span className="rounded-full bg-surface border border-subtle px-2 py-0.5 text-[10px] text-secondary flex items-center gap-1">
                    <MapPin size={10} className="text-accent" />
                    {recommendation.target_user_location}
                  </span>
                )}
              </div>
              <p className="truncate text-xs text-secondary mt-0.5 flex items-center gap-1.5 flex-wrap">
                <Briefcase size={12} className="shrink-0 text-accent/70" />
                <span>{recommendation.target_user_profession || "Chuyên môn"}</span>
                {recommendation.target_user_company && (
                  <span className="text-secondary/70">@ {recommendation.target_user_company}</span>
                )}
              </p>
              {targetEmail && (
                <p className="truncate text-[11px] text-secondary/60 mt-0.5">{targetEmail}</p>
              )}
            </div>
          </div>

          {/* Quick Skills / Interests Badges */}
          <div className="flex flex-col sm:items-end gap-1.5 max-w-xs">
            {recommendation.target_user_skills && recommendation.target_user_skills.length > 0 && (
              <div className="flex flex-wrap gap-1 sm:justify-end">
                {recommendation.target_user_skills.slice(0, 3).map((skill, idx) => (
                  <span
                    key={idx}
                    className="rounded-full bg-surface border border-subtle px-2 py-0.5 text-[11px] text-accent/90"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            )}
            {recommendation.target_user_interests && recommendation.target_user_interests.length > 0 && (
              <div className="flex flex-wrap gap-1 sm:justify-end">
                {recommendation.target_user_interests.slice(0, 2).map((interest, idx) => (
                  <span
                    key={idx}
                    className="rounded-full bg-elevated/70 border border-subtle/60 px-2 py-0.5 text-[10px] text-secondary"
                  >
                    #{interest}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>


      {/* AI Reason */}
      <div className="mb-4 space-y-1">
        <p className="text-xs font-semibold uppercase tracking-wide text-secondary flex items-center gap-1">
          <Sparkles size={12} className="text-accent" />
          Lý do AI gợi ý cho bạn
        </p>
        <p className="text-sm text-primary leading-relaxed">
          {recommendation.reason}
        </p>
      </div>

      {/* Actions */}
      {!isProcessed ? (
        <div className="flex items-center gap-2 pt-3 border-t border-subtle">
          <Button
            variant="primary"
            size="sm"
            onClick={handleAccept}
            disabled={isLoading}
            className="flex-1"
          >
            <MessageSquare className="w-3.5 h-3.5 mr-1.5" />
            {action === "accept" ? "Đang kết nối..." : "Kết nối & Trò chuyện"}
          </Button>
          <Button
            variant="secondary"
            size="sm"
            onClick={handleReject}
            disabled={isLoading}
          >
            Không phải lúc này
          </Button>
          {onViewDetails && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onViewDetails(recommendation.id)}
              className="text-secondary hover:text-primary"
            >
              Chi tiết
              <ChevronRight className="w-3.5 h-3.5 ml-1" />
            </Button>
          )}
        </div>
      ) : (
        <div className="flex items-center justify-between pt-2 border-t border-subtle text-xs text-secondary">
          <span className="flex items-center gap-1.5">
            {recommendation.status === "ACCEPTED" && (
              <span className="text-accent font-medium flex items-center gap-1">
                <Check size={14} /> Đã kết nối thành công
              </span>
            )}
            {recommendation.status === "REJECTED" && (
              <span className="text-secondary flex items-center gap-1">
                <X size={14} /> Đã từ chối gợi ý
              </span>
            )}
            {recommendation.status === "DISMISSED" && "Đã ẩn gợi ý"}
          </span>
          {onViewDetails && (
            <button
              type="button"
              onClick={() => onViewDetails(recommendation.id)}
              className="text-xs text-accent hover:underline flex items-center gap-0.5"
            >
              Xem lại chi tiết <ChevronRight size={12} />
            </button>
          )}
        </div>
      )}
    </div>
  );
}
