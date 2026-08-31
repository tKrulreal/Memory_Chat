"use client";

import { useQuery } from "@tanstack/react-query";
import { getSettings } from "@/lib/api/settings";
import { getLanguage, translate, type TranslationKey } from "@/lib/i18n";
import { useAuthStore } from "@/lib/stores/auth-store";

export function useLanguage() {
  const user = useAuthStore((state) => state.user);
  const { data: settings } = useQuery({
    queryKey: ["my-settings"],
    queryFn: getSettings,
    enabled: !!user,
  });
  const language = getLanguage(settings?.language);

  return {
    language,
    t: (key: TranslationKey) => translate(language, key),
  };
}
