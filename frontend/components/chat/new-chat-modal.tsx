"use client";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createConversation } from "@/lib/api/conversations";
import { useConversationStore } from "@/lib/stores/conversation-store";
import { Button } from "@/components/ui/button";

type NewChatModalProps = {
  isOpen: boolean;
  onClose: () => void;
};

export function NewChatModal({ isOpen, onClose }: NewChatModalProps) {
  const [email, setEmail] = useState("");
  const queryClient = useQueryClient();
  const setActive = useConversationStore((s) => s.setActiveConversation);

  const mutation = useMutation({
    mutationFn: createConversation,
    onSuccess: (conversation) => {
      queryClient.invalidateQueries({ queryKey: ["conversations"] });
      setActive(conversation.id);
      setEmail("");
      onClose();
    },
  });

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="w-full max-w-md rounded-button border border-subtle bg-surface p-6">
        <h2 className="mb-4 text-xl font-bold">New Chat</h2>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            mutation.mutate(email);
          }}
        >
          <div className="mb-4">
            <label htmlFor="peer_email" className="mb-1 block text-sm text-secondary">
              Peer Email
            </label>
            <input
              id="peer_email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="user@example.com"
              className="h-11 w-full rounded-button bg-input px-3 text-sm outline-none ring-accent focus:ring-1"
            />
          </div>
          {mutation.isError && (
            <p className="mb-4 text-sm text-red-400">
              {mutation.error instanceof Error ? mutation.error.message : "Failed to create chat"}
            </p>
          )}
          <div className="flex justify-end gap-2">
            <Button type="button" variant="ghost" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? "Creating..." : "Create Chat"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
