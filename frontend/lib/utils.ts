import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Parse date from backend (ensuring UTC timezone is preserved when 'Z' is omitted)
 */
export function parseServerDate(dateString: string | Date | undefined | null): Date | null {
  if (!dateString) return null;
  if (dateString instanceof Date) return isNaN(dateString.getTime()) ? null : dateString;

  let str = String(dateString).trim();
  if (str && !str.endsWith("Z") && !str.includes("+") && !/-\d{2}:\d{2}$/.test(str)) {
    if (str.includes("T")) {
      str = str + "Z";
    }
  }

  const d = new Date(str);
  if (isNaN(d.getTime())) {
    const fallback = new Date(dateString);
    return isNaN(fallback.getTime()) ? null : fallback;
  }
  return d;
}

/**
 * Format message time for message bubbles in chat window
 */
export function formatMessageTime(dateString: string | Date | undefined | null): string {
  const d = parseServerDate(dateString);
  if (!d) return "";

  return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

/**
 * Format conversation preview time for the left chat list panel
 */
export function formatChatListTime(dateString: string | Date | undefined | null, language: "vi" | "en" = "vi"): string {
  const d = parseServerDate(dateString);
  if (!d) return "";

  const now = new Date();
  const isToday = now.toDateString() === d.toDateString();

  const yesterday = new Date();
  yesterday.setDate(now.getDate() - 1);
  const isYesterday = yesterday.toDateString() === d.toDateString();

  const timeStr = d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

  if (isToday) {
    return timeStr;
  }
  if (isYesterday) {
    return language === "en" ? "Yesterday" : "Hôm qua";
  }
  const isSameYear = now.getFullYear() === d.getFullYear();
  if (isSameYear) {
    const day = String(d.getDate()).padStart(2, "0");
    const month = String(d.getMonth() + 1).padStart(2, "0");
    return `${day}/${month}`;
  }
  return d.toLocaleDateString(language === "en" ? "en-US" : "vi-VN");
}

/**
 * Get date divider label for separating message days in chat window
 */
export function getDateDividerLabel(date: Date | null, language: "vi" | "en" = "vi"): string {
  if (!date) return "";
  const now = new Date();
  if (now.toDateString() === date.toDateString()) {
    return language === "en" ? "Today" : "Hôm nay";
  }
  const yesterday = new Date();
  yesterday.setDate(now.getDate() - 1);
  if (yesterday.toDateString() === date.toDateString()) {
    return language === "en" ? "Yesterday" : "Hôm qua";
  }
  return date.toLocaleDateString(language === "en" ? "en-US" : "vi-VN", {
    weekday: "short",
    day: "numeric",
    month: "numeric",
    year: "numeric",
  });
}
