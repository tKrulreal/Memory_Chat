"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useConversationStore } from "@/lib/stores/conversation-store";
import { MessageSquare, UserPlus, Sparkles, Building2, Briefcase, Loader2, Check, Clock } from "lucide-react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { sendConnectionRequest } from "@/lib/api/connection-requests";
import { useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";

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

  const handleOpenChat = () => {
    if (conversationId) {
      setActive(conversationId);
      router.push("/chats");
    }
  };

  // Đã là bạn / đã từng chat → mở đoạn chat
  // Hồ sơ mới → gửi lời mời kết bạn, khi accept mới nhắn được
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
      toast.success(`Đã gửi lời mời kết bạn đến ${name}`, {
        description: "Bạn có thể nhắn tin sau khi lời mời được chấp nhận.",
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
    <div className="my-2.5 overflow-hidden rounded-xl border border-subtle bg-card/90 shadow-sm transition-all hover:border-accent/30 hover:shadow-md">
      {/* Top Header info */}
      <div className="p-3">
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-3">
            <div
              className={cn(
                "flex h-10 w-10 shrink-0 items-center justify-center rounded-full font-bold text-xs shadow-sm",
                hasChatted
                  ? "bg-gradient-to-tr from-blue-600 to-indigo-500 text-white"
                  : "bg-gradient-to-tr from-amber-500 to-purple-600 text-white"
              )}
            >
              {initials}
            </div>

            <div className="flex flex-col min-w-0">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-sm text-foreground truncate">{name}</span>
                {hasChatted ? (
                  <span className="rounded-md bg-blue-500/15 border border-blue-500/30 px-1.5 py-0.2 text-[10px] font-medium text-blue-300">
                    Đã từng chat
                  </span>
                ) : (
                  <span className="rounded-md bg-purple-500/15 border border-purple-500/30 px-1.5 py-0.2 text-[10px] font-medium text-purple-300 flex items-center gap-0.5">
                    <Sparkles size={9} />
                    Hồ sơ mới
                  </span>
                )}
              </div>

              {email && <span className="text-[11px] text-muted-foreground truncate">{email}</span>}
            </div>
          </div>
        </div>

        {/* Profession & Company */}
        {(profession || company) && (
          <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
            {profession && (
              <span className="flex items-center gap-1">
                <Briefcase size={11} className="text-accent" />
                <span className="truncate">{profession}</span>
              </span>
            )}
            {company && (
              <span className="flex items-center gap-1">
                <Building2 size={11} className="text-muted-foreground" />
                <span className="truncate">{company}</span>
              </span>
            )}
          </div>
        )}

        {/* Description / Summary reason */}
        {description && (
          <div className="mt-2 rounded-lg bg-muted/70 p-2 text-xs text-foreground leading-relaxed border border-subtle/50">
            {description}
          </div>
        )}
      </div>

      {/* Action Footer */}
      <div className="flex items-center justify-between border-t border-subtle/80 bg-muted/30 px-3 py-2">
        <span className="text-[11px] text-muted-foreground">
          {hasChatted
            ? "Sẵn sàng trong danh sách chat"
            : requestSent
              ? "Đang chờ đối phương chấp nhận"
              : "Cần kết bạn trước khi nhắn tin"}
        </span>

        {hasChatted ? (
          // Đã là bạn → mở chat trực tiếp
          <Button variant="ghost"
            type="button"
            onClick={handleOpenChat}
            className="flex items-center gap-1.5 rounded-lg bg-accent px-3 py-1.5 text-xs font-semibold text-white shadow hover:opacity-90 transition-opacity cursor-pointer"
          >
            <MessageSquare size={13} />
            <span>Mở đoạn chat</span>
          </Button>
        ) : requestSent ? (
          // Đã gửi lời mời → hiển thị pending state
          <Button variant="ghost"
            type="button"
            disabled
            className="flex items-center gap-1.5 rounded-lg bg-muted border border-subtle px-3 py-1.5 text-xs font-semibold text-muted-foreground cursor-not-allowed"
          >
            <Clock size={13} />
            <span>Đã gửi lời mời</span>
          </Button>
        ) : (
          // Hồ sơ mới → gửi lời mời kết bạn
          <Button variant="ghost"
            type="button"
            onClick={handleSendFriendRequest}
            disabled={isConnecting || !userId}
            className="flex items-center gap-1.5 rounded-lg bg-gradient-to-r from-purple-600 to-indigo-600 px-3 py-1.5 text-xs font-semibold text-white shadow hover:opacity-90 transition-opacity cursor-pointer disabled:opacity-50"
          >
            {isConnecting ? (
              <>
                <Loader2 size={13} className="animate-spin" />
                <span>Đang gửi...</span>
              </>
            ) : (
              <>
                <UserPlus size={13} />
                <span>Gửi lời mời kết bạn</span>
              </>
            )}
          </Button>
        )}
      </div>
    </div>
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
