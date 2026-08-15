"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";
import { Toaster } from "sonner";
import { AuthBootstrap } from "./auth/auth-bootstrap";
import { WSBootstrap } from "./ws/ws-bootstrap";

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 30_000,
            retry: 1,
          },
        },
      }),
  );

  return (
    <QueryClientProvider client={queryClient}>
      <AuthBootstrap>
        <WSBootstrap>
          {children}
          <Toaster theme="dark" position="top-right" />
        </WSBootstrap>
      </AuthBootstrap>
    </QueryClientProvider>
  );
}
