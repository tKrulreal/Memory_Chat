"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { usePathname } from "next/navigation";
import {
  ChevronLeft,
  ChevronDown,
  Lightbulb,
  Phone,
  X,
  Sparkles,
  RefreshCw,
  ArrowRight,
  Clock,
  CheckCircle2,
  Tag,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { AIRecommendationCard } from "@/components/ai/ai-recommendation-card";
import { ContactTagsCard } from "@/components/chat/contact-tags-card";

import { useUIStore } from "@/lib/stores/ui-store";
import { useAuthStore } from "@/lib/stores/auth-store";
import { useConversationStore } from "@/lib/stores/conversation-store";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getConversations } from "@/lib/api/conversations";
import { getConversationContext, refreshConversationContext } from "@/lib/api/context";
import { useAISettings } from "@/hooks/use-ai-settings";
import { cn } from "@/lib/utils";
import { toast } from "sonner";

const MIN_WIDTH = 280;
const MAX_WIDTH = 640;
const DEFAULT_WIDTH = 340;

export function InfoPanel() {
  const pathname = usePathname();
  const infoPanelOpen = useUIStore((s) => s.infoPanelOpen);
  const setInfoPanelOpen = useUIStore((s) => s.setInfoPanelOpen);

  const isChatsPage = pathname === "/chats";

  // Resizable width state
  const [panelWidth, setPanelWidth] = useState<number>(() => {
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("memorychat_info_panel_width");
      if (saved) {
        const parsed = parseInt(saved, 10);
        if (!isNaN(parsed) && parsed >= MIN_WIDTH && parsed <= MAX_WIDTH) {
          return parsed;
        }
      }
    }
    return DEFAULT_WIDTH;
  });

  const [isResizing, setIsResizing] = useState(false);
  const resizeRef = useRef<{ startX: number; startWidth: number } | null>(null);

  const startResizing = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsResizing(true);
    resizeRef.current = {
      startX: e.clientX,
      startWidth: panelWidth,
    };
    document.body.style.userSelect = "none";
    document.body.style.cursor = "col-resize";
  }, [panelWidth]);

  useEffect(() => {
    if (!isResizing) return;

    const handleMouseMove = (e: MouseEvent) => {
      if (!resizeRef.current) return;
      const deltaX = resizeRef.current.startX - e.clientX;
      const newWidth = Math.min(
        Math.max(resizeRef.current.startWidth + deltaX, MIN_WIDTH),
        Math.min(MAX_WIDTH, window.innerWidth * 0.55)
      );
      setPanelWidth(newWidth);
    };

    const handleMouseUp = () => {
      setIsResizing(false);
      resizeRef.current = null;
      document.body.style.userSelect = "";
      document.body.style.cursor = "";
      localStorage.setItem("memorychat_info_panel_width", panelWidth.toString());
    };

    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };
  }, [isResizing, panelWidth]);

  // If not on chats page or info panel is not open, do not render
  if (!isChatsPage) {
    return null;
  }

  return (
    <>
      {/* Desktop resizable panel */}
      <aside
        aria-label="Contact information"
        style={{ width: infoPanelOpen ? `${panelWidth}px` : "0px" }}
        className={cn(
          "relative hidden h-full shrink-0 flex-col border-l border-subtle bg-card transition-[opacity] duration-150 xl:flex select-auto",
          infoPanelOpen ? "opacity-100" : "overflow-hidden opacity-0 border-none",
          isResizing && "transition-none select-none"
        )}
      >
        {infoPanelOpen && (
          <>
            {/* Drag Handle on the Left Edge */}
            <div
              onMouseDown={startResizing}
              className={cn(
                "group absolute -left-1.5 top-0 bottom-0 z-20 w-3 cursor-col-resize flex items-center justify-center transition-colors",
                "hover:bg-accent/20 active:bg-accent/30",
                isResizing && "bg-accent/30"
              )}
              title="Kéo sang trái/phải để thay đổi kích thước bảng thông tin"
            >
              <div
                className={cn(
                  "h-8 w-1 rounded-full bg-subtle group-hover:bg-accent transition-colors",
                  isResizing && "bg-accent h-12"
                )}
              />
            </div>

            <PanelContent onClose={() => setInfoPanelOpen(false)} />
          </>
        )}
      </aside>

      {/* Tablet/mobile drawer overlay */}
      {infoPanelOpen && (
        <div className="fixed inset-0 z-40 xl:hidden">
          <Button
            variant="ghost"
            type="button"
            className="absolute inset-0 bg-black/60"
            onClick={() => setInfoPanelOpen(false)}
            aria-label="Close info panel"
          />
          <aside aria-label="Contact information" className="absolute right-0 top-0 h-full w-info-panel max-w-[85vw] bg-card shadow-xl">
            <PanelContent onClose={() => setInfoPanelOpen(false)} />
          </aside>
        </div>
      )}
    </>
  );
}

function PanelContent({ onClose }: { onClose: () => void }) {
  const user = useAuthStore((s) => s.user);
  const activeId = useConversationStore((s) => s.activeConversationId);
  const queryClient = useQueryClient();

  const { data: conversations = [] } = useQuery({
    queryKey: ["conversations"],
    queryFn: getConversations,
    enabled: !!user,
  });

  const { data: context, isLoading: isLoadingContext } = useQuery({
    queryKey: ["context", activeId],
    queryFn: () => getConversationContext(activeId!),
    enabled: !!activeId,
  });

  const { features } = useAISettings();

  const refreshMemoryMutation = useMutation({
    mutationFn: () => refreshConversationContext(activeId!),
    onSuccess: (data) => {
      queryClient.setQueryData(["context", activeId], data);
      queryClient.invalidateQueries({ queryKey: ["context", activeId] });
      toast.success("Đã cập nhật lại trí nhớ và ngữ cảnh đối phương!");
    },
    onError: () => {
      toast.error("Không thể làm mới ngữ cảnh đối phương.");
    },
  });

  const activeConversation = conversations.find((c) => c.id === activeId);
  const isUserA = user?.id === activeConversation?.user_a_id;
  const peerId = activeConversation
    ? isUserA
      ? activeConversation.user_b_id
      : activeConversation.user_a_id
    : "NC";
  const peer = isUserA ? activeConversation?.user_b : activeConversation?.user_a;

  let peerName = activeConversation ? `User ${peerId.substring(0, 4)}` : "NC";
  let peerShort = activeConversation ? peerId.substring(0, 2).toUpperCase() : "NC";

  if (peer) {
    peerName = peer.full_name || peer.email.split("@")[0];
    peerShort = peer.email.substring(0, 2).toUpperCase();
  }

  const handleMessageClick = () => {
    document.getElementById("composer-input")?.focus();
    if (window.innerWidth < 1280) {
      onClose();
    }
  };

  const interestsList = Array.isArray(context?.interested_in) ? context.interested_in : [];

  return (
    <div className="flex h-full flex-col min-w-0">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-subtle px-4 py-3 shrink-0">
        <h2 className="text-sm font-semibold truncate">Thông tin đối phương</h2>
        <Button
          variant="ghost"
          type="button"
          onClick={onClose}
          className="rounded-button p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground cursor-pointer"
          aria-label="Close panel"
          title="Đóng thanh thông tin"
        >
          <X size={16} />
        </Button>
      </div>

      {/* Content */}
      <div className="scrollbar-thin flex-1 overflow-y-auto p-4 space-y-4">
        {/* Peer Profile Card */}
        <div className="flex flex-col items-center text-center p-6 bg-white rounded-2xl border border-slate-100 shadow-sm">
          <Avatar className="h-20 w-20 shadow-md border-2 border-white">
            <AvatarFallback className="bg-blue-50 text-blue-700 text-2xl font-bold uppercase">
              {peerShort}
            </AvatarFallback>
          </Avatar>
          <h3 className="mt-4 text-lg font-bold text-slate-900 truncate max-w-full">{peerName}</h3>
          <p className="text-sm font-medium text-slate-500 mt-1 truncate max-w-full">{peer?.email || "Direct message"}</p>
          <div className="flex items-center gap-2 mt-3 bg-green-50 text-green-700 px-3 py-1 rounded-full border border-green-100">
            <span className="flex h-2 w-2 rounded-full bg-green-500 shadow-sm"></span>
            <p className="text-xs font-bold">Đang hoạt động</p>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-2 gap-2">
          <Button variant="primary" size="sm" onClick={handleMessageClick} className="w-full text-xs font-semibold">
            Nhắn tin
          </Button>
          <Button variant="secondary" size="sm" disabled title="Tính năng gọi thoại sắp ra mắt" className="w-full text-xs">
            <Phone size={14} className="mr-1.5" />
            Gọi thoại
          </Button>
        </div>

        {/* AI Context Card (Trí nhớ Ngữ cảnh AI về đối phương) */}
        {features.memory && (
          <div className="rounded-2xl border border-slate-200/80 bg-white p-4 space-y-3.5 shadow-sm">
            {/* Header with refresh button */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1.5">
                <Sparkles size={14} className="text-blue-600" />
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-800">
                  Trí nhớ Ngữ cảnh AI
                </h4>
              </div>

              <Button
                variant="ghost"
                type="button"
                size="sm"
                onClick={() => refreshMemoryMutation.mutate()}
                disabled={refreshMemoryMutation.isPending || isLoadingContext}
                className="flex items-center gap-1 text-[11px] font-medium text-slate-500 hover:text-blue-600 hover:bg-blue-50 px-2 py-1 h-auto rounded-lg cursor-pointer disabled:opacity-50"
                title="Quét lại tin nhắn để cập nhật tóm tắt và ngữ cảnh mới nhất"
              >
                <RefreshCw
                  size={12}
                  className={cn("text-blue-600", refreshMemoryMutation.isPending && "animate-spin")}
                />
                <span>{refreshMemoryMutation.isPending ? "Đang quét..." : "Quét lại"}</span>
              </Button>
            </div>

            {/* 1. AI Summary: Ngắn gọn, các ý chính */}
            <div className="space-y-1">
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                Tóm tắt về đối phương
              </span>
              <p className="text-xs text-slate-700 leading-relaxed font-normal bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                {context?.summary || "Chưa có đủ dữ liệu hội thoại để tóm tắt. AI sẽ tự động phân tích khi bạn trao đổi thêm."}
              </p>
            </div>

            {/* 2. Interested in / Topics: Chủ đề quan tâm tự do từ hội thoại */}
            <div className="space-y-1.5">
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1">
                <Tag size={11} className="text-blue-500" />
                Chủ đề quan tâm
              </span>
              {interestsList.length > 0 ? (
                <div className="flex flex-wrap gap-1.5 pt-0.5">
                  {interestsList.map((interest, idx) => (
                    <span
                      key={idx}
                      className="rounded-full bg-blue-50 border border-blue-200 px-2.5 py-0.5 text-xs font-semibold text-blue-700 shadow-2xs"
                    >
                      #{interest}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-400 italic">Chưa xác định chủ đề quan tâm.</p>
              )}
            </div>

            {/* 3. Follow-up / Gợi ý việc tiếp theo: Bám sát tin nhắn gần nhất */}
            {context?.follow_up && (
              <div className="rounded-xl bg-amber-50/70 border border-amber-200/80 p-2.5 space-y-1">
                <p className="text-[11px] font-bold text-amber-900 flex items-center gap-1.5 uppercase tracking-wider">
                  <ArrowRight size={12} className="text-amber-600" />
                  Gợi ý việc tiếp theo:
                </p>
                <p className="text-xs text-amber-950 font-medium leading-relaxed">
                  {context.follow_up}
                </p>
              </div>
            )}

            {/* 4. Last met / Bối cảnh quen biết nếu có */}
            {context?.last_met && (
              <div className="flex items-center gap-1.5 text-[11px] text-slate-400 pt-1 border-t border-slate-100">
                <Clock size={11} className="text-slate-400" />
                <span>Bối cảnh: {context.last_met}</span>
              </div>
            )}
          </div>
        )}

        {/* AI Recommendation Follow-up Card */}
        {features.recommendation && <AIRecommendationCard />}

        {/* Contact Category Tags Card (AI Hub Tagging) */}
        {features.tagging && <ContactTagsCard />}

        {/* Extra details accordions */}
        <details className="group rounded-2xl border border-slate-100 bg-white shadow-sm overflow-hidden">
          <summary className="cursor-pointer list-none flex items-center justify-between px-5 py-4 text-sm font-bold text-slate-700 hover:bg-slate-50 transition-colors">
            <span>Thông tin kênh chat</span>
            <ChevronDown size={16} className="text-slate-400 transition-transform duration-200 group-open:-rotate-180" />
          </summary>
          <div className="border-t border-slate-100 bg-slate-50/50 px-5 py-4 text-sm text-slate-500 font-medium leading-relaxed">
            Cuộc trò chuyện trực tiếp bảo mật. Trí nhớ AI chỉ lưu trữ riêng cho tài khoản của bạn.
          </div>
        </details>

        <details className="group rounded-2xl border border-slate-100 bg-white shadow-sm overflow-hidden">
          <summary className="cursor-pointer list-none flex items-center justify-between px-5 py-4 text-sm font-bold text-slate-700 hover:bg-slate-50 transition-colors">
            <span>Tệp phương tiện & liên kết</span>
            <ChevronDown size={16} className="text-slate-400 transition-transform duration-200 group-open:-rotate-180" />
          </summary>
          <div className="border-t border-slate-100 bg-slate-50/50 px-5 py-4 text-sm text-slate-500 font-medium">
            Chưa có tệp phương tiện nào được chia sẻ.
          </div>
        </details>

        <details className="group rounded-2xl border border-slate-100 bg-white shadow-sm overflow-hidden">
          <summary className="cursor-pointer list-none flex items-center justify-between px-5 py-4 text-sm font-bold text-slate-700 hover:bg-slate-50 transition-colors">
            <div className="flex items-center gap-2">
              <Lightbulb size={16} className="text-amber-500" />
              Quyền riêng tư & hỗ trợ
            </div>
            <ChevronDown size={16} className="text-slate-400 transition-transform duration-200 group-open:-rotate-180" />
          </summary>
          <div className="border-t border-slate-100 bg-slate-50/50 px-5 py-4 text-sm text-slate-500 font-medium leading-relaxed">
            Các tùy chọn báo cáo, chặn người dùng hoặc tắt thông báo.
          </div>
        </details>
      </div>

      {/* Mobile Footer */}
      <div className="border-t border-subtle p-3 xl:hidden shrink-0">
        <Button variant="ghost" size="sm" className="w-full text-xs" onClick={onClose}>
          <ChevronLeft size={14} className="mr-1" />
          Quay lại trò chuyện
        </Button>
      </div>
    </div>
  );
}
