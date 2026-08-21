"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Bell,
  Brain,
  ChevronLeft,
  ChevronRight,
  LogOut,
  MessageSquare,
  Settings,
  Sparkles,
  Star,
  Users,
} from "lucide-react";
import { useAuthStore } from "@/lib/stores/auth-store";
import { useUIStore } from "@/lib/stores/ui-store";
import { cn } from "@/lib/utils";
import { useAISettings } from "@/hooks/use-ai-settings";

const NAV_ITEMS = [
  { href: "/chats", label: "Chats", icon: MessageSquare },
  { href: "/connections", label: "Connections", icon: Users },
  { href: "/ai-hub", label: "AI Hub", icon: Brain },
  { href: "/recommendations", label: "Recommendations", icon: Star },
  { href: "/copilot", label: "Copilot", icon: Sparkles },
  { href: "/notifications", label: "Notifications", icon: Bell },
] as const;

export function NavSidebar() {
  const pathname = usePathname();
  const user = useAuthStore((s) => s.user);
  const navCollapsed = useUIStore((s) => s.navCollapsed);
  const toggleNav = useUIStore((s) => s.toggleNav);

  const initials = user?.full_name
    ?.split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  const { features } = useAISettings();
  const visibleNavItems = NAV_ITEMS.filter((item) => {
    if (item.href === "/copilot" && !features.copilot) return false;
    if (item.href === "/recommendations" && !features.recommendation) return false;
    return true;
  });

  return (
    <>
      <aside
        className={cn(
          "flex h-full shrink-0 flex-col border-r border-subtle bg-surface transition-[width] duration-200",
          navCollapsed ? "w-[var(--width-nav-collapsed)]" : "w-nav",
        )}
      >
        <div className="flex items-center justify-between gap-2 border-b border-subtle p-4">
          {!navCollapsed && (
            <div>
              <p className="text-sm font-semibold text-accent">MemoryChat</p>
              <p className="text-xs text-secondary">Your second brain</p>
            </div>
          )}
          <button
            type="button"
            onClick={toggleNav}
            className="rounded-button p-1.5 text-secondary hover:bg-elevated hover:text-primary"
            aria-label={navCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {navCollapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
          </button>
        </div>


        <nav className="flex-1 space-y-1 px-2 py-1">
          {visibleNavItems.map(({ href, label, icon: Icon }) => {
            const active = pathname.startsWith(href);
            return (
              <Link
                key={href}
                href={href}
                className={cn(
                  "flex items-center gap-3 rounded-button px-3 py-2.5 text-sm transition-colors",
                  active
                    ? "bg-accent/15 text-accent"
                    : "text-secondary hover:bg-elevated hover:text-primary",
                  navCollapsed && "justify-center px-2",
                )}
                title={navCollapsed ? label : undefined}
              >
                <Icon size={18} />
                {!navCollapsed && <span>{label}</span>}
              </Link>
            );
          })}
        </nav>

        <div className="mt-auto border-t border-subtle p-3 space-y-1">
          <Link
            href="/settings"
            className="flex items-center gap-3 rounded-button px-3 py-2 text-sm text-secondary hover:bg-elevated hover:text-primary"
          >
            <Settings size={18} />
            {!navCollapsed && <span>Settings</span>}
          </Link>
          <button
            type="button"
            onClick={async () => {
              await fetch("/api/auth/logout", { method: "POST" });
              useAuthStore.getState().setUser(null);
              window.location.href = "/login";
            }}
            className="flex w-full items-center gap-3 rounded-button px-3 py-2 text-sm text-secondary hover:bg-elevated hover:text-primary"
          >
            <LogOut size={18} />
            {!navCollapsed && <span>Logout</span>}
          </button>

          {user && (
            <div
              className={cn(
                "mt-2 flex items-center gap-3 rounded-button bg-elevated p-3",
                navCollapsed && "justify-center p-2",
              )}
            >
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-accent/20 text-xs font-semibold text-accent">
                {initials ?? "U"}
              </div>
              {!navCollapsed && (
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium">{user.full_name}</p>
                  <p className="truncate text-xs text-secondary">{user.email}</p>
                </div>
              )}
            </div>
          )}
        </div>
      </aside>
    </>
  );
}
