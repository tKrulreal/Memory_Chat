"use client";

import { useEffect } from "react";
import { useAuthStore } from "@/lib/stores/auth-store";

const PUBLIC_PATHS = ["/login", "/register", "/forgot-password", "/reset-password"];

export function AuthBootstrap({ children }: { children: React.ReactNode }) {
  const setUser = useAuthStore((s) => s.setUser);
  const setLoading = useAuthStore((s) => s.setLoading);

  useEffect(() => {
    if (PUBLIC_PATHS.includes(window.location.pathname)) {
      setLoading(false);
      return;
    }

    async function loadUser() {
      try {
        const res = await fetch("/api/auth/me");
        if (res.ok) {
          const data = await res.json();
          setUser(data.user);
        } else {
          setUser(null);
          window.location.href = "/login";
        }
      } catch {
        setUser(null);
        window.location.href = "/login";
      } finally {
        setLoading(false);
      }
    }

    loadUser();
  }, [setUser, setLoading]);

  return <>{children}</>;
}
