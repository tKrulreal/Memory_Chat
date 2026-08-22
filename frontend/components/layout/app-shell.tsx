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

  const router = useRouter();

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
                router.push(`/recommendations?search=${encodeURIComponent(rec.target_user_email)}`);
              } else {
                router.push("/recommendations");
              }
            }
          },
          duration: 8000,
        });
      });
    }
  }, [recommendations, router]);

  return (
    <div className="flex h-screen w-full overflow-hidden bg-app">
      <NavSidebar />
      {isChatsPage && <ChatListPanel />}
      {children ?? <ChatWindow />}
      {isChatsPage && <InfoPanel />}
      {features.copilot && <CopilotDrawer />}
    </div>
  );
}

