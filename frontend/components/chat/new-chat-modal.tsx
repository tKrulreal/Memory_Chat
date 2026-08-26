"use client";

import { useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { sendConnectionRequest } from "@/lib/api/connection-requests";
import { Button } from "@/components/ui/button";

type NewChatModalProps = {
  isOpen: boolean;
  onClose: () => void;
};

export function NewChatModal({ isOpen, onClose }: NewChatModalProps) {
  const router = useRouter();
  const pathname = usePathname();
  const [email, setEmail] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: (email: string) => sendConnectionRequest(undefined, email),
    onSuccess: (request) => {
      queryClient.invalidateQueries({ queryKey: ["connection-requests"] });
      if (request.status === "ACCEPTED") {
        setSuccessMsg("Connected! You can now chat.");
        // Could redirect to chats here if we knew the conversation_id
      } else {
        setSuccessMsg("Connection request sent!");
      }
      setTimeout(() => {
        setSuccessMsg("");
        setEmail("");
        onClose();
      }, 2000);
    },
  });


  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="w-full max-w-md rounded-button border border-subtle bg-card p-6">
        <h2 className="mb-4 text-xl font-bold">New Chat</h2>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            mutation.mutate(email);
          }}
        >
          <div className="mb-4">
            <label htmlFor="peer_email" className="mb-1 block text-sm text-muted-foreground">
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
              {mutation.error instanceof Error ? mutation.error.message : "Failed to send request"}
            </p>
          )}
          {successMsg && (
            <p className="mb-4 text-sm text-green-400">
              {successMsg}
            </p>
          )}
          <div className="flex justify-end gap-2">
            <Button type="button" variant="ghost" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={mutation.isPending || !!successMsg}>
              {mutation.isPending ? "Sending..." : "Send Request"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
