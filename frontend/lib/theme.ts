export type ThemePreferences = {
  theme?: string;
  accent_color?: string;
  font_size?: string;
  language?: string;
};

export function applyThemePreferences(preferences: ThemePreferences) {
  const root = document.documentElement;
  const theme = preferences.theme || "system";
  const isDark = theme === "dark" || (
    theme === "system" && window.matchMedia("(prefers-color-scheme: dark)").matches
  );

  root.classList.toggle("dark", isDark);
  root.style.colorScheme = isDark ? "dark" : "light";
  root.setAttribute("data-theme", isDark ? "dark" : "light");
  root.setAttribute("data-accent-color", preferences.accent_color || "blue");
  root.lang = preferences.language === "en" ? "en" : "vi";

  const fontSizes: Record<string, string> = {
    small: "13px",
    medium: "14px",
    large: "16px",
  };
  root.style.fontSize = fontSizes[preferences.font_size || "medium"];
}
