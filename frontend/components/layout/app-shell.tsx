"use client";

import { NavSidebar } from "@/components/layout/nav-sidebar";
import { ChatListPanel } from "@/components/layout/chat-list-panel";
import { ChatWindow } from "@/components/layout/chat-window";
import { InfoPanel } from "@/components/layout/info-panel";
import { CopilotDrawer } from "@/components/ai/copilot-drawer";

type AppShellProps = {
  children?: React.ReactNode;
};

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="flex h-screen w-full overflow-hidden bg-app">
      <NavSidebar />
      <ChatListPanel />
      {children ?? <ChatWindow />}
      <InfoPanel />
      <CopilotDrawer />
    </div>
  );
}
