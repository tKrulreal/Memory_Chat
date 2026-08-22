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
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  getConnectionDetail,
  acceptConnection,
  rejectConnection,
} from "@/lib/api/recommendations";
import { cn } from "@/lib/utils";
import { useRouter } from "next/navigation";
import { useConversationStore } from "@/lib/stores/conversation-store";

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
  const router = useRouter();
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
      queryClient.invalidateQueries({ queryKey: ["conversations"] });
      queryClient.invalidateQueries({ queryKey: ["connection-recommendations"] });
      if (data?.conversation_id) {
        setActiveConversation(data.conversation_id);
      }
      onAccepted?.();
      router.push("/chats");
    },
  });

  const rejectMutation = useMutation({
    mutationFn: () => rejectConnection(recommendationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["connection-recommendations"] });
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
    <div className="flex h-full flex-col bg-surface border border-subtle rounded-2xl shadow-xl overflow-hidden animate-in fade-in slide-in-from-right-4 duration-200">
      {/* Panel Header */}
      <div className="flex items-center justify-between border-b border-subtle px-5 py-3.5 bg-surface/90 backdrop-blur shrink-0">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-accent/15 text-accent">
            <Sparkles size={16} />
          </div>
          <div>
            <h2 className="text-sm font-bold text-primary">So sánh & Đánh giá tương thích</h2>
            <p className="text-[11px] text-secondary">Phân tích đối ứng giữa Bạn và {targetName}</p>
          </div>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="rounded-xl p-1.5 text-secondary hover:bg-elevated hover:text-primary transition-colors cursor-pointer"
          title="Đóng chi tiết"
        >
          <X size={18} />
        </button>
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
          <div className="py-12 text-center text-secondary">
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
                    : "bg-elevated border-subtle text-secondary"
                )}
              >
                <Sparkles size={13} />
                <span>{matchPercent}% Độ phù hợp hợp tác & networking</span>
              </div>
            </div>

            {/* Side-by-Side Comparison Profiles (Bạn vs Ứng viên) */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 rounded-2xl bg-elevated/40 border border-subtle p-4">
              {/* Left Column: YOU */}
              <div className="space-y-3.5">
                <div className="flex items-center gap-3">
                  <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-blue-500/20 text-xs font-bold text-blue-400 uppercase overflow-hidden">
                    {detail.current_user_avatar ? (
                      <img src={detail.current_user_avatar} alt={detail.current_user_name} className="h-full w-full object-cover" />
                    ) : (
                      myInitials
                    )}
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-1.5 flex-wrap">
                      <p className="text-sm font-bold text-primary truncate">{detail.current_user_name}</p>
                      <span className="rounded-full bg-blue-500/15 border border-blue-500/30 px-2 py-0.2 text-[10px] text-blue-400 font-semibold">
                        Bạn
                      </span>
                      {detail.current_user_location && (
                        <span className="rounded-full bg-surface border border-subtle px-1.5 py-0.2 text-[10px] text-secondary flex items-center gap-1">
                          <MapPin size={9} className="text-blue-400" />
                          {detail.current_user_location}
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-secondary truncate mt-0.5">
                      {detail.current_user_profession || "Chuyên môn"}
                      {detail.current_user_company && ` @ ${detail.current_user_company}`}
                    </p>
                  </div>
                </div>

                {/* Your Skills */}
                <div>
                  <p className="text-[11px] font-semibold uppercase tracking-wider text-secondary mb-1 flex items-center gap-1">
                    <Briefcase size={11} className="text-blue-400" />
                    Kỹ năng (Skills):
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {detail.current_user_skills && detail.current_user_skills.length > 0 ? (
                      detail.current_user_skills.map((skill, i) => (
                        <span
                          key={i}
                          className="rounded-lg bg-surface border border-blue-500/20 px-2 py-0.5 text-[11px] text-blue-300 font-medium"
                        >
                          {skill}
                        </span>
                      ))
                    ) : (
                      <span className="text-xs text-secondary italic">Chưa cập nhật</span>
                    )}
                  </div>
                </div>

                {/* Your Interests */}
                <div>
                  <p className="text-[11px] font-semibold uppercase tracking-wider text-secondary mb-1 flex items-center gap-1">
                    <Hash size={11} className="text-blue-400" />
                    Quan tâm (Interests):
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {detail.current_user_interests && detail.current_user_interests.length > 0 ? (
                      detail.current_user_interests.map((interest, i) => (
                        <span
                          key={i}
                          className="rounded-lg bg-elevated/70 border border-subtle/60 px-2 py-0.5 text-[10px] text-secondary"
                        >
                          #{interest}
                        </span>
                      ))
                    ) : (
                      <span className="text-xs text-secondary italic">Chưa cập nhật</span>
                    )}
                  </div>
                </div>
              </div>

              {/* Right Column: TARGET CANDIDATE */}
              <div className="space-y-3.5 border-t md:border-t-0 md:border-l border-subtle pt-3.5 md:pt-0 md:pl-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-accent text-white text-xs font-bold uppercase shadow-sm overflow-hidden">
                    {detail.target_user_avatar ? (
                      <img src={detail.target_user_avatar} alt={targetName} className="h-full w-full object-cover" />
                    ) : (
                      targetInitials
                    )}
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-1.5 flex-wrap">
                      <p className="text-sm font-bold text-primary truncate">{targetName}</p>
                      <span className="rounded-full bg-accent/15 border border-accent/30 px-2 py-0.2 text-[10px] text-accent font-semibold">
                        Ứng viên
                      </span>
                      {detail.target_user_location && (
                        <span className="rounded-full bg-surface border border-subtle px-1.5 py-0.2 text-[10px] text-secondary flex items-center gap-1">
                          <MapPin size={9} className="text-accent" />
                          {detail.target_user_location}
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-secondary truncate mt-0.5">
                      {detail.target_user_profession || "Chuyên môn"}
                      {detail.target_user_company && ` @ ${detail.target_user_company}`}
                    </p>
                  </div>
                </div>

                {/* Candidate Skills */}
                <div>
                  <p className="text-[11px] font-semibold uppercase tracking-wider text-secondary mb-1 flex items-center gap-1">
                    <Briefcase size={11} className="text-accent" />
                    Kỹ năng (Skills):
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {detail.target_user_skills && detail.target_user_skills.length > 0 ? (
                      detail.target_user_skills.map((skill, i) => (
                        <span
                          key={i}
                          className="rounded-lg bg-surface border border-accent/20 px-2 py-0.5 text-[11px] text-accent font-medium"
                        >
                          {skill}
                        </span>
                      ))
                    ) : (
                      <span className="text-xs text-secondary italic">Chưa cập nhật</span>
                    )}
                  </div>
                </div>

                {/* Candidate Interests */}
                <div>
                  <p className="text-[11px] font-semibold uppercase tracking-wider text-secondary mb-1 flex items-center gap-1">
                    <Hash size={11} className="text-accent" />
                    Quan tâm (Interests):
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {detail.target_user_interests && detail.target_user_interests.length > 0 ? (
                      detail.target_user_interests.map((interest, i) => (
                        <span
                          key={i}
                          className="rounded-lg bg-elevated/70 border border-subtle/60 px-2 py-0.5 text-[10px] text-secondary"
                        >
                          #{interest}
                        </span>
                      ))
                    ) : (
                      <span className="text-xs text-secondary italic">Chưa cập nhật</span>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Looking for & Offering Matrix */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
              {/* Your Needs */}
              <div className="rounded-2xl border border-blue-500/25 bg-blue-500/5 p-4 space-y-2">
                <h4 className="text-xs font-bold text-blue-300 flex items-center gap-1.5">
                  <ArrowRight size={13} className="text-blue-400" />
                  Looking for (Nhu cầu tìm kiếm của bạn):
                </h4>
                <ul className="text-xs text-blue-200/90 space-y-1">
                  {detail.current_user_needs && detail.current_user_needs.length > 0 ? (
                    detail.current_user_needs.map((need, i) => <li key={i}>• {need}</li>)
                  ) : (
                    <li className="italic text-secondary">Mở rộng quan hệ hợp tác chuyên môn</li>
                  )}
                </ul>
              </div>

              {/* Candidate Offering */}
              <div className="rounded-2xl border border-emerald-500/25 bg-emerald-500/5 p-4 space-y-2">
                <h4 className="text-xs font-bold text-emerald-300 flex items-center gap-1.5">
                  <Gift size={13} className="text-emerald-400" />
                  Offering ({targetName} có thể chia sẻ/đóng góp):
                </h4>
                <ul className="text-xs text-emerald-200/90 space-y-1">
                  {detail.target_user_offers && detail.target_user_offers.length > 0 ? (
                    detail.target_user_offers.map((offer, i) => <li key={i}>• {offer}</li>)
                  ) : (
                    <li className="italic text-secondary">Kinh nghiệm thực tiễn và chuyên môn</li>
                  )}
                </ul>
              </div>
            </div>

            {/* AI Match Reasoning */}
            <div className="rounded-2xl border border-subtle bg-surface p-4 space-y-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-accent flex items-center gap-1.5">
                <Sparkles size={14} />
                Đánh giá từ AI Matchmaker
              </h3>
              <p className="text-xs leading-relaxed text-primary">{detail.reason}</p>
            </div>

            {/* Suggested Intro Message Textarea */}
            {!isProcessed && (
              <div className="rounded-2xl border border-subtle bg-surface p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-bold uppercase tracking-wider text-secondary flex items-center gap-1.5">
                    <Send size={13} className="text-accent" />
                    Lời chào gửi tới {targetName} (AI gợi ý):
                  </label>
                  <span className="text-[10px] text-secondary">Tự động gửi khi kết nối</span>
                </div>
                <textarea
                  value={customMessage}
                  onChange={(e) => setCustomMessage(e.target.value)}
                  placeholder={`Chào ${targetName}, mình muốn kết nối để trao đổi về...`}
                  rows={3}
                  maxLength={500}
                  className="w-full rounded-xl bg-elevated border border-subtle px-3 py-2.5 text-xs text-primary placeholder:text-secondary focus:outline-none focus:ring-1 focus:ring-accent resize-none scrollbar-thin"
                />
              </div>
            )}
          </>
        )}
      </div>

      {/* Panel Sticky Footer Action Bar */}
      {detail && (
        <div className="border-t border-subtle bg-surface px-6 py-4 shrink-0 flex items-center justify-between gap-3">
          {!isProcessed ? (
            <>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => rejectMutation.mutate()}
                disabled={rejectMutation.isPending || acceptMutation.isPending}
                className="text-secondary hover:text-primary text-xs"
              >
                <ThumbsDown size={13} className="mr-1.5" />
                Không phải lúc này
              </Button>

              <Button
                variant="primary"
                size="sm"
                onClick={() => acceptMutation.mutate()}
                disabled={acceptMutation.isPending || rejectMutation.isPending}
                className="flex-1 shadow-md shadow-accent/20 text-xs font-semibold"
              >
                <MessageSquare size={13} className="mr-1.5" />
                {acceptMutation.isPending ? "Đang kết nối..." : "Gửi lời chào & Mở Chat ngay"}
              </Button>
            </>
          ) : (
            <div className="flex items-center justify-between w-full">
              <span className="text-xs text-secondary flex items-center gap-1.5 font-medium">
                {detail.status === "ACCEPTED" ? (
                  <span className="text-accent flex items-center gap-1">
                    <CheckCircle2 size={14} /> Đã kết nối thành công
                  </span>
                ) : (
                  <span className="text-secondary">Trạng thái: {detail.status}</span>
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
