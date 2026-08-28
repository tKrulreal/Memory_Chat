"use client";

import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  X,
  MessageSquare,
  Sparkles,
  User,
  Briefcase,
  MapPin,
  Send,
  CheckCircle2,
  ThumbsDown,
  ArrowRight,
  Target,
  Gift,
  HelpCircle,
  Hash,
  UserPlus,
  Loader2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  getConnectionDetail,
  acceptConnection,
  rejectConnection,
} from "@/lib/api/recommendations";
import { cn } from "@/lib/utils";
import { useConversationStore } from "@/lib/stores/conversation-store";
import { toast } from "sonner";

interface ConnectionDetailPanelProps {
  recommendationId: string;
  onClose: () => void;
  onAccepted?: () => void;
}

export function ConnectionDetailPanel({
  recommendationId,
  onClose,
  onAccepted,
}: ConnectionDetailPanelProps) {
  const queryClient = useQueryClient();
  const setActiveConversation = useConversationStore((s) => s.setActiveConversation);
  const [customMessage, setCustomMessage] = useState("");

  const {
    data: detail,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["connection-detail", recommendationId],
    queryFn: () => getConnectionDetail(recommendationId),
    enabled: !!recommendationId,
  });

  // Pre-fill intro message from AI
  useEffect(() => {
    if (detail?.suggested_intro) {
      setCustomMessage(detail.suggested_intro);
    }
  }, [detail?.suggested_intro]);

  const acceptMutation = useMutation({
    mutationFn: () => acceptConnection(recommendationId, customMessage || undefined),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["connection-requests"] });
      queryClient.invalidateQueries({ queryKey: ["connections"] });
      queryClient.invalidateQueries({ queryKey: ["connection-recommendations"] });
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      queryClient.invalidateQueries({ queryKey: ["notifications-unread-count"] });
      onAccepted?.();
      toast.success(`Đã gửi lời mời kết bạn đến ${targetName}`, {
        description: "Bạn có thể nhắn tin sau khi lời mời được chấp nhận.",
      });
    },
    onError: (err: any) => {
      toast.error(err?.message || "Không thể gửi lời mời. Vui lòng thử lại.");
    },
  });

  const rejectMutation = useMutation({
    mutationFn: () => rejectConnection(recommendationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["connection-recommendations"] });
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      queryClient.invalidateQueries({ queryKey: ["notifications-unread-count"] });
      onClose();
    },
  });

  const isProcessed = detail?.status !== "PENDING";
  const myInitials = detail?.current_user_name?.[0]?.toUpperCase() || "BẠN";
  const targetName = detail?.target_user_name || detail?.contact_b_name || "Ứng viên";
  const targetInitials =
    targetName
      .split(" ")
      .map((part) => part[0])
      .join("")
      .slice(0, 2)
      .toUpperCase() || "U";

  const matchPercent = Math.round((detail?.confidence ?? 0.5) * 100);

  return (
    <div className="flex h-full flex-col bg-white border border-slate-100 rounded-3xl shadow-xl overflow-hidden animate-in fade-in slide-in-from-right-4 duration-200">
      {/* Panel Header */}
      <div className="flex items-center justify-between border-b border-slate-100 px-6 py-4 bg-white/90 backdrop-blur shrink-0">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 text-blue-600 shadow-sm">
            <Sparkles size={18} />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-900">So sánh & Đánh giá tương thích</h2>
            <p className="text-sm font-medium text-slate-500">Phân tích đối ứng giữa Bạn và {targetName}</p>
          </div>
        </div>
        <Button variant="ghost"
          type="button"
          onClick={onClose}
          className="rounded-xl p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors cursor-pointer"
          title="Đóng chi tiết"
        >
          <X size={18} />
        </Button>
      </div>

      {/* Scrollable Body */}
      <div className="flex-1 overflow-y-auto p-5 space-y-5 scrollbar-thin">
        {isLoading ? (
          <div className="space-y-4">
            <Skeleton className="h-10 w-48 mx-auto rounded-full" />
            <Skeleton className="h-44 w-full rounded-2xl" />
            <Skeleton className="h-28 w-full rounded-2xl" />
            <Skeleton className="h-24 w-full rounded-2xl" />
          </div>
        ) : isError || !detail ? (
          <div className="py-12 text-center text-muted-foreground">
            <p className="text-sm">Không thể tải chi tiết so sánh gợi ý.</p>
            <Button variant="secondary" size="sm" onClick={onClose} className="mt-3">
              Quay lại danh sách
            </Button>
          </div>
        ) : (
          <>
            {/* Confidence Score Pill */}
            <div className="flex items-center justify-center">
              <div
                className={cn(
                  "rounded-full border px-4 py-1.5 text-xs font-bold uppercase tracking-wider flex items-center gap-2 shadow-sm",
                  matchPercent >= 80
                    ? "bg-accent/15 border-accent/30 text-accent"
                    : matchPercent >= 60
                    ? "bg-amber-500/15 border-amber-500/30 text-amber-400"
                    : "bg-muted border-subtle text-muted-foreground"
                )}
              >
                <Sparkles size={13} />
                <span>{matchPercent}% Độ phù hợp hợp tác & networking</span>
              </div>
            </div>

            {/* Side-by-Side Comparison Profiles (Bạn vs Ứng viên) */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 rounded-3xl bg-slate-50/50 border border-slate-100 p-5">
              {/* Left Column: YOU */}
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <Avatar className="h-12 w-12 border border-blue-100 shadow-sm">
                    {detail.current_user_avatar && (
                      <AvatarImage src={detail.current_user_avatar} alt={detail.current_user_name} />
                    )}
                    <AvatarFallback className="bg-blue-100 text-blue-700 font-bold">
                      {myInitials}
                    </AvatarFallback>
                  </Avatar>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2 flex-wrap mb-1">
                      <p className="text-base font-bold text-slate-900 truncate">{detail.current_user_name}</p>
                      <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200 px-2 py-0 text-xs">
                        Bạn
                      </Badge>
                      {detail.current_user_location && (
                        <span className="rounded-full bg-white border border-slate-200 px-2 py-0.5 text-xs text-slate-500 flex items-center gap-1 shadow-sm">
                          <MapPin size={12} className="text-blue-500" />
                          {detail.current_user_location}
                        </span>
                      )}
                    </div>
                    <p className="text-sm font-medium text-slate-500 truncate">
                      {detail.current_user_profession || "Chuyên môn"}
                      {detail.current_user_company && ` @ ${detail.current_user_company}`}
                    </p>
                  </div>
                </div>

                {/* Your Skills */}
                <div>
                  <p className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2 flex items-center gap-1.5">
                    <Briefcase size={14} className="text-blue-500" />
                    Kỹ năng (Skills):
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {detail.current_user_skills && detail.current_user_skills.length > 0 ? (
                      detail.current_user_skills.map((skill, i) => (
                        <Badge
                          key={i}
                          variant="outline"
                          className="bg-white border-blue-200 text-blue-600 font-semibold shadow-sm"
                        >
                          {skill}
                        </Badge>
                      ))
                    ) : (
                      <span className="text-sm text-slate-400 italic">Chưa cập nhật</span>
                    )}
                  </div>
                </div>

                {/* Your Interests */}
                <div>
                  <p className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2 flex items-center gap-1.5">
                    <Hash size={14} className="text-blue-500" />
                    Quan tâm (Interests):
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {detail.current_user_interests && detail.current_user_interests.length > 0 ? (
                      detail.current_user_interests.map((interest, i) => (
                        <Badge
                          key={i}
                          variant="secondary"
                          className="bg-slate-200/50 text-slate-600 hover:bg-slate-200 font-medium"
                        >
                          #{interest}
                        </Badge>
                      ))
                    ) : (
                      <span className="text-sm text-slate-400 italic">Chưa cập nhật</span>
                    )}
                  </div>
                </div>
              </div>

              {/* Right Column: TARGET CANDIDATE */}
              <div className="space-y-4 border-t md:border-t-0 md:border-l border-slate-200 pt-4 md:pt-0 md:pl-5">
                <div className="flex items-center gap-3">
                  <Avatar className="h-12 w-12 border border-blue-600/20 shadow-sm">
                    {detail.target_user_avatar && (
                      <AvatarImage src={detail.target_user_avatar} alt={targetName} />
                    )}
                    <AvatarFallback className="bg-blue-600 text-white font-bold text-lg">
                      {targetInitials}
                    </AvatarFallback>
                  </Avatar>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2 flex-wrap mb-1">
                      <p className="text-base font-bold text-slate-900 truncate">{targetName}</p>
                      <Badge className="bg-blue-600 hover:bg-blue-700 px-2 py-0 text-xs">
                        Ứng viên
                      </Badge>
                      {detail.target_user_location && (
                        <span className="rounded-full bg-white border border-slate-200 px-2 py-0.5 text-xs text-slate-500 flex items-center gap-1 shadow-sm">
                          <MapPin size={12} className="text-blue-600" />
                          {detail.target_user_location}
                        </span>
                      )}
                    </div>
                    <p className="text-sm font-medium text-slate-500 truncate">
                      {detail.target_user_profession || "Chuyên môn"}
                      {detail.target_user_company && ` @ ${detail.target_user_company}`}
                    </p>
                  </div>
                </div>

                {/* Candidate Skills */}
                <div>
                  <p className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2 flex items-center gap-1.5">
                    <Briefcase size={14} className="text-blue-600" />
                    Kỹ năng (Skills):
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {detail.target_user_skills && detail.target_user_skills.length > 0 ? (
                      detail.target_user_skills.map((skill, i) => (
                        <Badge
                          key={i}
                          variant="outline"
                          className="bg-white border-blue-200 text-blue-700 font-semibold shadow-sm"
                        >
                          {skill}
                        </Badge>
                      ))
                    ) : (
                      <span className="text-sm text-slate-400 italic">Chưa cập nhật</span>
                    )}
                  </div>
                </div>

                {/* Candidate Interests */}
                <div>
                  <p className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2 flex items-center gap-1.5">
                    <Hash size={14} className="text-blue-600" />
                    Quan tâm (Interests):
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {detail.target_user_interests && detail.target_user_interests.length > 0 ? (
                      detail.target_user_interests.map((interest, i) => (
                        <Badge
                          key={i}
                          variant="secondary"
                          className="bg-slate-200/50 text-slate-700 hover:bg-slate-200 font-medium"
                        >
                          #{interest}
                        </Badge>
                      ))
                    ) : (
                      <span className="text-sm text-slate-400 italic">Chưa cập nhật</span>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Looking for & Offering Matrix */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Your Needs */}
              <div className="rounded-3xl border border-blue-100 bg-blue-50/30 p-5 space-y-3">
                <h4 className="text-sm font-bold text-blue-700 flex items-center gap-2">
                  <ArrowRight size={16} className="text-blue-500" />
                  Looking for (Nhu cầu tìm kiếm của bạn):
                </h4>
                <ul className="text-sm font-medium text-blue-900/80 space-y-2">
                  {detail.current_user_needs && detail.current_user_needs.length > 0 ? (
                    detail.current_user_needs.map((need, i) => <li key={i}>• {need}</li>)
                  ) : (
                    <li className="italic text-slate-400">Mở rộng quan hệ hợp tác chuyên môn</li>
                  )}
                </ul>
              </div>

              {/* Candidate Offering */}
              <div className="rounded-3xl border border-emerald-100 bg-emerald-50/30 p-5 space-y-3">
                <h4 className="text-sm font-bold text-emerald-700 flex items-center gap-2">
                  <Gift size={16} className="text-emerald-500" />
                  Offering ({targetName} có thể chia sẻ):
                </h4>
                <ul className="text-sm font-medium text-emerald-900/80 space-y-2">
                  {detail.target_user_offers && detail.target_user_offers.length > 0 ? (
                    detail.target_user_offers.map((offer, i) => <li key={i}>• {offer}</li>)
                  ) : (
                    <li className="italic text-slate-400">Kinh nghiệm thực tiễn và chuyên môn</li>
                  )}
                </ul>
              </div>
            </div>

            {/* AI Match Reasoning */}
            <div className="rounded-3xl border border-slate-100 bg-white shadow-sm p-6 space-y-3">
              <h3 className="text-sm font-bold uppercase tracking-wider text-blue-600 flex items-center gap-2">
                <Sparkles size={18} />
                Đánh giá từ AI Matchmaker
              </h3>
              <p className="text-sm font-medium leading-relaxed text-slate-700">{detail.reason}</p>
            </div>

            {/* Suggested Intro Message Textarea */}
            {!isProcessed && (
              <div className="rounded-3xl border border-slate-100 bg-white shadow-sm p-6 space-y-3">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <label className="text-sm font-bold uppercase tracking-wider text-slate-500 flex items-center gap-2">
                    <Send size={16} className="text-blue-500" />
                    Lời chào gửi tới {targetName} (AI gợi ý):
                  </label>
                  <span className="text-xs font-semibold text-slate-400 bg-slate-100 px-2 py-1 rounded-md">Tự động gửi khi kết nối</span>
                </div>
                <Textarea
                  value={customMessage}
                  onChange={(e) => setCustomMessage(e.target.value)}
                  placeholder={`Chào ${targetName}, mình muốn kết nối để trao đổi về...`}
                  rows={4}
                  maxLength={500}
                  className="w-full resize-none text-sm font-medium text-slate-700 rounded-2xl bg-slate-50/50 border-slate-200 focus-visible:ring-blue-500/30 mt-2 p-4"
                />
              </div>
            )}
          </>
        )}
      </div>

      {/* Panel Sticky Footer Action Bar */}
      {detail && (
        <div className="border-t border-subtle bg-card px-6 py-4 shrink-0 flex items-center justify-between gap-3">
          {!isProcessed ? (
            <>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => rejectMutation.mutate()}
                disabled={rejectMutation.isPending || acceptMutation.isPending}
                className="text-muted-foreground hover:text-foreground text-xs"
              >
                <ThumbsDown size={13} className="mr-1.5" />
                Không phải lúc này
              </Button>

              <Button
                variant="primary"
                size="sm"
                onClick={() => acceptMutation.mutate()}
                disabled={acceptMutation.isPending || rejectMutation.isPending}
                className="flex-1 shadow-md shadow-accent/20 text-sm font-semibold rounded-full flex justify-center items-center py-2.5"
              >
                {acceptMutation.isPending ? (
                  <>
                    <Loader2 size={13} className="mr-1.5 animate-spin" />
                    Đang gửi lời mời...
                  </>
                ) : (
                  <>
                    <UserPlus size={13} className="mr-1.5" />
                    Gửi lời mời kết bạn
                  </>
                )}
              </Button>
            </>
          ) : (
            <div className="flex items-center justify-between w-full">
              <span className="text-xs text-muted-foreground flex items-center gap-1.5 font-medium">
                {detail.status === "ACCEPTED" ? (
                  <span className="text-accent flex items-center gap-1">
                    <CheckCircle2 size={14} /> Đã kết nối thành công
                  </span>
                ) : (
                  <span className="text-muted-foreground">Trạng thái: {detail.status}</span>
                )}
              </span>
              <Button variant="secondary" size="sm" onClick={onClose}>
                Đóng
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
