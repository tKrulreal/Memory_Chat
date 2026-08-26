"use client";

import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { getSettings } from "@/lib/api/settings";
import { useAuthStore } from "@/lib/stores/auth-store";

export function ThemeBootstrap({ children }: { children: React.ReactNode }) {
  const user = useAuthStore((s) => s.user);

  const { data: settings } = useQuery({
    queryKey: ["my-settings"],
    queryFn: getSettings,
    enabled: !!user,
    staleTime: 60_000,
  });

  useEffect(() => {
    if (!settings) return;

    // 1. Apply Theme
    const root = document.documentElement;
    const theme = settings.theme || "system";

    const applyThemeClass = (isDark: boolean) => {
      if (isDark) {
        root.classList.add("dark");
      } else {
        root.classList.remove("dark");
      }
    };

    if (theme === "dark") {
      applyThemeClass(true);
    } else if (theme === "light") {
      applyThemeClass(false);
    } else {
      // System mode
      const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
      applyThemeClass(mediaQuery.matches);

      const handler = (e: MediaQueryListEvent) => applyThemeClass(e.matches);
      mediaQuery.addEventListener("change", handler);
      return () => mediaQuery.removeEventListener("change", handler);
    }

    // 2. Apply Font Size
    const fontSize = settings.font_size || "medium";
    if (fontSize === "small") {
      root.style.fontSize = "13px";
    } else if (fontSize === "large") {
      root.style.fontSize = "16px";
    } else {
      root.style.fontSize = "14px";
    }

    // 3. Apply Accent Color Data Attribute
    const accent = settings.accent_color || "blue";
    root.setAttribute("data-accent-color", accent);
  }, [settings]);

  return <>{children}</>;
}
