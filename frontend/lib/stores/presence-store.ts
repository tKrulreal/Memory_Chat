import { create } from "zustand";

interface PresenceState {
  onlineUserIds: Set<string>;
  setUserOnline: (userId: string, isOnline: boolean) => void;
  setOnlineUsers: (userIds: string[]) => void;
  isUserOnline: (userId: string) => boolean;
}

export const usePresenceStore = create<PresenceState>((set, get) => ({
  onlineUserIds: new Set<string>(),

  setUserOnline: (userId: string, isOnline: boolean) =>
    set((state) => {
      const next = new Set(state.onlineUserIds);
      if (isOnline) {
        next.add(userId);
      } else {
        next.delete(userId);
      }
      return { onlineUserIds: next };
    }),

  setOnlineUsers: (userIds: string[]) =>
    set({ onlineUserIds: new Set(userIds) }),

  isUserOnline: (userId: string) => get().onlineUserIds.has(userId),
}));
