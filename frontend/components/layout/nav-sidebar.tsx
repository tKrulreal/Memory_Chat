"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import { MessageCircle, Users, Settings, LogOut, Sparkles, Box, Bell, User as UserIcon } from "lucide-react";
import { useAuthStore } from "@/lib/stores/auth-store";
import { useAISettings } from "@/hooks/use-ai-settings";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

import { useQuery } from "@tanstack/react-query";
import { getUnreadNotificationsCount } from "@/lib/api/notifications";
import { getSettings } from "@/lib/api/settings";
import { getLanguage, translate, type TranslationKey } from "@/lib/i18n";

const NAV_ITEMS = [
  { href: "/chats", labelKey: "chats", icon: MessageCircle },
  { href: "/connections", labelKey: "connections", icon: Users },
  { href: "/ai-hub", labelKey: null, icon: Box },
  { href: "/copilot", labelKey: "copilot", icon: Sparkles },
  { href: "/notifications", labelKey: "navNotifications", icon: Bell },
] as const;

export function NavSidebar() {
  const pathname = usePathname();
  const user = useAuthStore((s) => s.user);
  const { features } = useAISettings();
  const { data: preferences } = useQuery({
    queryKey: ["my-settings"],
    queryFn: getSettings,
    enabled: !!user,
  });
  const language = getLanguage(preferences?.language);
  const t = (key: TranslationKey) => translate(language, key);

  const { data: unreadData } = useQuery({
    queryKey: ["notifications-unread-count"],
    queryFn: getUnreadNotificationsCount,
    enabled: !!user,
    refetchInterval: 30000,
  });
  const unreadCount = unreadData?.unread_count || 0;

  const initials =
    user?.full_name?.split(" ").map((p) => p[0]).join("").slice(0, 2).toUpperCase() ||
    user?.email?.[0]?.toUpperCase() ||
    "U";

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
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-accent shadow-sm">
              <Sparkles size={20} className="text-white" />
            </div>
            <span className="truncate font-bold text-white opacity-0 group-hover:opacity-100 transition-opacity duration-200">
              MemoryChat
            </span>
          </div>
        </div>

        {/* Main Nav */}
        <div className="flex-1 space-y-2 overflow-y-auto overflow-x-hidden p-3 scrollbar-thin">
          {visibleNavItems.map(({ href, labelKey, icon: Icon }) => {
            const active = isActive(href);
            const isNotif = href === "/notifications";
            const label = labelKey ? t(labelKey) : "AI Hub";
            return (
              <Link
                key={href}
                href={href}
                className={cn(
                  "flex items-center gap-3 rounded-xl p-3 text-sm transition-colors w-[196px] relative",
                  active ? "bg-accent/15" : "hover:bg-slate-800/50"
                )}
              >
                <div className="flex shrink-0 items-center justify-center relative">
                  <Icon
                    size={22}
                    className={cn("transition-colors", active ? "text-accent" : "text-slate-400 group-hover:text-white")}
                  />
                  {isNotif && unreadCount > 0 && (
                    <span className="absolute -top-1 -right-1 h-2.5 w-2.5 rounded-full bg-red-500 ring-2 ring-slate-800" />
                  )}
                </div>
                <span
                  className={cn(
                    "truncate whitespace-nowrap transition-opacity duration-200 opacity-0 group-hover:opacity-100 flex items-center justify-between flex-1",
                    active ? "text-accent font-semibold" : "text-slate-300 group-hover:text-white"
                  )}
                >
                  <span>{label}</span>
                  {isNotif && unreadCount > 0 && (
                    <span className="ml-auto rounded-full bg-red-500 px-1.5 py-0.2 text-[10px] font-bold text-white">
                      {unreadCount > 99 ? "99+" : unreadCount}
                    </span>
                  )}
                </span>
              </Link>
            );
          })}
        </div>

        {/* Bottom Section: Settings, Logout & User Profile */}
        <div className="mt-auto border-t border-slate-700 p-3 space-y-2 shrink-0">
          {/* Settings Button -> Opens New Settings Page */}
          <Link
            href="/settings"
            title={t("systemSettingsTitle")}
            className={cn(
              "flex items-center gap-3 rounded-xl p-3 text-sm transition-colors w-[196px]",
              isActive("/settings") ? "bg-accent/15 ring-1 ring-accent/40" : "hover:bg-slate-800/50"
            )}
          >
            <div className="flex shrink-0 items-center justify-center">
              <Settings size={22} className={cn("transition-colors", isActive("/settings") ? "text-accent" : "text-slate-400 group-hover:text-white")} />
            </div>
            <span className={cn(
              "truncate transition-opacity duration-200 opacity-0 group-hover:opacity-100",
              isActive("/settings") ? "text-accent font-semibold" : "text-slate-300 group-hover:text-white"
            )}>
              {t("navSettings")}
            </span>
          </Link>

          {/* Logout Button */}
          <Button
            variant="ghost"
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
              {t("logout")}
            </span>
          </Button>

          {/* Bottom User Info Card & Icon -> Opens Profile Page */}
          <Link
            href="/profile"
            title={t("profileTitle")}
            className={cn(
              "mt-2 flex items-center gap-3 rounded-xl p-2.5 w-[196px] cursor-pointer transition-all duration-200 border",
              isActive("/profile")
                ? "bg-accent/20 border-accent/50 text-white shadow-sm"
                : "bg-slate-800/90 border-slate-700/60 hover:bg-slate-700/80 hover:border-slate-600 text-slate-200"
            )}
          >
            <div className={cn(
              "flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-sm font-bold transition-colors",
              isActive("/profile") ? "bg-accent text-accent-foreground" : "bg-accent/20 text-accent"
            )}>
              {user ? initials : <UserIcon size={18} />}
            </div>
            <div className="min-w-0 flex-1 transition-opacity duration-200 opacity-0 group-hover:opacity-100">
              <p className="truncate text-xs font-bold text-white">
                {user?.full_name || t("profile")}
              </p>
              <p className="truncate text-[10px] text-slate-400 leading-tight mt-0.5">
                {user?.email || t("viewEditProfile")}
              </p>
            </div>
          </Link>
        </div>
      </aside>
    </div>
  );
}
