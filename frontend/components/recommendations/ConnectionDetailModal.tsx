"use client";

import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  X,
  MessageSquare,
  Check,
  Sparkles,
  ArrowRight,
  User,
  Briefcase,
  MapPin,
  UserPlus,
  ShieldCheck,
  Target,
  Send,
  Loader2,
  Workflow,
  Cpu,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  getConnectionDetail,
  acceptConnection,
  rejectConnection,
} from "@/lib/api/recommendations";
import { cn } from "@/lib/utils";
import { toast } from "sonner";
import { usePresenceStore } from "@/lib/stores/presence-store";
import { useLanguage } from "@/hooks/use-language";

interface ConnectionDetailModalProps {
  recommendationId: string;
  onClose: () => void;
  onAccepted?: () => void;
}

export function ConnectionDetailModal({
  recommendationId,
  onClose,
  onAccepted,
}: ConnectionDetailModalProps) {
  const queryClient = useQueryClient();
  const [customMessage, setCustomMessage] = useState("");
  const { language, t } = useLanguage();
  const l = (vi: string, en: string) => language === "en" ? en : vi;

  const {
    data: detail,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["connection-detail", recommendationId],
    queryFn: () => getConnectionDetail(recommendationId),
    enabled: !!recommendationId,
  });

  useEffect(() => {
    if (detail?.suggested_intro) {
      setCustomMessage(detail.suggested_intro);
    }
  }, [detail?.suggested_intro]);

  const targetName = detail?.target_user_name || detail?.contact_b_name || l("Ứng viên", "Candidate");
  const targetInitials =
    targetName
      .split(" ")
      .map((part) => part[0])
      .join("")
      .slice(0, 2)
      .toUpperCase() || "U";

  const myName = detail?.current_user_name || l("Bạn", "You");
  const myInitials =
    myName
      .split(" ")
      .map((part) => part[0])
      .join("")
      .slice(0, 2)
      .toUpperCase() || "ME";

  const acceptMutation = useMutation({
    mutationFn: () => acceptConnection(recommendationId, customMessage || undefined),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["conversations"] });
      queryClient.invalidateQueries({ queryKey: ["connection-requests"] });
      queryClient.invalidateQueries({ queryKey: ["connection-recommendations"] });
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      queryClient.invalidateQueries({ queryKey: ["notifications-unread-count"] });
      onAccepted?.();
      onClose();
      toast.success(l(`Đã gửi lời mời kết bạn đến ${targetName}`, `Connection request sent to ${targetName}`), {
        description: l("Bạn có thể nhắn tin ngay sau khi đối phương chấp nhận.", "You can message them as soon as they accept."),
      });
    },
    onError: (err: any) => {
      toast.error(err?.message || l("Không thể gửi lời mời. Vui lòng thử lại.", "Could not send the request. Please try again."));
    },
  });

  const rejectMutation = useMutation({
    mutationFn: () => rejectConnection(recommendationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["connection-recommendations"] });
      onClose();
      toast.info(l("Đã bỏ qua gợi ý kết nối này.", "Connection suggestion dismissed."));
    },
  });

  const isProcessed = detail?.status !== "PENDING";
  const matchPercent = Math.round((detail?.confidence ?? 0.5) * 100);

  const isTargetOnline = detail?.target_user_id
    ? usePresenceStore.getState().isUserOnline(detail.target_user_id)
    : false;

  // Compute shared skills
  const mySkills = detail?.current_user_skills || [];
  const targetSkills = detail?.target_user_skills || [];
  const sharedSkills = mySkills.filter((s) =>
    targetSkills.some((ts) => ts.toLowerCase() === s.toLowerCase())
  );

  return (
    <Dialog open={true} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="w-[96vw] sm:w-[90vw] md:w-[80vw] lg:w-[68vw] xl:w-[66vw] max-w-[1250px] sm:max-w-none max-h-[92vh] flex flex-col p-0 gap-0 overflow-hidden rounded-3xl border-slate-100 shadow-2xl bg-slate-50">
        {/* Modal Header */}
        <DialogHeader className="px-6 py-5 border-b border-slate-200 bg-white shrink-0">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-600 text-white shadow-md shadow-blue-500/20">
                <Sparkles size={20} />
              </div>
              <div>
                <DialogTitle className="text-lg font-bold text-slate-900 flex items-center gap-2">
                   {l("Bảng So Sánh & Ghép Đôi AI (Matchmaker Comparison)", "AI Matchmaker Comparison")}
                </DialogTitle>
                <DialogDescription className="text-xs text-slate-500 mt-0.5">
                   {l("Phân tích độ tương thích đa tiêu chí giữa Hồ sơ của bạn và Ứng viên tiềm năng.", "A multi-factor compatibility analysis of your profile and a potential connection.")}
                </DialogDescription>
              </div>
            </div>

            {/* Match Score Badge */}
            {detail && (
              <div className="flex items-center gap-2 shrink-0">
                <span
                  className={cn(
                    "rounded-full border px-3.5 py-1 text-xs font-bold tracking-wide uppercase flex items-center gap-1.5 shadow-2xs",
                    detail.confidence >= 0.8
                      ? "bg-blue-50 border-blue-200 text-blue-700"
                      : detail.confidence >= 0.6
                      ? "bg-amber-50 border-amber-200 text-amber-700"
                      : "bg-slate-100 border-slate-200 text-slate-600"
                  )}
                >
                  <Sparkles size={13} className="text-blue-600" />
                   {matchPercent}% {l("Tương thích", "Compatible")}
                </span>
              </div>
            )}
          </div>
        </DialogHeader>

        {/* Scrollable Content Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin">
          {isLoading ? (
            <div className="space-y-4">
              <Skeleton className="h-40 w-full rounded-2xl" />
              <Skeleton className="h-28 w-full rounded-2xl" />
              <Skeleton className="h-24 w-full rounded-2xl" />
            </div>
          ) : isError ? (
            <div className="text-center py-12 text-slate-500">
               {l("Không thể tải thông tin so sánh chi tiết. Vui lòng thử lại sau.", "Could not load the detailed comparison. Please try again later.")}
            </div>
          ) : detail ? (
            <>
              {/* SIDE-BY-SIDE PROFILES COMPARISON */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                {/* Column 1: Current User */}
                <div className="rounded-3xl border border-blue-100 bg-white p-6 space-y-4 shadow-sm relative overflow-hidden">
                  <div className="absolute top-0 right-0 bg-blue-600 text-white text-[10px] font-bold px-3 py-1 rounded-bl-xl uppercase tracking-wider">
                     {l("Hồ sơ của bạn", "Your Profile")}
                  </div>
                  
                  <div className="flex items-center gap-3.5 pt-1">
                    <Avatar className="h-12 w-12 border-2 border-blue-200 shadow-sm shrink-0">
                      <AvatarFallback className="bg-blue-50 text-blue-700 font-bold text-sm">
                        {myInitials}
                      </AvatarFallback>
                    </Avatar>
                    <div className="min-w-0 flex-1">
                      <h4 className="text-base font-bold text-slate-900 truncate">{myName}</h4>
                      <p className="text-xs text-slate-500 truncate flex items-center gap-1 mt-0.5">
                        <Briefcase size={12} className="text-blue-500 shrink-0" />
                         {detail.current_user_profession || l("Chuyên môn", "Profession")}
                        {detail.current_user_company && ` @ ${detail.current_user_company}`}
                      </p>
                      {detail.current_user_location && (
                        <p className="text-xs text-slate-400 truncate flex items-center gap-1 mt-0.5">
                          <MapPin size={11} className="text-blue-400 shrink-0" />
                          {detail.current_user_location}
                        </p>
                      )}
                    </div>
                  </div>

                  {/* Your Skills */}
                  <div>
                    <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">
                       {l("Kỹ năng của bạn", "Your Skills")}
                    </p>
                    <div className="flex flex-wrap gap-1.5">
                      {detail.current_user_skills && detail.current_user_skills.length > 0 ? (
                        detail.current_user_skills.map((skill, i) => {
                          const isMatch = sharedSkills.some((s) => s.toLowerCase() === skill.toLowerCase());
                          return (
                            <Badge
                              key={i}
                              variant="secondary"
                              className={cn(
                                "text-xs font-semibold px-2.5 py-0.5 rounded-lg border",
                                isMatch
                                  ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                                  : "bg-slate-100 text-slate-700 border-slate-200/60"
                              )}
                            >
                              {skill}
                              {isMatch && <Check size={11} className="ml-1 text-emerald-600" />}
                            </Badge>
                          );
                        })
                      ) : (
                         <span className="text-xs text-slate-400 italic">{l("Chưa cập nhật kỹ năng", "No skills added")}</span>
                      )}
                    </div>
                  </div>

                  {/* Your Looking For */}
                  <div className="rounded-2xl bg-blue-50/60 border border-blue-100/80 p-3.5 space-y-1">
                    <p className="text-xs font-bold text-blue-900 flex items-center gap-1.5">
                      <Target size={13} className="text-blue-600" />
                       {l("Nhu cầu tìm kiếm (Looking for):", "Looking for:")}
                    </p>
                    <ul className="text-xs text-blue-800/80 space-y-0.5 pl-4 list-disc">
                      {detail.current_user_needs && detail.current_user_needs.length > 0 ? (
                        detail.current_user_needs.map((need, i) => <li key={i}>{need}</li>)
                      ) : (
                         <li className="italic text-slate-400 list-none -ml-4">{l("Mở rộng mạng lưới quan hệ chuyên môn", "Expand a professional network")}</li>
                      )}
                    </ul>
                  </div>
                </div>

                {/* Column 2: Candidate */}
                <div className="rounded-3xl border border-indigo-100 bg-white p-6 space-y-4 shadow-sm relative overflow-hidden">
                  <div className="absolute top-0 right-0 bg-indigo-600 text-white text-[10px] font-bold px-3 py-1 rounded-bl-xl uppercase tracking-wider">
                     {l("Ứng viên được đề xuất", "Suggested Connection")}
                  </div>

                  <div className="flex items-center gap-3.5 pt-1">
                    <div className="relative shrink-0">
                      <Avatar className="h-12 w-12 border-2 border-indigo-200 shadow-sm">
                        {detail.target_user_avatar && (
                          <AvatarImage src={detail.target_user_avatar} alt={targetName} />
                        )}
                        <AvatarFallback className="bg-indigo-50 text-indigo-700 font-bold text-sm">
                          {targetInitials}
                        </AvatarFallback>
                      </Avatar>
                      {isTargetOnline ? (
                         <span className="absolute bottom-0 right-0 h-3.5 w-3.5 rounded-full bg-emerald-500 ring-2 ring-white" title={t("online")} />
                      ) : (
                         <span className="absolute bottom-0 right-0 h-3.5 w-3.5 rounded-full bg-slate-100 border-2 border-slate-400 ring-2 ring-white" title={t("offline")} />
                      )}
                    </div>
                    <div className="min-w-0 flex-1">
                      <h4 className="text-base font-bold text-slate-900 truncate">{targetName}</h4>
                      <p className="text-xs text-slate-500 truncate flex items-center gap-1 mt-0.5">
                        <Briefcase size={12} className="text-indigo-500 shrink-0" />
                         {detail.target_user_profession || l("Chuyên môn", "Profession")}
                        {detail.target_user_company && ` @ ${detail.target_user_company}`}
                      </p>
                      {detail.target_user_location && (
                        <p className="text-xs text-slate-400 truncate flex items-center gap-1 mt-0.5">
                          <MapPin size={11} className="text-indigo-400 shrink-0" />
                          {detail.target_user_location}
                        </p>
                      )}
                    </div>
                  </div>

                  {/* Target Skills */}
                  <div>
                    <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">
                       {l("Kỹ năng của ứng viên", "Candidate Skills")}
                    </p>
                    <div className="flex flex-wrap gap-1.5">
                      {detail.target_user_skills && detail.target_user_skills.length > 0 ? (
                        detail.target_user_skills.map((skill, i) => {
                          const isMatch = sharedSkills.some((s) => s.toLowerCase() === skill.toLowerCase());
                          return (
                            <Badge
                              key={i}
                              variant="secondary"
                              className={cn(
                                "text-xs font-semibold px-2.5 py-0.5 rounded-lg border",
                                isMatch
                                  ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                                  : "bg-indigo-50 text-indigo-700 border-indigo-200/60"
                              )}
                            >
                              {skill}
                              {isMatch && <Check size={11} className="ml-1 text-emerald-600" />}
                            </Badge>
                          );
                        })
                      ) : (
                         <span className="text-xs text-slate-400 italic">{l("Chưa cập nhật kỹ năng", "No skills added")}</span>
                      )}
                    </div>
                  </div>

                  {/* Target Offering */}
                  <div className="rounded-2xl bg-emerald-50/60 border border-emerald-100/80 p-3.5 space-y-1">
                    <p className="text-xs font-bold text-emerald-900 flex items-center gap-1.5">
                      <Sparkles size={13} className="text-emerald-600" />
                       {l("Có thể chia sẻ (Offering):", "Offering:")}
                    </p>
                    <ul className="text-xs text-emerald-800/80 space-y-0.5 pl-4 list-disc">
                      {detail.target_user_offers && detail.target_user_offers.length > 0 ? (
                        detail.target_user_offers.map((offer, i) => <li key={i}>{offer}</li>)
                      ) : (
                         <li className="italic text-slate-400 list-none -ml-4">{l("Kinh nghiệm chuyên môn và hỗ trợ dự án", "Professional experience and project support")}</li>
                      )}
                    </ul>
                  </div>
                </div>
              </div>

              {/* AI MATCH RATIONALE BOX */}
              <div className="rounded-3xl border border-blue-200/70 bg-gradient-to-r from-blue-50/80 via-white to-indigo-50/80 p-5 space-y-2 shadow-xs">
                <div className="flex items-center gap-2 text-blue-700">
                  <Workflow size={16} className="text-blue-600" />
                  <h4 className="text-xs font-bold uppercase tracking-wider">
                     {l("Phân tích & Lý do ghép đôi từ AI Matchmaker", "AI Matchmaker Analysis & Rationale")}
                  </h4>
                </div>
                <p className="text-sm leading-relaxed text-slate-800 font-medium">
                  {detail.reason}
                </p>
              </div>

              {/* INTRO GREETING COMPOSER */}
              {!isProcessed && (
                <div className="rounded-3xl border border-slate-200 bg-white p-5 space-y-2.5 shadow-sm">
                  <div className="flex items-center justify-between">
                    <label className="text-xs font-bold text-slate-800 flex items-center gap-1.5">
                      <Send size={13} className="text-blue-600" />
                       {l("Lời chào mở đầu cuộc trò chuyện (Gửi cùng lời mời kết bạn):", "Opening message (sent with your request):")}
                    </label>
                    <span className="text-[11px] text-slate-400 font-medium">
                      {customMessage.length}/500
                    </span>
                  </div>
                  <Textarea
                    value={customMessage}
                    onChange={(e) => setCustomMessage(e.target.value)}
                     placeholder={l(`Chào ${targetName}, mình thấy bạn cũng quan tâm đến... Chúng ta kết nối nhé!`, `Hi ${targetName}, I noticed we share an interest in... Let's connect!`)}
                    rows={3}
                    maxLength={500}
                    className="w-full rounded-2xl border-slate-200 bg-slate-50 text-sm focus:border-blue-500 focus:bg-white resize-none"
                  />
                  <p className="text-[11px] text-slate-400">
                     {l("AI đã tự động tạo lời chào cá nhân hóa dựa trên điểm chung của hai bạn. Bạn có thể chỉnh sửa trước khi gửi.", "AI created a personalized greeting based on your shared interests. You can edit it before sending.")}
                  </p>
                </div>
              )}
            </>
          ) : null}
        </div>

        {/* Modal Footer */}
        <DialogFooter className="px-6 py-4 border-t border-slate-200 bg-white shrink-0 flex items-center justify-between sm:justify-between">
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="rounded-xl text-slate-500 hover:bg-slate-100"
          >
             {isProcessed ? l("Đóng", "Close") : l("Để sau", "Later")}
          </Button>

          {!isProcessed && (
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => rejectMutation.mutate()}
                disabled={rejectMutation.isPending || acceptMutation.isPending}
                className="rounded-xl border-slate-200 text-slate-600 hover:bg-slate-100"
              >
                 {rejectMutation.isPending ? l("Đang bỏ qua...", "Dismissing...") : l("Bỏ qua", "Dismiss")}
              </Button>

              <Button
                size="sm"
                onClick={() => acceptMutation.mutate()}
                disabled={acceptMutation.isPending || rejectMutation.isPending}
                className="rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold shadow-sm px-4"
              >
                {acceptMutation.isPending ? (
                  <>
                    <Loader2 size={14} className="mr-1.5 animate-spin" />
                     {l("Đang gửi...", "Sending...")}
                  </>
                ) : (
                  <>
                    <UserPlus size={14} className="mr-1.5" />
                     {l("Gửi lời mời & Mở Chat", "Send Request & Open Chat")}
                  </>
                )}
              </Button>
            </div>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
