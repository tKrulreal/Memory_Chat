"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

import { X, MessageSquare, Check, Sparkles, ArrowRight, User, Briefcase, MapPin } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

import {
  getConnectionDetail,
  acceptConnection,
  rejectConnection,
} from "@/lib/api/recommendations";
import { cn } from "@/lib/utils";
import { useRouter } from "next/navigation";

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
  const router = useRouter();
  const queryClient = useQueryClient();
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

  const acceptMutation = useMutation({
    mutationFn: () => acceptConnection(recommendationId, customMessage || undefined),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["conversations"] });
      queryClient.invalidateQueries({ queryKey: ["connection-recommendations"] });
      onAccepted?.();
      onClose();
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
  const myInitials = detail?.current_user_name?.[0]?.toUpperCase() || "YOU";
  const targetName = detail?.target_user_name || detail?.contact_b_name || "Người dùng";
  const targetInitials = targetName
    .split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase() || "U";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/70 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      {/* Modal Card */}
      <div className="relative w-full max-w-xl max-h-[90vh] flex flex-col rounded-button border border-subtle bg-surface shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-subtle px-6 py-4 bg-surface shrink-0">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-button bg-elevated text-accent">
              <Sparkles size={16} />
            </div>
            <div>
              <h2 className="text-base font-semibold text-primary">Chi tiết cơ hội kết nối</h2>
              <p className="text-xs text-secondary">Phân tích AI giữa bạn và người dùng trong hệ thống</p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-button p-1.5 text-secondary hover:bg-elevated hover:text-primary transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-5 scrollbar-thin">
          {isLoading ? (
            <div className="space-y-4">
              <Skeleton className="h-32 w-full rounded-button" />
              <Skeleton className="h-24 w-full rounded-button" />
              <Skeleton className="h-20 w-full rounded-button" />
            </div>
          ) : isError ? (
            <div className="text-center py-8 text-secondary">
              Không thể tải thông tin chi tiết.
            </div>
          ) : detail ? (
            <>
              {/* Confidence Score Pill */}
              <div className="flex items-center justify-center">
                <div
                  className={cn(
                    "rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-wider flex items-center gap-1.5",
                    detail.confidence >= 0.8
                      ? "bg-accent/15 border-accent/30 text-accent"
                      : detail.confidence >= 0.6
                      ? "bg-amber-500/15 border-amber-500/30 text-amber-400"
                      : "bg-elevated border-subtle text-secondary"
                  )}
                >
                  <Sparkles size={12} />
                  <span>{Math.round(detail.confidence * 100)}% Độ phù hợp hợp tác & networking</span>
                </div>
              </div>

              {/* Side by Side Profiles */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 rounded-button bg-elevated/40 border border-subtle/80 p-4">
                {/* You */}
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-blue-500/20 text-xs font-semibold text-blue-400 uppercase">
                      {myInitials}
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-1.5 flex-wrap">
                        <p className="text-sm font-semibold text-primary truncate">{detail.current_user_name}</p>
                        <span className="rounded-full bg-surface px-1.5 py-0.2 text-[10px] text-blue-400 font-medium">
                          Bạn
                        </span>
                        {detail.current_user_location && (
                          <span className="rounded-full bg-surface border border-subtle px-1.5 py-0.2 text-[10px] text-secondary flex items-center gap-1">
                            <MapPin size={9} className="text-blue-400" />
                            {detail.current_user_location}
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-secondary truncate">
                        {detail.current_user_profession || "Chuyên môn"}
                        {detail.current_user_company && ` @ ${detail.current_user_company}`}
                      </p>
                    </div>
                  </div>

                  {/* Skills */}
                  {detail.current_user_skills && detail.current_user_skills.length > 0 && (
                    <div>
                      <p className="text-[11px] uppercase tracking-wide text-secondary mb-1">Skills</p>
                      <div className="flex flex-wrap gap-1">
                        {detail.current_user_skills.map((skill, i) => (
                          <span
                            key={i}
                            className="rounded-full bg-surface border border-subtle px-2 py-0.5 text-[11px] text-blue-300"
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Interests */}
                  {detail.current_user_interests && detail.current_user_interests.length > 0 && (
                    <div>
                      <p className="text-[11px] uppercase tracking-wide text-secondary mb-1">Interests</p>
                      <div className="flex flex-wrap gap-1">
                        {detail.current_user_interests.map((interest, i) => (
                          <span
                            key={i}
                            className="rounded-full bg-elevated/70 border border-subtle/60 px-2 py-0.5 text-[10px] text-secondary"
                          >
                            #{interest}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Target User */}
                <div className="space-y-3 border-t md:border-t-0 md:border-l border-subtle pt-3 md:pt-0 md:pl-4">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-accent/20 text-xs font-semibold text-accent uppercase">
                      {targetInitials}
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-1.5 flex-wrap">
                        <p className="text-sm font-semibold text-primary truncate">{targetName}</p>
                        <span className="rounded-full bg-surface px-1.5 py-0.2 text-[10px] text-accent font-medium">
                          Ứng viên
                        </span>
                        {detail.target_user_location && (
                          <span className="rounded-full bg-surface border border-subtle px-1.5 py-0.2 text-[10px] text-secondary flex items-center gap-1">
                            <MapPin size={9} className="text-accent" />
                            {detail.target_user_location}
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-secondary truncate">
                        {detail.target_user_profession || "Chuyên môn"}
                        {detail.target_user_company && ` @ ${detail.target_user_company}`}
                      </p>
                    </div>
                  </div>

                  {/* Skills */}
                  {detail.target_user_skills && detail.target_user_skills.length > 0 && (
                    <div>
                      <p className="text-[11px] uppercase tracking-wide text-secondary mb-1">Skills</p>
                      <div className="flex flex-wrap gap-1">
                        {detail.target_user_skills.map((skill, i) => (
                          <span
                            key={i}
                            className="rounded-full bg-surface border border-subtle px-2 py-0.5 text-[11px] text-accent"
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Interests */}
                  {detail.target_user_interests && detail.target_user_interests.length > 0 && (
                    <div>
                      <p className="text-[11px] uppercase tracking-wide text-secondary mb-1">Interests</p>
                      <div className="flex flex-wrap gap-1">
                        {detail.target_user_interests.map((interest, i) => (
                          <span
                            key={i}
                            className="rounded-full bg-elevated/70 border border-subtle/60 px-2 py-0.5 text-[10px] text-secondary"
                          >
                            #{interest}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Looking for & Offering Matrix */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="rounded-button border border-blue-500/20 bg-blue-500/5 p-3.5 space-y-2">
                  <h4 className="text-xs font-semibold text-blue-300 flex items-center gap-1.5">
                    <ArrowRight size={13} />
                    Looking for (Nhu cầu tìm kiếm của bạn):
                  </h4>
                  <ul className="text-xs text-blue-200/80 space-y-1">
                    {detail.current_user_needs && detail.current_user_needs.length > 0 ? (
                      detail.current_user_needs.map((need, i) => <li key={i}>• {need}</li>)
                    ) : (
                      <li className="italic text-secondary">Mở rộng quan hệ hợp tác chuyên môn</li>
                    )}
                  </ul>
                </div>

                <div className="rounded-button border border-emerald-500/20 bg-emerald-500/5 p-3.5 space-y-2">
                  <h4 className="text-xs font-semibold text-emerald-300 flex items-center gap-1.5">
                    <ArrowRight size={13} />
                    Offering ({targetName} có thể chia sẻ/đóng góp):
                  </h4>
                  <ul className="text-xs text-emerald-200/80 space-y-1">
                    {detail.target_user_offers && detail.target_user_offers.length > 0 ? (
                      detail.target_user_offers.map((offer, i) => <li key={i}>• {offer}</li>)
                    ) : (
                      <li className="italic text-secondary">Kinh nghiệm thực tiễn và chuyên môn</li>
                    )}
                  </ul>
                </div>
              </div>


              {/* AI Match Reasoning */}
              <div className="rounded-button border border-subtle bg-elevated/30 p-4 space-y-1.5">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-secondary flex items-center gap-1.5">
                  <Sparkles size={13} className="text-accent" />
                  Đánh giá từ AI Matchmaker
                </h3>
                <p className="text-sm leading-relaxed text-primary">{detail.reason}</p>
              </div>

              {/* Custom Message to Send */}
              {!isProcessed && (
                <div className="space-y-1.5">
                  <label className="block text-xs font-medium text-secondary">
                    Lời chào gửi tới {targetName} (Tin nhắn mở đầu cuộc trò chuyện):
                  </label>
                  <textarea
                    value={customMessage || detail.suggested_intro || ""}
                    onChange={(e) => setCustomMessage(e.target.value)}
                    placeholder={`Chào ${targetName}, mình muốn kết nối để trao đổi về...`}
                    rows={3}
                    maxLength={500}
                    className="w-full rounded-button bg-input border border-subtle px-3 py-2 text-sm text-primary placeholder:text-secondary focus:outline-none focus:ring-1 focus:ring-accent resize-none scrollbar-thin"
                  />
                  <div className="flex justify-between text-[11px] text-secondary">
                    <span>Lời chào này sẽ được gửi trực tiếp khi bạn bấm Kết nối.</span>
                    <span>{(customMessage || detail.suggested_intro || "").length}/500</span>
                  </div>
                </div>
              )}
            </>
          ) : null}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-2 border-t border-subtle px-6 py-4 bg-surface shrink-0">
          <Button variant="ghost" size="sm" onClick={onClose}>
            {isProcessed ? "Đóng" : "Hủy"}
          </Button>
          {!isProcessed && (
            <>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => rejectMutation.mutate()}
                disabled={rejectMutation.isPending}
              >
                {rejectMutation.isPending ? "Đang xử lý..." : "Bỏ qua"}
              </Button>
              <Button
                variant="primary"
                size="sm"
                onClick={() => acceptMutation.mutate()}
                disabled={acceptMutation.isPending}
              >
                <MessageSquare className="w-3.5 h-3.5 mr-1.5" />
                {acceptMutation.isPending ? "Đang kết nối..." : "Gửi lời chào & Mở Chat"}
              </Button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
