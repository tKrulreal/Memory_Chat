"use client";

import { useEffect } from "react";
import { useAuthStore } from "@/lib/stores/auth-store";

export function AuthBootstrap({ children }: { children: React.ReactNode }) {
  const setUser = useAuthStore((s) => s.setUser);
  const setLoading = useAuthStore((s) => s.setLoading);

  useEffect(() => {
    async function loadUser() {
      try {
        const res = await fetch("/api/auth/me");
        if (res.ok) {
          const data = await res.json();
          setUser(data.user);
        } else {
          setUser(null);
          if (window.location.pathname !== "/login" && window.location.pathname !== "/register") {
            window.location.href = "/login";
          }
        }
      } catch (err) {
        setUser(null);
        if (window.location.pathname !== "/login" && window.location.pathname !== "/register") {
          window.location.href = "/login";
        }
      } finally {
        setLoading(false);
      }
    }

    loadUser();
  }, [setUser, setLoading]);

  return <>{children}</>;
}
