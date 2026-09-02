"use client";

import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { getSettings } from "@/lib/api/settings";
import { useAuthStore } from "@/lib/stores/auth-store";
import { applyThemePreferences } from "@/lib/theme";

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

    applyThemePreferences(settings);
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
    const handler = () => {
      if ((settings.theme || "system") === "system") applyThemePreferences(settings);
    };
    mediaQuery.addEventListener("change", handler);

    return () => {
      mediaQuery.removeEventListener("change", handler);
    };
  }, [settings]);

  return <>{children}</>;
}
