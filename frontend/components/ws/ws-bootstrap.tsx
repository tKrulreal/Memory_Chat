"use client";

import { useEffect, useRef } from "react";
import { useAuthStore } from "@/lib/stores/auth-store";
import { useUIStore } from "@/lib/stores/ui-store";
import { usePresenceStore } from "@/lib/stores/presence-store";
import { wsManager } from "@/lib/ws/manager";
import { useQueryClient, useQuery } from "@tanstack/react-query";
import type { Message, Setting } from "@/types";
import { toast } from "sonner";
import { useAISettings } from "@/hooks/use-ai-settings";
import { getSettings } from "@/lib/api/settings";

function playNotificationChime() {
  try {
    const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
    if (!AudioCtx) return;
    const ctx = new AudioCtx();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.type = "sine";
    osc.frequency.setValueAtTime(587.33, ctx.currentTime); // D5
    osc.frequency.setValueAtTime(880, ctx.currentTime + 0.08); // A5

    gain.gain.setValueAtTime(0.12, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.3);

    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.3);
  } catch {
    // Ignore audio context autoplay limitations
  }
}

export function WSBootstrap({ children }: { children: React.ReactNode }) {
  const user = useAuthStore((s) => s.user);
  const queryClient = useQueryClient();
  const { features } = useAISettings(!!user);
  const featuresRef = useRef(features);

  const { data: settings } = useQuery<Setting>({
    queryKey: ["my-settings"],
    queryFn: getSettings,
    enabled: !!user,
    staleTime: 60_000,
  });

  const settingsRef = useRef(settings);
  useEffect(() => {
    settingsRef.current = settings;
  }, [settings]);

  useEffect(() => {
    featuresRef.current = features;
  }, [features]);

  // Initial Presence Bootstrap
  useEffect(() => {
    if (!user) return;
    fetch("/api/proxy/api/v1/presence/online")
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data?.online_user_ids) {
          usePresenceStore.getState().setOnlineUsers(data.online_user_ids);
        }
      })
      .catch(() => {});
  }, [user]);

  useEffect(() => {
    if (!user) {
      wsManager.disconnect();
      return;
    }

    wsManager.connect();

    const unsubscribe = wsManager.subscribe((data) => {
      const currentSettings = settingsRef.current;

      if (data.type === "ONLINE_USERS") {
        if (Array.isArray(data.user_ids)) {
          usePresenceStore.getState().setOnlineUsers(data.user_ids);
        }
      } else if (data.type === "USER_PRESENCE") {
        if (data.user_id) {
          usePresenceStore.getState().setUserOnline(data.user_id, !!data.is_online);
        }
      } else if (data.type === "MESSAGE_READ") {
        if (data.conversation_id) {
          queryClient.setQueryData(["messages", data.conversation_id], (old: any) => {
            if (!old || !old.pages) return old;
            return {
              ...old,
              pages: old.pages.map((page: any) => ({
                ...page,
                data: page.data.map((m: Message) => {
                  if (m.sender_user_id === user.id) {
                    return { ...m, is_read: true };
                  }
                  return m;
                }),
              })),
            };
          });
        }
      } else if (data.type === "NEW_MESSAGE") {
        const message = data as Message;

        // 1. Update message list for the specific conversation (Infinite Query shape)
        queryClient.setQueryData(["messages", message.conversation_id], (old: any) => {
          if (!old || !old.pages || old.pages.length === 0) return old;
          
          const newPages = [...old.pages];
          const firstPage = { ...newPages[0] };
          
          // Check if we already have it (optimistic)
          let exists = false;
          firstPage.data = firstPage.data.map((m: Message) => {
            if (m.id === message.id || (m.client_message_id && m.client_message_id === message.client_message_id)) {
              exists = true;
              return message;
            }
            return m;
          });

          if (!exists) {
            firstPage.data = [message, ...firstPage.data].sort((a: Message, b: Message) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
          }
          
          newPages[0] = firstPage;
          return { ...old, pages: newPages };
        });

        // 2. Invalidate conversations list
        const { useConversationStore } = require("@/lib/stores/conversation-store");
        const activeId = useConversationStore.getState().activeConversationId;

        queryClient.setQueryData(["conversations"], (old: any) => {
          if (!old) return old;
          return old.map((c: any) => {
            if (c.id === message.conversation_id) {
              return { 
                ...c, 
                last_message: message.content,
                unread_count: activeId === c.id || message.sender_user_id === user.id ? 0 : (c.unread_count || 0) + 1 
              };
            }
            return c;
          });
        });
        queryClient.invalidateQueries({ queryKey: ["conversations"] });

        // 3. Audio & Notification feedback if message is from someone else
        if (message.sender_user_id !== user.id) {
          if (currentSettings?.sound_enabled !== false) {
            playNotificationChime();
          }

          if (
            currentSettings?.notifications_enabled !== false &&
            currentSettings?.notification !== false &&
            activeId !== message.conversation_id
          ) {
            const preview =
              currentSettings?.message_preview !== false
                ? message.content.length > 50
                  ? `${message.content.slice(0, 50)}...`
                  : message.content
                : "Bạn nhận được một tin nhắn mới";

            toast.info(`Tin nhắn mới: ${preview}`, {
              duration: 3500,
            });
          }
        }
        
        // 4. Invalidate AI context after a short delay
        setTimeout(() => {
          queryClient.invalidateQueries({ queryKey: ["context", message.conversation_id] });
        }, 3000);
      } else if (data.type === "MESSAGE_RECALLED") {
        if (!data.conversation_id || !data.message_id) return;
        
        queryClient.setQueryData(["messages", data.conversation_id], (old: any) => {
          if (!old || !old.pages) return old;
          
          return {
            ...old,
            pages: old.pages.map((page: any) => ({
              ...page,
              data: page.data.map((m: Message) => 
                m.id === data.message_id 
                  ? { ...m, deleted_at: data.deleted_at } 
                  : m
              )
            }))
          };
        });
      } else if (data.type === "NEW_NOTIFICATION") {
        queryClient.invalidateQueries({ queryKey: ["notifications"] });
        queryClient.invalidateQueries({ queryKey: ["notifications-unread-count"] });
        queryClient.invalidateQueries({ queryKey: ["connection-requests"] });
        queryClient.invalidateQueries({ queryKey: ["connections"] });
        queryClient.invalidateQueries({ queryKey: ["connection-recommendations"] });

        if (currentSettings?.sound_enabled !== false) {
          playNotificationChime();
        }

        const notif = data.notification;
        if (notif && currentSettings?.notifications_enabled !== false && currentSettings?.notification !== false) {
          if (notif.type === "CONNECTION_REQUEST") {
            toast.info(notif.content || "Bạn có một lời mời kết bạn mới", {
              duration: 4000,
            });
          } else if (notif.type === "MATCH_SUGGESTION" || notif.type === "CONNECTION_RECOMMENDATION") {
            toast(notif.content || "Profile của người này hợp với bạn, hãy thử kết nối", {
              duration: 4000,
            });
          } else if (notif.type === "CONNECTION_ACCEPTED") {
            toast.success(notif.content || "Lời mời kết bạn đã được chấp nhận", {
              duration: 4000,
            });
          } else {
            toast(notif.content || notif.title || "Thông báo mới", {
              duration: 4000,
            });
          }
        }
      } else if (data.type === "CONNECTION_REQUEST") {
        queryClient.invalidateQueries({ queryKey: ["connection-requests"] });
        queryClient.invalidateQueries({ queryKey: ["notifications"] });
        queryClient.invalidateQueries({ queryKey: ["notifications-unread-count"] });
      } else if (data.type === "NEW_RECOMMENDATION") {
        queryClient.invalidateQueries({ queryKey: ["connection-recommendations"] });
        queryClient.invalidateQueries({ queryKey: ["notifications"] });
        queryClient.invalidateQueries({ queryKey: ["notifications-unread-count"] });
        if (featuresRef.current.recommendation !== false && currentSettings?.notifications_enabled !== false) {
          toast("Profile của người này hợp với bạn, hãy thử kết nối", {
            duration: 4000,
          });
        }
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
      queryClient.invalidateQueries({ queryKey: ["conversations"] });
      queryClient.invalidateQueries({ queryKey: ["messages"] });
    }
  }, [connectionState, queryClient]);

  return <>{children}</>;
}
