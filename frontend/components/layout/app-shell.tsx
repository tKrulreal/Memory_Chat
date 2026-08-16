"use client";

import { usePathname } from "next/navigation";
import { NavSidebar } from "@/components/layout/nav-sidebar";
import { ChatListPanel } from "@/components/layout/chat-list-panel";
import { ChatWindow } from "@/components/layout/chat-window";
import { InfoPanel } from "@/components/layout/info-panel";
import { CopilotDrawer } from "@/components/ai/copilot-drawer";

type AppShellProps = {
  children?: React.ReactNode;
};

export function AppShell({ children }: AppShellProps) {
  const pathname = usePathname();
  const isChatsPage = pathname === "/" || pathname?.startsWith("/chats");

  return (
    <div className="flex h-screen w-full overflow-hidden bg-app">
      <NavSidebar />
      {isChatsPage && <ChatListPanel />}
      {children ?? <ChatWindow />}
      {isChatsPage && <InfoPanel />}
      <CopilotDrawer />
    </div>
  );
}

