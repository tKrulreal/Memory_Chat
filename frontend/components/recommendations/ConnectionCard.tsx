"use client";

import { useState } from "react";
import {
  UserPlus,
  X,
  Check,
  ChevronRight,
  Sparkles,
  Briefcase,
  MapPin,
  HelpCircle,
  Gift,
  Loader2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import {
  ConnectionRecommendation,
  acceptConnection,
  rejectConnection,
  dismissConnection,
} from "@/lib/api/recommendations";
import { cn } from "@/lib/utils";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { usePresenceStore } from "@/lib/stores/presence-store";
import { useLanguage } from "@/hooks/use-language";

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
  const queryClient = useQueryClient();
  const [isLoading, setIsLoading] = useState(false);
  const [action, setAction] = useState<"accept" | "reject" | null>(null);
  const { language, t } = useLanguage();
  const l = (vi: string, en: string) => language === "en" ? en : vi;

  const priorityStyles: Record<Priority, string> = {
    HIGH: "bg-accent/15 border-accent/30 text-accent",
    MEDIUM: "bg-amber-500/15 border-amber-500/30 text-amber-400",
    LOW: "bg-muted border-subtle text-muted-foreground",
  };

  const targetName =
    recommendation.target_user_name ||
    recommendation.target_contact_name ||
    l("Người dùng", "User");
  const targetEmail = recommendation.target_user_email || "";
  const targetInitials =
    targetName
      .split(" ")
      .map((part) => part[0])
      .join("")
      .slice(0, 2)
      .toUpperCase() || "U";

  const matchPercent = Math.round((recommendation.confidence ?? 0.5) * 100);

  const handleAccept = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsLoading(true);
    setAction("accept");
    try {
      await acceptConnection(recommendation.id);
      queryClient.invalidateQueries({ queryKey: ["connection-requests"] });
      queryClient.invalidateQueries({ queryKey: ["connections"] });
      queryClient.invalidateQueries({ queryKey: ["connection-recommendations"] });
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      queryClient.invalidateQueries({ queryKey: ["notifications-unread-count"] });
      onAccept?.(recommendation.id);
      toast.success(l(`Đã gửi lời mời kết bạn đến ${targetName}`, `Connection request sent to ${targetName}`), {
        description: l("Bạn có thể nhắn tin sau khi lời mời được chấp nhận.", "You can message them after they accept the request."),
      });
    } catch (error: any) {
      toast.error(error?.message || l("Không thể gửi lời mời. Vui lòng thử lại.", "Could not send the request. Please try again."));
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
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      queryClient.invalidateQueries({ queryKey: ["notifications-unread-count"] });
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
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      queryClient.invalidateQueries({ queryKey: ["notifications-unread-count"] });
      onDismiss?.(recommendation.id);
    } catch (error) {
      console.error("Failed to dismiss:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const isProcessed = recommendation.status !== "PENDING";

  return (
    <div
      onClick={() => onViewDetails?.(recommendation.id)}
      className={cn(
        "group relative rounded-2xl border bg-white p-6 transition-all cursor-pointer select-none",
        isSelected
          ? "border-accent bg-slate-50/50 shadow-md ring-1 ring-accent/40"
          : "border-slate-100 hover:border-slate-200 hover:bg-slate-50/30 hover:shadow-md",
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
            {matchPercent}% {l("Phù hợp", "Match")}
          </span>
          <span className="text-[11px] font-medium text-muted-foreground">
            {recommendation.priority === "HIGH"
              ? l("Rất phù hợp", "Excellent match")
              : recommendation.priority === "MEDIUM"
              ? l("Tương thích tốt", "Good match")
              : l("Có tiềm năng", "Potential match")}
          </span>
        </div>

        {!isProcessed && (
          <Button variant="ghost"
            type="button"
            onClick={handleDismiss}
            disabled={isLoading}
            className="rounded-lg p-1 text-muted-foreground/60 hover:bg-muted hover:text-foreground transition-colors cursor-pointer"
            title={l("Bỏ qua gợi ý này", "Dismiss this suggestion")}
          >
            <X size={15} />
          </Button>
        )}
      </div>

      {/* Main Candidate Card */}
      <div className="flex items-start justify-between gap-4 mb-4">
        <div className="flex items-center gap-4 min-w-0">
          <div className="relative shrink-0">
            <Avatar className="h-14 w-14 border border-slate-100 shadow-sm">
              {recommendation.target_user_avatar && (
                <AvatarImage src={recommendation.target_user_avatar} alt={targetName} />
              )}
              <AvatarFallback className="bg-blue-50 text-blue-700 font-bold text-lg uppercase">
                {targetInitials}
              </AvatarFallback>
            </Avatar>
            {recommendation.target_user_id && usePresenceStore.getState().isUserOnline(recommendation.target_user_id) ? (
              <span className="absolute bottom-0 right-0 h-3.5 w-3.5 rounded-full bg-green-500 ring-2 ring-white" title={t("online")} />
            ) : (
              <span className="absolute bottom-0 right-0 h-3.5 w-3.5 rounded-full bg-slate-100 border-2 border-slate-400 ring-2 ring-white" title={t("offline")} />
            )}
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2 flex-wrap mb-1">
              <h3 className="truncate text-base font-bold text-slate-900 group-hover:text-blue-700 transition-colors">
                {targetName}
              </h3>
              {recommendation.target_user_location && (
                <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-500 flex items-center gap-1">
                  <MapPin size={12} className="text-blue-600" />
                  {recommendation.target_user_location}
                </span>
              )}
            </div>
            <p className="truncate text-sm font-medium text-slate-500 flex items-center gap-1.5">
              <Briefcase size={14} className="shrink-0 text-blue-600/80" />
              <span className="text-slate-700">
                {recommendation.target_user_profession || l("Chuyên môn", "Profession")}
              </span>
              {recommendation.target_user_company && (
                <span className="text-slate-400">
                  @ {recommendation.target_user_company}
                </span>
              )}
            </p>
          </div>
        </div>

        <ChevronRight
          size={18}
          className={cn(
            "text-muted-foreground/40 shrink-0 transition-transform duration-200 mt-1",
            isSelected ? "text-accent translate-x-1" : "group-hover:text-foreground group-hover:translate-x-0.5"
          )}
        />
      </div>

      {/* AI Reason Preview */}
      <div className="rounded-xl bg-blue-50/50 border border-blue-100/50 p-4 mb-4">
        <p className="text-sm font-medium text-slate-700 leading-relaxed line-clamp-2">
          {recommendation.reason}
        </p>
      </div>

      {/* Tags Matrix Preview */}
      <div className="flex flex-wrap items-center gap-2 mb-4">
        {recommendation.target_user_skills &&
          recommendation.target_user_skills.slice(0, 3).map((skill, idx) => (
            <Badge
              key={idx}
              variant="outline"
              className="rounded-full border-blue-200 bg-white px-2.5 py-0.5 text-xs font-semibold text-blue-700 shadow-sm"
            >
              {skill}
            </Badge>
          ))}
        {recommendation.target_user_interests &&
          recommendation.target_user_interests.slice(0, 2).map((interest, idx) => (
            <Badge
              key={idx}
              variant="secondary"
              className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-semibold text-slate-600 hover:bg-slate-200"
            >
              #{interest}
            </Badge>
          ))}
      </div>

      {/* Card Actions Footer */}
      {!isProcessed ? (
        <div className="flex items-center gap-3 pt-4 border-t border-slate-100">
          <Button
            variant="primary"
            size="sm"
            onClick={handleAccept}
            disabled={isLoading}
            className="flex-1 text-sm rounded-full font-semibold shadow-sm flex justify-center items-center py-2.5"
          >
            {action === "accept" ? (
              <>
                <Loader2 size={16} className="mr-2 animate-spin" />
                {l("Đang gửi lời mời...", "Sending request...")}
              </>
            ) : (
              <>
                <UserPlus size={16} className="mr-2" />
                {l("Gửi lời mời kết bạn", "Send Connection Request")}
              </>
            )}
          </Button>

          <Button
            variant="secondary"
            size="sm"
            onClick={handleReject}
            disabled={isLoading}
            className="text-sm font-semibold rounded-full bg-slate-100 text-slate-600 hover:bg-slate-200 hover:text-slate-800"
          >
            {l("Để sau", "Later")}
          </Button>

          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              onViewDetails?.(recommendation.id);
            }}
            className="text-sm font-semibold text-slate-500 hover:text-blue-700 hover:bg-blue-50 rounded-full px-4"
          >
            {l("Chi tiết", "Details")}
          </Button>
        </div>
      ) : (
        <div className="flex items-center justify-between pt-2 border-t border-subtle/60 text-xs text-muted-foreground">
          <span className="flex items-center gap-1.5 font-medium">
            {recommendation.status === "ACCEPTED" ? (
              <span className="text-accent flex items-center gap-1">
                <Check size={13} /> {l("Đã kết nối", "Connected")}
              </span>
            ) : recommendation.status === "REJECTED" ? (
              <span className="text-muted-foreground flex items-center gap-1">
                <X size={13} /> {l("Đã từ chối", "Declined")}
              </span>
            ) : (
              l("Đã ẩn", "Hidden")
            )}
          </span>
          <span className="text-xs text-accent hover:underline flex items-center gap-0.5">
            {l("Xem chi tiết", "View details")}
          </span>
        </div>
      )}
    </div>
  );
}
