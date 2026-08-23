"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getNotifications, markNotificationRead } from "@/lib/api/notifications";
import { Bell, Check, MessageSquare, Sparkles, UserPlus } from "lucide-react";
import { cn } from "@/lib/utils";

function getRelativeTime(dateString: string) {
  const date = new Date(dateString);
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
  
  if (diffInSeconds < 60) return "Just now";
  
  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
  
  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) return `${diffInHours}h ago`;
  
  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 7) return `${diffInDays}d ago`;
  
  return date.toLocaleDateString();
}

import { useRouter } from "next/navigation";

export default function NotificationsPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ["notifications"],
    queryFn: () => getNotifications(1, 50),
  });

  const markAsReadMutation = useMutation({
    mutationFn: (id: string) => markNotificationRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });

  const handleNotificationClick = (notif: any) => {
    if (notif.status === "UNREAD") {
      markAsReadMutation.mutate(notif.id);
    }
    
    switch (notif.type) {
      case "CONNECTION_REQUEST":
        router.push("/connections");
        break;
      case "MATCH_RECOMMENDATION":
      case "CONNECTION_RECOMMENDATION":
      case "RECOMMENDATION":
      case "MATCH_SUGGESTION":
        router.push("/connections?tab=matchmaker");
        break;
      case "NEW_MESSAGE":
        router.push("/chats");
        break;
      default:
        break;
    }
  };

  const getIcon = (type: string) => {
    switch (type) {
      case "CONNECTION_REQUEST":
        return <UserPlus className="h-5 w-5 text-blue-500" />;
      case "MATCH_RECOMMENDATION":
      case "CONNECTION_RECOMMENDATION":
      case "RECOMMENDATION":
      case "MATCH_SUGGESTION":
        return <Sparkles className="h-5 w-5 text-blue-600" />;
      case "NEW_MESSAGE":
        return <MessageSquare className="h-5 w-5 text-blue-500" />;
      default:
        return <Bell className="h-5 w-5 text-slate-400" />;
    }
  };

  const notifications = data?.data || [];

  return (
    <main className="flex flex-1 flex-col overflow-hidden bg-slate-50">
      <header className="border-b border-gray-200 bg-white px-8 py-6">
        <h1 className="text-2xl font-bold text-slate-800">Notifications</h1>
        <p className="text-sm text-slate-500 mt-1">Stay updated with your latest activities</p>
      </header>

      <div className="flex-1 overflow-y-auto p-8">
        <div className="mx-auto max-w-3xl space-y-4">
          {isLoading ? (
            <div className="flex flex-col gap-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-24 rounded-xl bg-white animate-pulse shadow-sm" />
              ))}
            </div>
          ) : notifications.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-20 text-center">
              <Bell className="mb-4 h-12 w-12 text-slate-300" />
              <h3 className="text-lg font-medium text-slate-800">No notifications yet</h3>
              <p className="text-sm text-slate-500">When you get notifications, they&apos;ll show up here.</p>
            </div>
          ) : (
            notifications.map((notif) => (
              <div
                key={notif.id}
                onClick={() => handleNotificationClick(notif)}
                className={cn(
                  "group flex items-start gap-4 rounded-xl border p-4 transition-all cursor-pointer",
                  notif.status === "UNREAD"
                    ? "border-blue-200 bg-blue-50"
                    : "border-gray-200 bg-white hover:border-blue-200 shadow-sm"
                )}
              >
                <div className="mt-1 shrink-0 rounded-full bg-gray-100 p-2">
                  {getIcon(notif.type)}
                </div>

                <div className="flex-1 space-y-1">
                  <div className="flex items-start justify-between gap-2">
                    <h4 className={cn(
                      "font-semibold",
                      notif.status === "UNREAD" ? "text-slate-800" : "text-slate-600"
                    )}>
                      {notif.title}
                    </h4>
                    <span className="shrink-0 text-xs text-slate-400">
                      {notif.created_at ? getRelativeTime(notif.created_at) : ""}
                    </span>
                  </div>
                  <p className={cn(
                    "text-sm leading-relaxed",
                    notif.status === "UNREAD" ? "text-slate-700" : "text-slate-500"
                  )}>
                    {notif.content}
                  </p>
                </div>

                {notif.status === "UNREAD" && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      markAsReadMutation.mutate(notif.id);
                    }}
                    disabled={markAsReadMutation.isPending}
                    className="shrink-0 rounded-full p-2 text-blue-600 opacity-0 hover:bg-blue-100 focus:opacity-100 group-hover:opacity-100 transition-all disabled:opacity-50"
                    title="Mark as read"
                  >
                    <Check className="h-5 w-5" />
                  </button>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </main>
  );
}
