"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import {
  getNotifications,
  markNotificationRead,
  markAllNotificationsRead,
  deleteNotification,
} from "@/lib/api/notifications";
import {
  acceptConnectionRequest,
  rejectConnectionRequest,
  getConnectionRequests,
} from "@/lib/api/connection-requests";
import {
  Bell,
  Check,
  CheckCheck,
  CheckCircle2,
  Filter,
  MessageSquare,
  Sparkles,
  Trash2,
  UserCheck,
  UserPlus,
  Users,
  X,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

function getRelativeTime(dateString: string) {
  if (!dateString) return "";
  const date = new Date(dateString);
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffInSeconds < 60) return "Vừa xong";
  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) return `${diffInMinutes} phút trước`;
  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) return `${diffInHours} giờ trước`;
  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 7) return `${diffInDays} ngày trước`;

  return date.toLocaleDateString("vi-VN");
}

type TabType = "all" | "unread" | "requests" | "matching";

export default function NotificationsPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<TabType>("all");

  const { data, isLoading } = useQuery({
    queryKey: ["notifications"],
    queryFn: () => getNotifications(1, 50),
  });

  const markAsReadMutation = useMutation({
    mutationFn: (id: string) => markNotificationRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      queryClient.invalidateQueries({ queryKey: ["notifications-unread-count"] });
    },
  });

  const markAllReadMutation = useMutation({
    mutationFn: () => markAllNotificationsRead(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      queryClient.invalidateQueries({ queryKey: ["notifications-unread-count"] });
      toast.success("Đã đánh dấu tất cả thông báo là đã đọc");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteNotification(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      queryClient.invalidateQueries({ queryKey: ["notifications-unread-count"] });
      toast.success("Đã xóa thông báo");
    },
  });

  const acceptRequestMutation = useMutation({
    mutationFn: async ({
      requestId,
      senderId,
      notifId,
    }: {
      requestId?: string;
      senderId?: string;
      notifId: string;
    }) => {
      let targetReqId = requestId;

      // Fallback: If requestId is missing, lookup pending incoming request by senderId
      if (!targetReqId && senderId) {
        try {
          const incoming = await getConnectionRequests("incoming", "PENDING", 1, 100);
          const matched = incoming.data.find(
            (r) => r.sender_id === senderId || r.sender?.id === senderId
          );
          if (matched) {
            targetReqId = matched.id;
          }
        } catch (e) {
          console.warn("Failed to lookup request for sender", e);
        }
      }

      if (!targetReqId) {
        await markNotificationRead(notifId);
        toast.info("Lời mời kết bạn này đã được xử lý hoặc không còn khả dụng.");
        return;
      }

      try {
        await acceptConnectionRequest(targetReqId);
        await markNotificationRead(notifId);
      } catch (err: any) {
        const msg = err.message || "";
        if (
          msg.includes("not pending") ||
          msg.includes("không ở trạng thái") ||
          msg.includes("Already") ||
          msg.includes("bạn bè")
        ) {
          await markNotificationRead(notifId);
          toast.info("Lời mời này đã được chấp nhận trước đó!");
          return;
        }
        throw err;
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      queryClient.invalidateQueries({ queryKey: ["notifications-unread-count"] });
      queryClient.invalidateQueries({ queryKey: ["connection-requests"] });
      queryClient.invalidateQueries({ queryKey: ["connections"] });
      queryClient.invalidateQueries({ queryKey: ["conversations"] });
      toast.success("Đã chấp nhận lời mời kết bạn!");
    },
    onError: (err: any) => {
      toast.error(err.message || "Không thể chấp nhận lời mời kết bạn");
    },
  });

  const rejectRequestMutation = useMutation({
    mutationFn: async ({
      requestId,
      senderId,
      notifId,
    }: {
      requestId?: string;
      senderId?: string;
      notifId: string;
    }) => {
      let targetReqId = requestId;
      if (!targetReqId && senderId) {
        try {
          const incoming = await getConnectionRequests("incoming", "PENDING", 1, 100);
          const matched = incoming.data.find(
            (r) => r.sender_id === senderId || r.sender?.id === senderId
          );
          if (matched) targetReqId = matched.id;
        } catch (e) {}
      }

      if (targetReqId) {
        try {
          await rejectConnectionRequest(targetReqId);
        } catch (e) {}
      }
      await markNotificationRead(notifId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      queryClient.invalidateQueries({ queryKey: ["notifications-unread-count"] });
      queryClient.invalidateQueries({ queryKey: ["connection-requests"] });
      toast.info("Đã từ chối lời mời kết bạn");
    },
  });

  const allNotifications = data?.data || [];
  const unreadCount = allNotifications.filter((n) => n.status === "UNREAD").length;

  const filteredNotifications = allNotifications.filter((notif) => {
    if (activeTab === "unread") return notif.status === "UNREAD";
    if (activeTab === "requests") return notif.type === "CONNECTION_REQUEST";
    if (activeTab === "matching") {
      return (
        notif.type === "MATCH_SUGGESTION" ||
        notif.type === "CONNECTION_RECOMMENDATION" ||
        notif.type === "RECOMMENDATION"
      );
    }
    return true;
  });

  const handleCardClick = (notif: any) => {
    if (notif.status === "UNREAD") {
      markAsReadMutation.mutate(notif.id);
    }
    if (notif.type === "CONNECTION_REQUEST") {
      router.push("/connections");
    } else if (
      notif.type === "MATCH_SUGGESTION" ||
      notif.type === "CONNECTION_RECOMMENDATION" ||
      notif.type === "RECOMMENDATION"
    ) {
      router.push("/connections?tab=matchmaker");
    } else if (notif.type === "CONNECTION_ACCEPTED" || notif.type === "NEW_MESSAGE") {
      router.push("/chats");
    }
  };

  return (
    <main className="flex flex-1 flex-col overflow-hidden bg-slate-50">
      {/* Header */}
      <header className="border-b border-slate-200/80 bg-white px-6 py-5 md:px-10">
        <div className="mx-auto max-w-4xl flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="flex items-center gap-2.5">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
                <Bell size={20} />
              </div>
              <h1 className="text-xl font-bold text-slate-800">Thông báo</h1>
              {unreadCount > 0 && (
                <Badge className="bg-red-500 text-white hover:bg-red-600 text-xs font-semibold px-2 py-0.5 rounded-full">
                  {unreadCount} mới
                </Badge>
              )}
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Cập nhật các hoạt động mới, lời mời kết bạn và gợi ý matching từ AI
            </p>
          </div>

          {allNotifications.length > 0 && unreadCount > 0 && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => markAllReadMutation.mutate()}
              disabled={markAllReadMutation.isPending}
              className="rounded-xl border-slate-200 text-xs font-medium text-slate-600 hover:text-blue-600 hover:bg-blue-50/50 shadow-xs"
            >
              <CheckCheck size={14} className="mr-1.5 text-blue-500" />
              Đánh dấu tất cả đã đọc
            </Button>
          )}
        </div>

        {/* Tab Filters */}
        <div className="mx-auto max-w-4xl mt-5 flex flex-wrap items-center gap-2 border-t border-slate-100 pt-3">
          <button
            type="button"
            onClick={() => setActiveTab("all")}
            className={cn(
              "rounded-xl px-3.5 py-1.5 text-xs font-semibold transition-all cursor-pointer",
              activeTab === "all"
                ? "bg-blue-600 text-white shadow-sm"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200/80"
            )}
          >
            Tất cả ({allNotifications.length})
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("unread")}
            className={cn(
              "rounded-xl px-3.5 py-1.5 text-xs font-semibold transition-all cursor-pointer",
              activeTab === "unread"
                ? "bg-blue-600 text-white shadow-sm"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200/80"
            )}
          >
            Chưa đọc ({unreadCount})
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("requests")}
            className={cn(
              "rounded-xl px-3.5 py-1.5 text-xs font-semibold transition-all cursor-pointer flex items-center gap-1.5",
              activeTab === "requests"
                ? "bg-blue-600 text-white shadow-sm"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200/80"
            )}
          >
            <UserPlus size={13} />
            Lời mời kết bạn
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("matching")}
            className={cn(
              "rounded-xl px-3.5 py-1.5 text-xs font-semibold transition-all cursor-pointer flex items-center gap-1.5",
              activeTab === "matching"
                ? "bg-blue-600 text-white shadow-sm"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200/80"
            )}
          >
            <Sparkles size={13} />
            Gợi ý AI Matching
          </button>
        </div>
      </header>

      {/* Main Content List */}
      <div className="flex-1 overflow-y-auto p-4 md:p-8">
        <div className="mx-auto max-w-4xl space-y-3.5">
          {isLoading ? (
            <div className="space-y-3">
              {[1, 2, 3, 4].map((i) => (
                <div
                  key={i}
                  className="h-24 rounded-2xl bg-white border border-slate-100 animate-pulse shadow-xs"
                />
              ))}
            </div>
          ) : filteredNotifications.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-20 text-center rounded-3xl bg-white border border-dashed border-slate-200 p-8 shadow-xs">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-50 text-slate-300 mb-3.5">
                <Bell size={28} />
              </div>
              <h3 className="text-base font-bold text-slate-800">Không có thông báo nào</h3>
              <p className="text-xs text-slate-500 max-w-sm mt-1">
                {activeTab === "unread"
                  ? "Bạn đã đọc hết các thông báo."
                  : activeTab === "requests"
                  ? "Hiện tại không có lời mời kết bạn nào đang chờ."
                  : activeTab === "matching"
                  ? "Chưa có gợi ý matching mới từ AI. Hãy thử trò chuyện thêm để AI nhận diện mối quan tâm của bạn."
                  : "Các thông báo và tương tác mới sẽ xuất hiện tại đây."}
              </p>
            </div>
          ) : (
            filteredNotifications.map((notif) => {
              const isUnread = notif.status === "UNREAD";
              const isRequest = notif.type === "CONNECTION_REQUEST";
              const isMatching =
                notif.type === "MATCH_SUGGESTION" ||
                notif.type === "CONNECTION_RECOMMENDATION" ||
                notif.type === "RECOMMENDATION";
              const isAccepted = notif.type === "CONNECTION_ACCEPTED";
              const notifData = notif.data || {};

              return (
                <div
                  key={notif.id}
                  onClick={() => handleCardClick(notif)}
                  className={cn(
                    "group relative rounded-2xl border p-4 md:p-5 transition-all duration-200 cursor-pointer shadow-xs",
                    isUnread
                      ? "border-blue-200 bg-blue-50/40 hover:bg-blue-50/70"
                      : "border-slate-200/80 bg-white hover:border-blue-200 hover:shadow-sm"
                  )}
                >
                  <div className="flex items-start gap-4">
                    {/* Left Icon / Avatar */}
                    {isRequest ? (
                      <div className="relative shrink-0">
                        <Avatar className="h-11 w-11 border border-blue-200">
                          {notifData.sender_avatar && (
                            <AvatarImage
                              src={notifData.sender_avatar}
                              alt={notifData.sender_name || "Sender"}
                            />
                          )}
                          <AvatarFallback className="bg-blue-100 text-blue-700 font-bold text-sm">
                            {(notifData.sender_name || "U")[0].toUpperCase()}
                          </AvatarFallback>
                        </Avatar>
                        <span className="absolute -bottom-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-blue-600 text-white shadow-xs">
                          <UserPlus size={11} />
                        </span>
                      </div>
                    ) : isMatching ? (
                      <div className="relative shrink-0">
                        <Avatar className="h-11 w-11 border border-purple-200">
                          {notifData.target_avatar && (
                            <AvatarImage
                              src={notifData.target_avatar}
                              alt={notifData.target_name || "Match"}
                            />
                          )}
                          <AvatarFallback className="bg-purple-100 text-purple-700 font-bold text-sm">
                            <Sparkles size={16} />
                          </AvatarFallback>
                        </Avatar>
                        <span className="absolute -bottom-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-purple-600 text-white shadow-xs">
                          <Sparkles size={11} />
                        </span>
                      </div>
                    ) : isAccepted ? (
                      <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-green-100 text-green-600 font-bold">
                        <CheckCircle2 size={22} />
                      </div>
                    ) : (
                      <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-slate-100 text-slate-500">
                        <Bell size={20} />
                      </div>
                    )}

                    {/* Content Section */}
                    <div className="flex-1 min-w-0 space-y-1.5">
                      <div className="flex items-center justify-between gap-2">
                        <div className="flex items-center gap-2 flex-wrap">
                          <h4
                            className={cn(
                              "text-sm font-bold truncate",
                              isUnread ? "text-slate-900" : "text-slate-700"
                            )}
                          >
                            {notif.title}
                          </h4>

                          {isMatching && notifData.match_score && (
                            <Badge className="bg-emerald-50 text-emerald-700 border-emerald-200 hover:bg-emerald-100 text-[10px] font-bold px-2 py-0.2 shadow-none">
                              {notifData.match_score}% Tương thích
                            </Badge>
                          )}

                          {isUnread && (
                            <span className="h-2 w-2 rounded-full bg-blue-500 shrink-0" />
                          )}
                        </div>

                        <span className="shrink-0 text-[11px] text-slate-400 font-medium">
                          {getRelativeTime(notif.created_at)}
                        </span>
                      </div>

                      {/* Notification Body */}
                      <p className="text-xs leading-relaxed text-slate-600">
                        {notif.content}
                      </p>

                      {/* Extra Sub-info for Request or Match */}
                      {isRequest &&
                        (notifData.sender_profession || notifData.sender_company) && (
                          <div className="flex items-center gap-2 text-[11px] text-slate-500 pt-0.5">
                            {notifData.sender_profession && (
                              <span className="font-medium text-slate-700">
                                {notifData.sender_profession}
                              </span>
                            )}
                            {notifData.sender_profession &&
                              notifData.sender_company && <span>•</span>}
                            {notifData.sender_company && (
                              <span>{notifData.sender_company}</span>
                            )}
                          </div>
                        )}

                      {isMatching &&
                        (notifData.target_name || notifData.target_profession) && (
                          <div className="flex items-center gap-2 text-[11px] text-slate-500 pt-0.5">
                            {notifData.target_name && (
                              <span className="font-semibold text-slate-800">
                                {notifData.target_name}
                              </span>
                            )}
                            {notifData.target_name &&
                              notifData.target_profession && <span>•</span>}
                            {notifData.target_profession && (
                              <span>{notifData.target_profession}</span>
                            )}
                            {notifData.target_location && (
                              <>
                                <span>•</span>
                                <span>{notifData.target_location}</span>
                              </>
                            )}
                          </div>
                        )}

                      {/* Action Buttons Bar */}
                      <div
                        className="pt-2 flex items-center gap-2 flex-wrap"
                        onClick={(e) => e.stopPropagation()}
                      >
                        {isRequest && (
                          <>
                            <Button
                              size="xs"
                              variant="default"
                              onClick={() =>
                                acceptRequestMutation.mutate({
                                  requestId: notifData.request_id,
                                  senderId: notifData.sender_id,
                                  notifId: notif.id,
                                })
                              }
                              disabled={acceptRequestMutation.isPending}
                              className="rounded-lg bg-blue-600 hover:bg-blue-700 text-xs font-semibold px-3 py-1.5 shadow-xs cursor-pointer"
                            >
                              <UserCheck size={13} className="mr-1.5" />
                              {acceptRequestMutation.isPending ? "Đang xử lý..." : "Chấp nhận"}
                            </Button>
                            <Button
                              size="xs"
                              variant="outline"
                              onClick={() =>
                                rejectRequestMutation.mutate({
                                  requestId: notifData.request_id,
                                  senderId: notifData.sender_id,
                                  notifId: notif.id,
                                })
                              }
                              disabled={rejectRequestMutation.isPending}
                              className="rounded-lg border-slate-200 text-slate-600 hover:text-red-600 hover:bg-red-50 text-xs font-semibold px-3 py-1.5 cursor-pointer"
                            >
                              <X size={13} className="mr-1.5" />
                              Từ chối
                            </Button>
                          </>
                        )}

                        {isMatching && (
                          <Button
                            size="xs"
                            variant="secondary"
                            onClick={() => {
                              if (isUnread) markAsReadMutation.mutate(notif.id);
                              router.push("/connections?tab=matchmaker");
                            }}
                            className="rounded-lg bg-purple-50 hover:bg-purple-100 text-purple-700 border border-purple-200 text-xs font-semibold px-3 py-1.5 shadow-xs cursor-pointer"
                          >
                            <Sparkles size={13} className="mr-1.5 text-purple-600" />
                            Xem gợi ý & Kết nối
                          </Button>
                        )}

                        {isAccepted && (
                          <Button
                            size="xs"
                            variant="outline"
                            onClick={() => {
                              if (isUnread) markAsReadMutation.mutate(notif.id);
                              router.push("/chats");
                            }}
                            className="rounded-lg border-green-200 bg-green-50/50 hover:bg-green-100 text-green-700 text-xs font-semibold px-3 py-1.5 shadow-xs cursor-pointer"
                          >
                            <MessageSquare size={13} className="mr-1.5 text-green-600" />
                            Mở cuộc trò chuyện
                          </Button>
                        )}

                        <Button
                          size="xs"
                          variant="ghost"
                          onClick={() => deleteMutation.mutate(notif.id)}
                          disabled={deleteMutation.isPending}
                          className="h-7 text-[11px] px-2 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 ml-auto cursor-pointer"
                        >
                          <Trash2 size={12} className="mr-1" />
                          Xóa
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </main>
  );
}
