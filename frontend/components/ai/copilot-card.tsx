"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useConversationStore } from "@/lib/stores/conversation-store";
import { MessageSquare, UserPlus, Sparkles, Building2, Briefcase, Loader2, Clock, Eye, X } from "lucide-react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { sendConnectionRequest } from "@/lib/api/connection-requests";
import { useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { UserProfileView } from "@/components/profile/user-profile-view";

interface CopilotCardProps {
  name: string;
  email: string;
  conversationId?: string;
  userId?: string;
  hasChatted: boolean;
  profession?: string;
  company?: string;
  description: string;
}

export function CopilotCard({
  name,
  email,
  conversationId,
  userId,
  hasChatted,
  profession,
  company,
  description,
}: CopilotCardProps) {
  const router = useRouter();
  const setActive = useConversationStore((s) => s.setActiveConversation);
  const queryClient = useQueryClient();
  const [isConnecting, setIsConnecting] = useState(false);
  const [requestSent, setRequestSent] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);

  const handleOpenChat = () => {
    if (conversationId) {
      setActive(conversationId);
      router.push("/chats");
    }
  };

  const handleSendFriendRequest = async () => {
    if (!userId) {
      toast.error("Không tìm thấy thông tin người dùng để gửi lời mời.");
      return;
    }

    setIsConnecting(true);
    try {
      await sendConnectionRequest(userId);
      setRequestSent(true);
      queryClient.invalidateQueries({ queryKey: ["connection-requests"] });
      queryClient.invalidateQueries({ queryKey: ["connections"] });
      queryClient.invalidateQueries({ queryKey: ["public-profile", userId] });
      toast.success(`Đã gửi lời mời kết bạn đến ${name}`, {
        description: "Bạn có thể nhắn tin sau khi đối phương chấp nhận.",
      });
    } catch (err: any) {
      const msg = err?.message || "";
      if (msg.includes("409") || msg.toLowerCase().includes("already") || msg.toLowerCase().includes("conflict")) {
        setRequestSent(true);
        toast.info(`Bạn đã gửi lời mời đến ${name} trước đó.`);
      } else {
        toast.error(msg || "Không thể gửi lời mời kết bạn.");
      }
    } finally {
      setIsConnecting(false);
    }
  };

  const initials = name ? name.substring(0, 2).toUpperCase() : "MC";

  return (
    <>
      <div className="my-2.5 overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-sm transition-all hover:border-blue-300 hover:shadow-md">
        {/* Top Header info */}
        <div className="p-3.5">
          <div className="flex items-start justify-between gap-2">
            <div className="flex items-center gap-3">
              <div
                className={cn(
                  "flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl font-bold text-xs shadow-sm",
                  hasChatted
                    ? "bg-gradient-to-tr from-blue-600 to-indigo-500 text-white"
                    : "bg-gradient-to-tr from-amber-500 to-purple-600 text-white"
                )}
              >
                {initials}
              </div>

              <div className="flex flex-col min-w-0">
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-sm text-slate-800 truncate">{name}</span>
                  {hasChatted ? (
                    <span className="rounded-md bg-blue-50 border border-blue-200 px-1.5 py-0.5 text-[10px] font-semibold text-blue-700">
                      Đã từng chat
                    </span>
                  ) : (
                    <span className="rounded-md bg-purple-50 border border-purple-200 px-1.5 py-0.5 text-[10px] font-semibold text-purple-700 flex items-center gap-0.5">
                      <Sparkles size={9} />
                      Hồ sơ mới
                    </span>
                  )}
                </div>

                {email && <span className="text-[11px] text-slate-400 truncate">{email}</span>}
              </div>
            </div>
          </div>

          {/* Profession & Company */}
          {(profession || company) && (
            <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-slate-600">
              {profession && (
                <span className="flex items-center gap-1 font-medium">
                  <Briefcase size={12} className="text-blue-600" />
                  <span className="truncate">{profession}</span>
                </span>
              )}
              {company && (
                <span className="flex items-center gap-1 text-slate-500">
                  <Building2 size={12} className="text-slate-400" />
                  <span className="truncate">{company}</span>
                </span>
              )}
            </div>
          )}

          {/* Description / Summary reason */}
          {description && (
            <div className="mt-2.5 rounded-xl bg-slate-50 p-2.5 text-xs text-slate-700 leading-relaxed border border-slate-100">
              {description}
            </div>
          )}
        </div>

        {/* Action Footer */}
        <div className="flex items-center justify-between border-t border-slate-100 bg-slate-50/70 px-3.5 py-2.5 flex-wrap gap-2">
          {/* View Profile Button */}
          {userId ? (
            <button
              type="button"
              onClick={() => setShowProfileModal(true)}
              className="flex items-center gap-1 text-xs font-semibold text-slate-600 hover:text-blue-600 transition-colors cursor-pointer"
            >
              <Eye size={13} />
              <span>Xem Profile</span>
            </button>
          ) : (
            <span className="text-[11px] text-slate-400">
              {hasChatted ? "Sẵn sàng trong danh sách chat" : "Hồ sơ công khai"}
            </span>
          )}

          {/* Connect / Chat Action Buttons */}
          <div className="flex items-center gap-2">
            {hasChatted ? (
              <Button
                type="button"
                size="sm"
                onClick={handleOpenChat}
                className="flex items-center gap-1.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-xs font-semibold text-white shadow-2xs cursor-pointer"
              >
                <MessageSquare size={13} />
                <span>Mở đoạn chat</span>
              </Button>
            ) : requestSent ? (
              <Button
                type="button"
                size="sm"
                disabled
                className="flex items-center gap-1.5 rounded-xl bg-slate-100 border border-slate-200 text-xs font-semibold text-slate-400 cursor-not-allowed"
              >
                <Clock size={13} />
                <span>Đã gửi lời mời</span>
              </Button>
            ) : (
              <Button
                type="button"
                size="sm"
                onClick={handleSendFriendRequest}
                disabled={isConnecting || !userId}
                className="flex items-center gap-1.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:opacity-90 text-xs font-semibold text-white shadow-2xs cursor-pointer disabled:opacity-50"
              >
                {isConnecting ? (
                  <>
                    <Loader2 size={13} className="animate-spin" />
                    <span>Đang gửi...</span>
                  </>
                ) : (
                  <>
                    <UserPlus size={13} />
                    <span>Gửi kết bạn</span>
                  </>
                )}
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Profile Modal Dialog */}
      {showProfileModal && userId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4 backdrop-blur-xs">
          <div className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-3xl bg-slate-50 p-6 shadow-2xl">
            <button
              type="button"
              onClick={() => setShowProfileModal(false)}
              className="absolute top-4 right-4 z-10 flex h-8 w-8 items-center justify-center rounded-full bg-white text-slate-400 hover:text-slate-700 shadow-sm cursor-pointer"
            >
              <X size={18} />
            </button>
            <UserProfileView userId={userId} isModal onClose={() => setShowProfileModal(false)} />
          </div>
        </div>
      )}
    </>
  );
}

export function renderCopilotMessageWithCards(content: string) {
  // Split by <card...>...</card>
  const parts = content.split(/(<card[^>]*>[\s\S]*?<\/card>)/);

  return parts.map((part, idx) => {
    if (part.startsWith("<card")) {
      const nameMatch = part.match(/name="([^"]+)"/);
      const emailMatch = part.match(/email="([^"]+)"/);
      const convIdMatch = part.match(/conversation_id="([^"]+)"/);
      const userIdMatch = part.match(/user_id="([^"]+)"/);
      const hasChattedMatch = part.match(/has_chatted="([^"]+)"/);
      const professionMatch = part.match(/profession="([^"]+)"/);
      const companyMatch = part.match(/company="([^"]+)"/);

      const name = nameMatch ? nameMatch[1] : "Người liên hệ";
      const email = emailMatch ? emailMatch[1] : "";
      const conversationId = convIdMatch ? convIdMatch[1] : "";
      const userId = userIdMatch ? userIdMatch[1] : "";
      const hasChatted = hasChattedMatch
        ? hasChattedMatch[1] === "true"
        : Boolean(conversationId && conversationId.trim() !== "");
      const profession = professionMatch ? professionMatch[1] : "";
      const company = companyMatch ? companyMatch[1] : "";
      const desc = part.replace(/<[^>]*>/g, "").trim();

      return (
        <CopilotCard
          key={idx}
          name={name}
          email={email}
          conversationId={conversationId}
          userId={userId}
          hasChatted={hasChatted}
          profession={profession}
          company={company}
          description={desc}
        />
      );
    }

    return part.trim() ? (
      <div key={idx} className="whitespace-pre-wrap mb-2 last:mb-0">
        {part}
      </div>
    ) : null;
  });
}
