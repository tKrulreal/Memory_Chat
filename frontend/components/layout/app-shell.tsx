"use client";

import { usePathname, useRouter } from "next/navigation";
import { NavSidebar } from "@/components/layout/nav-sidebar";
import { ChatListPanel } from "@/components/layout/chat-list-panel";
import { ChatWindow } from "@/components/layout/chat-window";
import { InfoPanel } from "@/components/layout/info-panel";
import { CopilotDrawer } from "@/components/ai/copilot-drawer";
import { useAISettings } from "@/hooks/use-ai-settings";
import { useEffect } from "react";
import { toast } from "sonner";
import { useQuery } from "@tanstack/react-query";
import { getConnectionRecommendations } from "@/lib/api/recommendations";
import { getConnectionRequests } from "@/lib/api/connection-requests";
import { useAuthStore } from "@/lib/stores/auth-store";

type AppShellProps = {
  children?: React.ReactNode;
};

export function AppShell({ children }: AppShellProps) {
  const pathname = usePathname();
  const isChatsPage = pathname === "/" || pathname?.startsWith("/chats");

  const { features } = useAISettings();
  const user = useAuthStore((s) => s.user);

  const { data: recommendations } = useQuery({
    queryKey: ["recommendations", "PENDING", 1],
    queryFn: () => getConnectionRecommendations("PENDING", 1),
    enabled: !!user && features.recommendation, // only check if logged in and feature enabled
  });

  const { data: incomingRequests } = useQuery({
    queryKey: ["connection-requests", "incoming", "PENDING", 1],
    queryFn: () => getConnectionRequests("incoming", "PENDING", 1, 3),
    enabled: !!user,
  });

  const router = useRouter();

  useEffect(() => {
    if (incomingRequests && incomingRequests.data && incomingRequests.data.length > 0) {
      incomingRequests.data.forEach((req) => {
        const name = req.sender?.full_name || req.sender?.email || "Một người mới";
        toast.info(`Lời mời kết bạn mới`, {
          description: `${name} đã gửi cho bạn một lời mời kết bạn.`,
          action: {
            label: "Xem ngay",
            onClick: () => {
              router.push("/connections?tab=requests");
            }
          },
          duration: 8000,
        });
      });
    }
  }, [incomingRequests, router]);

  useEffect(() => {
    if (recommendations && recommendations.length > 0) {
      recommendations.slice(0, 3).forEach((rec) => {
        const name = rec.target_user_name || "Một người mới";
        toast.info(`Gợi ý kết bạn: ${name}`, {
          description: rec.reason,
          action: {
            label: "Xem ngay",
            onClick: () => {
              if (rec.target_user_email) {
                // Not ideal to pass search through tab URL, but keeping the intent
                router.push(`/connections?tab=matchmaker&search=${encodeURIComponent(rec.target_user_email)}`);
              } else {
                router.push("/connections?tab=matchmaker");
              }
            }
          },
          duration: 8000,
        });
      });
    }
  }, [recommendations, router]);

  return (
    <div className="app-shell">
      <NavSidebar />
      {isChatsPage && <ChatListPanel />}
      <main className="page-container flex-1 overflow-hidden">
        {children ?? <ChatWindow />}
      </main>
      {isChatsPage && <InfoPanel />}
      {features.copilot && <CopilotDrawer />}
    </div>
  );
}

