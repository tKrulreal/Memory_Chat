"use client";

import { create } from "zustand";

export type ConnectionState = "connected" | "reconnecting" | "offline";

type UIState = {
  navCollapsed: boolean;
  infoPanelOpen: boolean;
  copilotOpen: boolean;
  connectionState: ConnectionState;
  toggleNav: () => void;
  toggleInfoPanel: () => void;
  setInfoPanelOpen: (open: boolean) => void;
  toggleCopilot: () => void;
  setCopilotOpen: (open: boolean) => void;
  setConnectionState: (state: ConnectionState) => void;
};

export const useUIStore = create<UIState>((set) => ({
  navCollapsed: false,
  infoPanelOpen: false,
  copilotOpen: false,
  connectionState: "offline",

  toggleNav: () => set((s) => ({ navCollapsed: !s.navCollapsed })),
  toggleInfoPanel: () => set((s) => ({ infoPanelOpen: !s.infoPanelOpen })),
  setInfoPanelOpen: (infoPanelOpen) => set({ infoPanelOpen }),
  toggleCopilot: () => set((s) => ({ copilotOpen: !s.copilotOpen })),
  setCopilotOpen: (copilotOpen) => set({ copilotOpen }),
  setConnectionState: (connectionState) => set({ connectionState }),
}));
