"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Check, X, MessageCircle, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  getConnectionRequests,
  acceptConnectionRequest,
  rejectConnectionRequest,
  cancelConnectionRequest,
  ConnectionRequest,
} from "@/lib/api/connection-requests";
import { getConversations } from "@/lib/api/conversations";
import { useAuthStore } from "@/lib/stores/auth-store";
import { useConversationStore } from "@/lib/stores/conversation-store";

export default function ConnectionsPage() {
  const [tab, setTab] = useState<"incoming" | "outgoing">("incoming");
  const [searchQuery, setSearchQuery] = useState("");
  const queryClient = useQueryClient();
  const router = useRouter();
  const user = useAuthStore((s) => s.user);
  const setActiveConversation = useConversationStore((s) => s.setActiveConversation);

  const { data, isLoading } = useQuery({
    queryKey: ["connection-requests", tab],
    queryFn: () => getConnectionRequests(tab, "PENDING", 1, 50),
  });

  const { data: conversations, isLoading: isLoadingFriends } = useQuery({
    queryKey: ["conversations"],
    queryFn: getConversations,
  });

  const acceptMutation = useMutation({
    mutationFn: acceptConnectionRequest,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["connection-requests"] });
    },
  });

  const rejectMutation = useMutation({
    mutationFn: rejectConnectionRequest,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["connection-requests"] });
    },
  });

  const cancelMutation = useMutation({
    mutationFn: cancelConnectionRequest,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["connection-requests"] });
    },
  });

  const requests = data?.data || [];

  const filteredConversations = (conversations?.filter(conv => {
    const peer = conv.user_a_id === user?.id ? conv.user_b : conv.user_a;
    const q = searchQuery.toLowerCase();
    return peer?.full_name?.toLowerCase().includes(q) || peer?.email?.toLowerCase().includes(q);
  }) || []).sort((a, b) => {
    const peerA = a.user_a_id === user?.id ? a.user_b : a.user_a;
    const peerB = b.user_a_id === user?.id ? b.user_b : b.user_a;
    const nameA = peerA?.full_name || peerA?.email || "";
    const nameB = peerB?.full_name || peerB?.email || "";
    return nameA.localeCompare(nameB);
  });

  return (
    <div className="flex h-full flex-col">
      <header className="flex h-14 shrink-0 items-center border-b border-subtle px-6">
        <h1 className="text-lg font-semibold">Connections</h1>
      </header>
      <div className="flex-1 overflow-hidden">
        <div className="grid h-full grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-subtle">
          
          {/* LEFT PANEL: Requests */}
          <div className="flex flex-col h-full overflow-hidden p-6">
            <div className="mb-6 flex gap-4 border-b border-subtle pb-2 shrink-0">
              <button
                onClick={() => setTab("incoming")}
                className={`text-sm font-medium transition-colors ${
                  tab === "incoming" ? "text-primary border-b-2 border-primary" : "text-secondary hover:text-primary"
                }`}
              >
                Incoming Requests
              </button>
              <button
                onClick={() => setTab("outgoing")}
                className={`text-sm font-medium transition-colors ${
                  tab === "outgoing" ? "text-primary border-b-2 border-primary" : "text-secondary hover:text-primary"
                }`}
              >
                Outgoing Requests
              </button>
            </div>

            <div className="flex-1 overflow-y-auto scrollbar-thin pr-2">
              {isLoading ? (
                <div className="text-sm text-secondary">Loading requests...</div>
              ) : requests.length === 0 ? (
                <div className="text-sm text-secondary">No pending requests.</div>
              ) : (
                <div className="space-y-4">
                  {requests.map((req: ConnectionRequest) => {
                    const peer = tab === "incoming" ? req.sender : req.receiver;
                    return (
                      <div
                        key={req.id}
                        className="flex items-center justify-between rounded-button border border-subtle bg-surface p-4"
                      >
                        <div className="flex items-center gap-4">
                          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-accent/20 font-semibold text-accent">
                            {peer?.full_name?.charAt(0) || peer?.email?.charAt(0) || "U"}
                          </div>
                          <div>
                            <p className="font-medium text-primary">{peer?.full_name || "Unknown"}</p>
                            <p className="text-sm text-secondary">{peer?.email}</p>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          {tab === "incoming" ? (
                            <>
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => rejectMutation.mutate(req.id)}
                                disabled={rejectMutation.isPending}
                              >
                                <X size={16} className="mr-1" /> Reject
                              </Button>
                              <Button
                                size="sm"
                                onClick={() => acceptMutation.mutate(req.id)}
                                disabled={acceptMutation.isPending}
                              >
                                <Check size={16} className="mr-1" /> Accept
                              </Button>
                            </>
                          ) : (
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => cancelMutation.mutate(req.id)}
                              disabled={cancelMutation.isPending}
                            >
                              <X size={16} className="mr-1" /> Cancel
                            </Button>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>

          {/* RIGHT PANEL: Current Friends */}
          <div className="flex flex-col h-full overflow-hidden p-6">
            <div className="mb-6 shrink-0 border-b border-subtle pb-4">
              <h2 className="text-base font-semibold mb-4">
                Current Friends
              </h2>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-secondary" size={16} />
                <input
                  type="text"
                  placeholder="Search friends..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full rounded-button bg-input pl-9 pr-4 py-2 text-sm text-primary outline-none focus:ring-1 focus:ring-accent"
                />
              </div>
            </div>
            <div className="flex-1 overflow-y-auto scrollbar-thin pr-2">
              {isLoadingFriends ? (
                <div className="text-sm text-secondary">Loading friends...</div>
              ) : filteredConversations.length === 0 ? (
                <div className="text-sm text-secondary">No friends found.</div>
              ) : (
                <div className="space-y-4">
                  {filteredConversations.map((conv) => {
                    const peer = conv.user_a_id === user?.id ? conv.user_b : conv.user_a;
                    return (
                      <div
                        key={conv.id}
                        className="flex items-center justify-between rounded-button border border-subtle bg-surface p-4 transition-colors hover:bg-elevated cursor-pointer"
                        onClick={() => {
                          setActiveConversation(conv.id);
                          router.push("/chats");
                        }}
                      >
                        <div className="flex items-center gap-4">
                          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-accent/20 font-semibold text-accent">
                            {peer?.full_name?.charAt(0) || peer?.email?.charAt(0) || "U"}
                          </div>
                          <div>
                            <p className="font-medium text-primary">{peer?.full_name || "Unknown User"}</p>
                            <p className="text-sm text-secondary">{peer?.email}</p>
                          </div>
                        </div>
                        <Button size="sm" variant="secondary">
                          <MessageCircle size={16} className="mr-2" /> Chat
                        </Button>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
