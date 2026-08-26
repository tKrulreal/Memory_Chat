"use client";

import { create } from "zustand";

export type CopilotMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  intent?: string;
};

type CopilotState = {
  messages: CopilotMessage[];
  isLoading: boolean;
  activeConversationId: string | null;
  
  addMessage: (msg: CopilotMessage) => void;
  setLoading: (isLoading: boolean) => void;
  setActiveConversationId: (id: string | null) => void;
  clearMessages: () => void;
};

export const useCopilotStore = create<CopilotState>((set) => ({
  messages: [],
  isLoading: false,
  activeConversationId: null,

  addMessage: (msg) =>
    set((state) => ({
      messages: [...state.messages, msg],
    })),

  setLoading: (isLoading) => set({ isLoading }),

  setActiveConversationId: (activeConversationId) =>
    set((state) => {
      // Clear messages if switching to a different conversation
      if (state.activeConversationId !== activeConversationId) {
        return { activeConversationId, messages: [] };
      }
      return { activeConversationId };
    }),

  clearMessages: () => set({ messages: [] }),
}));
