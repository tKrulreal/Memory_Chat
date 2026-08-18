"use client";

import { useEffect } from "react";
import { useAuthStore } from "@/lib/stores/auth-store";
import { useUIStore } from "@/lib/stores/ui-store";
import { wsManager } from "@/lib/ws/manager";
import { useQueryClient } from "@tanstack/react-query";
import type { Message } from "@/types";

export function WSBootstrap({ children }: { children: React.ReactNode }) {
  const user = useAuthStore((s) => s.user);
  const queryClient = useQueryClient();

  useEffect(() => {
    if (!user) {
      wsManager.disconnect();
      return;
    }

    wsManager.connect();

    const unsubscribe = wsManager.subscribe((data) => {
      if (data.type === "NEW_MESSAGE") {
        const message = data as Message;
        // Ignore optimistic messages that we already sent 
        // Or actually, we should replace the optimistic message or just append if it's from someone else
        
        // 1. Update message list for the specific conversation
        queryClient.setQueryData(["messages", message.conversation_id], (old: any) => {
          if (!old) return old;
          
          // Check if we already have it (optimistic)
          const exists = old.data.find((m: Message) => m.id === message.id || (message.client_message_id && m.client_message_id === message.client_message_id));
          
          if (exists) {
            // Update it to remove "pending" state (it's now confirmed by the server)
            return {
              ...old,
              data: old.data.map((m: Message) => 
                (m.id === message.id || m.client_message_id === message.client_message_id) ? message : m
              ),
            };
          }

          // Otherwise append
          return {
            ...old,
            data: [message, ...old.data].sort((a: Message, b: Message) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()),
          };
        });

        // 2. Invalidate conversations list so it updates the last message preview
        queryClient.invalidateQueries({ queryKey: ["conversations"] });
        
        // 3. Invalidate AI context after a short delay to allow memory worker to process
        setTimeout(() => {
          queryClient.invalidateQueries({ queryKey: ["context", message.conversation_id] });
        }, 3000);
      } else if (data.type === "MESSAGE_RECALLED") {
        if (!data.conversation_id || !data.message_id) return;
        
        queryClient.setQueryData(["messages", data.conversation_id], (old: any) => {
          if (!old || !old.data) return old;
          
          return {
            ...old,
            data: old.data.map((m: Message) => 
              m.id === data.message_id 
                ? { ...m, deleted_at: data.deleted_at } 
                : m
            ),
          };
        });
      }
    });

    return () => {
      unsubscribe();
    };
  }, [user, queryClient]);

  // Gap recovery on reconnect
  const connectionState = useUIStore((s) => s.connectionState);
  useEffect(() => {
    if (connectionState === "connected") {
      // Invalidate to fetch missing messages and conversations when we get back online
      queryClient.invalidateQueries({ queryKey: ["conversations"] });
      queryClient.invalidateQueries({ queryKey: ["messages"] });
    }
  }, [connectionState, queryClient]);

  return <>{children}</>;
}
