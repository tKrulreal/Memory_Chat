"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Check, X, MessageCircle, Search, UserPlus, Clock, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  getConnectionRequests,
  acceptConnectionRequest,
  rejectConnectionRequest,
  cancelConnectionRequest,
  sendConnectionRequest,
  ConnectionRequest,
} from "@/lib/api/connection-requests";
import { searchUsers, SearchUser, UserRelation } from "@/lib/api/search";
import { getConversations } from "@/lib/api/conversations";
import { useAuthStore } from "@/lib/stores/auth-store";
import { useConversationStore } from "@/lib/stores/conversation-store";

// ─── Relation action button ────────────────────────────────────────────────

interface RelationButtonProps {
  user: SearchUser;
  loading: boolean;
  onAddFriend: (userId: string) => void;
  onAccept: (userId: string) => void;
  onChat: (conversationId: string) => void;
}

function RelationButton({ user, loading, onAddFriend, onAccept, onChat }: RelationButtonProps) {
  const { relation, conversation_id } = user;

  if (relation === "none") {
    return (
      <Button
        size="sm"
        onClick={() => onAddFriend(user.id)}
        disabled={loading}
        id={`add-friend-${user.id}`}
      >
        <UserPlus size={14} className="mr-1.5" />
        {loading ? "Adding..." : "Add Friend"}
      </Button>
    );
  }

  if (relation === "pending_sent") {
    return (
      <Button size="sm" variant="ghost" disabled id={`pending-${user.id}`}>
        <Clock size={14} className="mr-1.5" />
        Pending
      </Button>
    );
  }

  if (relation === "pending_received") {
    return (
      <Button
        size="sm"
        variant="secondary"
        onClick={() => onAccept(user.id)}
        disabled={loading}
        id={`accept-${user.id}`}
      >
        <Check size={14} className="mr-1.5" />
        {loading ? "Accepting..." : "Accept"}
      </Button>
    );
  }

  // friend
  return (
    <Button
      size="sm"
      onClick={() => conversation_id && onChat(conversation_id)}
      disabled={!conversation_id}
      id={`chat-${user.id}`}
    >
      <MessageCircle size={14} className="mr-1.5" />
      Chat
    </Button>
  );
}

// ─── User card ─────────────────────────────────────────────────────────────

interface UserCardProps {
  user: SearchUser;
  loadingId: string | null;
  onAddFriend: (userId: string) => void;
  onAccept: (userId: string) => void;
  onChat: (conversationId: string) => void;
}

function UserCard({ user, loadingId, onAddFriend, onAccept, onChat }: UserCardProps) {
  const initials =
    user.full_name?.split(" ").map((p) => p[0]).join("").slice(0, 2).toUpperCase() ||
    user.email[0].toUpperCase();

  return (
    <div className="flex items-center justify-between rounded-button border border-subtle bg-surface p-4 transition-colors hover:bg-elevated">
      <div className="flex items-center gap-4">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-accent/20 font-semibold text-accent text-sm">
          {initials}
        </div>
        <div>
          <p className="font-medium text-primary">{user.full_name || "Unknown"}</p>
          <p className="text-xs text-secondary">{user.email}</p>
        </div>
      </div>
      <RelationButton
        user={user}
        loading={loadingId === user.id}
        onAddFriend={onAddFriend}
        onAccept={onAccept}
        onChat={onChat}
      />
    </div>
  );
}

// ─── Page ──────────────────────────────────────────────────────────────────

export default function ConnectionsPage() {
  const [tab, setTab] = useState<"incoming" | "outgoing">("incoming");
  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [loadingUserId, setLoadingUserId] = useState<string | null>(null);
  const [searchError, setSearchError] = useState<string | null>(null);

  // People search result cache — keyed by userId for optimistic updates
  const [peopleResults, setPeopleResults] = useState<SearchUser[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  const queryClient = useQueryClient();
  const router = useRouter();
  const user = useAuthStore((s) => s.user);
  const setActiveConversation = useConversationStore((s) => s.setActiveConversation);

  // ── Debounce search query ─────────────────────────────────────────────────
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      setDebouncedQuery(searchQuery.trim());
    }, 300);
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [searchQuery]);

  // ── Cancel stale requests with AbortController ────────────────────────────
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    if (debouncedQuery.length < 2) {
      setPeopleResults([]);
      setIsSearching(false);
      setSearchError(null);
      return;
    }

    // Cancel previous
    if (abortRef.current) abortRef.current.abort();
    abortRef.current = new AbortController();
    const signal = abortRef.current.signal;

    setIsSearching(true);
    setSearchError(null);

    searchUsers(debouncedQuery)
      .then((res) => {
        if (!signal.aborted) {
          setPeopleResults(res.items);
          setIsSearching(false);
        }
      })
      .catch((err) => {
        if (!signal.aborted) {
          setSearchError(err.message || "Search failed");
          setIsSearching(false);
        }
      });
  }, [debouncedQuery]);

  // ── Connection requests ───────────────────────────────────────────────────
  const { data, isLoading: isLoadingReqs } = useQuery({
    queryKey: ["connection-requests", tab],
    queryFn: () => getConnectionRequests(tab, "PENDING", 1, 50),
  });

  // Friends fallback (empty query)
  const { data: conversations, isLoading: isLoadingFriends } = useQuery({
    queryKey: ["conversations"],
    queryFn: getConversations,
    enabled: debouncedQuery.length < 2,
  });

  const requests = data?.data || [];

  const friendsFromConvs: SearchUser[] = (conversations || []).map((conv) => {
    const peer = conv.user_a_id === user?.id ? conv.user_b : conv.user_a;
    return {
      id: peer?.id || "",
      full_name: peer?.full_name || null,
      email: peer?.email || "",
      avatar: peer?.avatar || null,
      relation: "friend" as UserRelation,
      conversation_id: conv.id,
    };
  });

  // ── Optimistic relation update ────────────────────────────────────────────
  const updateUserRelation = useCallback(
    (userId: string, patch: Partial<SearchUser>) => {
      setPeopleResults((prev) =>
        prev.map((u) => (u.id === userId ? { ...u, ...patch } : u))
      );
    },
    []
  );

  // ── Add Friend ─────────────────────────────────────────────────────────────
  const handleAddFriend = useCallback(
    async (targetUserId: string) => {
      setLoadingUserId(targetUserId);
      try {
        await sendConnectionRequest(targetUserId);
        updateUserRelation(targetUserId, { relation: "pending_sent" });
      } catch (err: any) {
        const msg: string = err.message || "";
        if (msg.includes("409") || msg.toLowerCase().includes("conflict") || msg.toLowerCase().includes("already")) {
          // Stale UI — re-fetch this user's relation
          searchUsers(debouncedQuery).then((res) => {
            const fresh = res.items.find((u) => u.id === targetUserId);
            if (fresh) updateUserRelation(targetUserId, fresh);
          });
        }
        // For other errors, surface is logged to console only (non-blocking)
        console.error("[People] addFriend error:", msg);
      } finally {
        setLoadingUserId(null);
      }
    },
    [debouncedQuery, updateUserRelation]
  );

  // ── Accept (from people list — for pending_received) ──────────────────────
  const handleAcceptFromPeople = useCallback(
    async (targetUserId: string) => {
      // Find the matching incoming request id
      const allIncoming = await getConnectionRequests("incoming", "PENDING", 1, 100);
      const req = allIncoming.data.find(
        (r: ConnectionRequest) => r.sender_id === targetUserId
      );
      if (!req) return;

      setLoadingUserId(targetUserId);
      try {
        const accepted = await acceptConnectionRequest(req.id);
        // Optimistically switch to friend — conversation_id comes from accepted request's conversation
        queryClient.invalidateQueries({ queryKey: ["conversations"] });
        queryClient.invalidateQueries({ queryKey: ["connection-requests"] });
        // Re-search to pick up fresh conversation_id
        searchUsers(debouncedQuery).then((res) => {
          const fresh = res.items.find((u) => u.id === targetUserId);
          if (fresh) updateUserRelation(targetUserId, fresh);
        });
      } catch (err: any) {
        console.error("[People] accept error:", err.message);
      } finally {
        setLoadingUserId(null);
      }
    },
    [debouncedQuery, queryClient, updateUserRelation]
  );

  // ── Chat navigation ───────────────────────────────────────────────────────
  const handleChat = useCallback(
    (conversationId: string) => {
      setActiveConversation(conversationId);
      router.push("/chats");
    },
    [router, setActiveConversation]
  );

  // ── Request list mutations ────────────────────────────────────────────────
  const acceptMutation = useMutation({
    mutationFn: acceptConnectionRequest,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["connection-requests"] });
      queryClient.invalidateQueries({ queryKey: ["conversations"] });
    },
  });

  const rejectMutation = useMutation({
    mutationFn: rejectConnectionRequest,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["connection-requests"] }),
  });

  const cancelMutation = useMutation({
    mutationFn: cancelConnectionRequest,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["connection-requests"] }),
  });

  // ── Display list ──────────────────────────────────────────────────────────
  const isSearchMode = debouncedQuery.length >= 2;
  const displayPeople = isSearchMode ? peopleResults : friendsFromConvs;

  return (
    <div className="flex h-full flex-col">
      <header className="flex h-14 shrink-0 items-center border-b border-subtle px-6">
        <h1 className="text-lg font-semibold">People</h1>
      </header>

      <div className="flex-1 overflow-hidden">
        <div className="grid h-full grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-subtle">

          {/* LEFT PANEL: Connection Requests */}
          <div className="flex flex-col h-full overflow-hidden p-6">
            <div className="mb-6 flex gap-4 border-b border-subtle pb-2 shrink-0">
              <button
                id="tab-incoming"
                onClick={() => setTab("incoming")}
                className={`text-sm font-medium transition-colors ${
                  tab === "incoming" ? "text-primary border-b-2 border-primary" : "text-secondary hover:text-primary"
                }`}
              >
                Incoming Requests
              </button>
              <button
                id="tab-outgoing"
                onClick={() => setTab("outgoing")}
                className={`text-sm font-medium transition-colors ${
                  tab === "outgoing" ? "text-primary border-b-2 border-primary" : "text-secondary hover:text-primary"
                }`}
              >
                Outgoing Requests
              </button>
            </div>

            <div className="flex-1 overflow-y-auto scrollbar-thin pr-2">
              {isLoadingReqs ? (
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
                                id={`reject-req-${req.id}`}
                              >
                                <X size={16} className="mr-1" /> Reject
                              </Button>
                              <Button
                                size="sm"
                                onClick={() => acceptMutation.mutate(req.id)}
                                disabled={acceptMutation.isPending}
                                id={`accept-req-${req.id}`}
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
                              id={`cancel-req-${req.id}`}
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

          {/* RIGHT PANEL: People */}
          <div className="flex flex-col h-full overflow-hidden p-6">
            <div className="mb-6 shrink-0 border-b border-subtle pb-4">
              <h2 className="text-base font-semibold mb-4 flex items-center gap-2">
                <Users size={16} />
                {isSearchMode ? "Search Results" : "People"}
              </h2>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-secondary" size={16} />
                <input
                  id="people-search-input"
                  type="text"
                  placeholder="Search by name, email, or phone number..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full rounded-button bg-input pl-9 pr-4 py-2 text-sm text-primary outline-none focus:ring-1 focus:ring-accent"
                />
              </div>
            </div>

            <div className="flex-1 overflow-y-auto scrollbar-thin pr-2">
              {isSearching ? (
                <div className="text-sm text-secondary">Searching...</div>
              ) : searchError ? (
                <div className="text-sm text-destructive">{searchError}</div>
              ) : displayPeople.length === 0 ? (
                <div className="text-sm text-secondary">
                  {isSearchMode ? "No users found." : "No friends yet. Search to find people."}
                </div>
              ) : (
                <div className="space-y-3">
                  {displayPeople.map((u) => (
                    <UserCard
                      key={u.id}
                      user={u}
                      loadingId={loadingUserId}
                      onAddFriend={handleAddFriend}
                      onAccept={handleAcceptFromPeople}
                      onChat={handleChat}
                    />
                  ))}
                </div>
              )}
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
