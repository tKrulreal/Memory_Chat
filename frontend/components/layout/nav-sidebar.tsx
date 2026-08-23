"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import { MessageCircle, Users, Settings, LogOut, Sparkles, Box, Bell } from "lucide-react";
import { useAuthStore } from "@/lib/stores/auth-store";
import { useAISettings } from "@/hooks/use-ai-settings";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

const NAV_ITEMS = [
  { href: "/chats", label: "Chats", icon: MessageCircle },
  { href: "/connections", label: "Connections", icon: Users },
  { href: "/ai-hub", label: "AI Hub", icon: Box },
  { href: "/copilot", label: "Copilot", icon: Sparkles },
  { href: "/notifications", label: "Notifications", icon: Bell },
] as const;

export function NavSidebar() {
  const pathname = usePathname();
  const user = useAuthStore((s) => s.user);
  const { features } = useAISettings();

  const initials =
    user?.full_name?.split(" ").map((p) => p[0]).join("").slice(0, 2).toUpperCase() ||
    user?.email?.[0].toUpperCase();

  const visibleNavItems = NAV_ITEMS.filter((item) => {
    if (item.href === "/copilot" && !features.copilot) return false;
    return true;
  });

  // Determine if a path is active
  const isActive = (href: string) => {
    if (href === "/chats") {
      return pathname === "/" || pathname?.startsWith("/chats");
    }
    return pathname?.startsWith(href);
  };

  return (
    <div className="relative h-full w-[72px] shrink-0 z-50">
      <aside
        className="absolute top-0 left-0 flex h-full w-[72px] hover:w-[220px] overflow-hidden flex-col group transition-all duration-300 shadow-2xl"
        style={{ backgroundColor: "#1e293b" }}
      >
        {/* Logo Header */}
      <div className="flex h-16 shrink-0 items-center border-b border-slate-700 px-4">
        <div className="flex items-center gap-3 w-[188px]">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-blue-500 shadow-sm">
            <Sparkles size={20} className="text-white" />
          </div>
          <span className="truncate font-bold text-white opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            MemoryChat
          </span>
        </div>
      </div>

      {/* Main Nav */}
      <div className="flex-1 space-y-2 overflow-y-auto overflow-x-hidden p-3 scrollbar-thin">
        {visibleNavItems.map(({ href, label, icon: Icon }) => {
          const active = isActive(href);
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 rounded-xl p-3 text-sm transition-colors w-[196px]",
                active ? "bg-blue-600/10" : "hover:bg-slate-800/50"
              )}
            >
              <div className="flex shrink-0 items-center justify-center">
                <Icon
                  size={22}
                  className={cn("transition-colors", active ? "text-blue-400" : "text-slate-400 group-hover:text-white")}
                />
              </div>
              <span
                className={cn(
                  "truncate whitespace-nowrap transition-opacity duration-200 opacity-0 group-hover:opacity-100",
                  active ? "text-blue-400 font-semibold" : "text-slate-300 group-hover:text-white"
                )}
              >
                {label}
              </span>
            </Link>
          );
        })}
      </div>

      {/* Bottom Section: Settings & User */}
      <div className="mt-auto border-t border-slate-700 p-3 space-y-2 shrink-0">
        {/* Settings */}
        <Link
          href="/settings"
          className={cn(
            "flex items-center gap-3 rounded-xl p-3 text-sm transition-colors w-[196px]",
            isActive("/settings") ? "bg-blue-600/10" : "hover:bg-slate-800/50"
          )}
        >
          <div className="flex shrink-0 items-center justify-center">
            <Settings size={22} className={cn("transition-colors", isActive("/settings") ? "text-blue-400" : "text-slate-400 group-hover:text-white")} />
          </div>
          <span className={cn(
            "truncate transition-opacity duration-200 opacity-0 group-hover:opacity-100",
            isActive("/settings") ? "text-blue-400 font-semibold" : "text-slate-300 group-hover:text-white"
          )}>
            Settings
          </span>
        </Link>

        {/* Logout */}
        <Button variant="ghost"
          onClick={async () => {
            await fetch("/api/auth/logout", { method: "POST" });
            useAuthStore.getState().setUser(null);
            window.location.href = "/login";
          }}
          className="flex w-[196px] items-center justify-start gap-3 rounded-xl p-3 text-sm transition-colors hover:bg-red-500/10 h-auto font-normal"
        >
          <div className="flex shrink-0 items-center justify-center">
            <LogOut size={22} className="text-slate-400 transition-colors group-hover:text-red-400" />
          </div>
          <span className="truncate text-slate-300 transition-colors group-hover:text-red-400 transition-opacity duration-200 opacity-0 group-hover:opacity-100">
            Logout
          </span>
        </Button>

        {/* User Info */}
        {user && (
          <div className="mt-2 flex items-center gap-3 rounded-xl bg-slate-800 p-3 w-[196px]">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-blue-500/20 text-sm font-bold text-blue-400">
              {initials ?? "U"}
            </div>
            <div className="min-w-0 flex-1 transition-opacity duration-200 opacity-0 group-hover:opacity-100">
              <p className="truncate text-sm font-semibold text-white">{user.full_name}</p>
              <p className="truncate text-[11px] text-slate-400 leading-tight mt-0.5">{user.email}</p>
            </div>
          </div>
        )}
      </div>
    </aside>
    </div>
  );
}
