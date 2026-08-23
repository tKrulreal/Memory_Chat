"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Check, X, MessageSquare, Search, UserPlus, Clock, Users, Sparkles, Star, Lock, MoreHorizontal } from "lucide-react";
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
import { ConnectionList, ConnectionDetailPanel } from "@/components/recommendations";
import { cn } from "@/lib/utils";
import { useAISettings } from "@/hooks/use-ai-settings";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";

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
        className="rounded-full transition-colors"
      >
        <UserPlus size={14} className="mr-1.5" />
        {loading ? "Adding..." : "Add Friend"}
      </Button>
    );
  }

  if (relation === "pending_sent") {
    return (
      <Button size="sm" variant="ghost" disabled id={`pending-${user.id}`} className="rounded-full transition-colors">
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
        className="rounded-full transition-colors"
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
      variant="outline"
      onClick={() => conversation_id && onChat(conversation_id)}
      disabled={!conversation_id}
      id={`chat-${user.id}`}
      className="rounded-full shadow-sm font-medium"
    >
      <MessageSquare size={14} className="mr-1.5" />
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
    <div className="flex items-center justify-between p-4 bg-white border border-slate-200 rounded-xl shadow-sm hover:shadow-md transition-all w-full">
      {/* Left side: Info */}
      <div className="flex items-center gap-4 min-w-0">
        <div className="relative shrink-0">
          <Avatar className="h-10 w-10 shrink-0 border border-slate-100">
            <AvatarFallback className="bg-blue-50 font-semibold text-blue-700 text-sm">
              {initials}
            </AvatarFallback>
          </Avatar>
          <span className="absolute bottom-0 right-0 h-2.5 w-2.5 rounded-full border-2 border-background bg-green-500" />
        </div>
        <div className="min-w-0 flex flex-col justify-center">
          <p className="text-sm font-semibold text-foreground truncate">{user.full_name || "Unknown"}</p>
          <div className="flex items-center gap-2 mt-0.5">
            <p className="text-xs text-slate-500 truncate">{user.email}</p>
            <div className="flex items-center gap-1 shrink-0">
              <Badge variant="secondary" className="text-[10px] py-0 px-1.5 h-4 font-normal bg-slate-100 text-slate-600">Bạn Bè</Badge>
              {user.relation === "friend" && <Badge variant="secondary" className="text-[10px] py-0 px-1.5 h-4 font-normal bg-blue-50 text-blue-600">Kết nối</Badge>}
            </div>
          </div>
        </div>
      </div>
      
      {/* Right side: Actions */}
      <div className="flex items-center gap-2 shrink-0 ml-4">
        <RelationButton
          user={user}
          loading={loadingId === user.id}
          onAddFriend={onAddFriend}
          onAccept={onAccept}
          onChat={onChat}
        />
        {user.relation === "friend" && (
          <DropdownMenu>
            <DropdownMenuTrigger className="h-8 w-8 rounded-md shrink-0 inline-flex items-center justify-center hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors focus:outline-none">
              <MoreHorizontal size={14} />
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem>View Profile</DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="text-destructive">Remove Connection</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )}
      </div>
    </div>
  );
}

// ─── My Network View ───────────────────────────────────────────────────────
function MyNetworkView() {
  const [tab, setTab] = useState<string>("incoming");
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
    queryFn: () => getConnectionRequests(tab as "incoming" | "outgoing" | "all", "PENDING", 1, 50),
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
    <div className="flex-1 overflow-hidden">
      <div className="grid h-full grid-cols-1 lg:grid-cols-[340px_1fr] divide-y lg:divide-y-0 divide-slate-200">

        {/* LEFT PANEL: Connection Requests */}
        <div className="flex flex-col h-full overflow-hidden py-6 pl-6 pr-4 border-r border-border bg-background">
          <h3 className="font-semibold text-sm mb-4">Requests</h3>
          <div className="flex p-1 bg-slate-100 rounded-xl w-fit mb-4 shrink-0">
            <button 
              className={tab === "incoming" 
                ? "px-4 py-1.5 text-sm font-semibold bg-white text-slate-900 shadow-sm rounded-lg transition-all" 
                : "px-4 py-1.5 text-sm font-medium text-slate-500 hover:text-slate-800 rounded-lg transition-all"}
              onClick={() => setTab("incoming")}
            >
              Incoming
            </button>
            <button 
              className={tab === "outgoing" 
                ? "px-4 py-1.5 text-sm font-semibold bg-white text-slate-900 shadow-sm rounded-lg transition-all" 
                : "px-4 py-1.5 text-sm font-medium text-slate-500 hover:text-slate-800 rounded-lg transition-all"}
              onClick={() => setTab("outgoing")}
            >
              Outgoing
            </button>
          </div>

          <div className="flex-1 overflow-y-auto scrollbar-thin pr-2">
            {isLoadingReqs ? (
              <div className="text-sm text-slate-500">Loading requests...</div>
            ) : requests.length === 0 ? (
              <div className="text-sm text-slate-500">No pending requests.</div>
            ) : (
              <div className="flex flex-col gap-3 w-full">
                {requests.map((req: ConnectionRequest) => {
                  const peer = tab === "incoming" ? req.sender : req.receiver;
                  const initials =
                    peer?.full_name?.split(" ").map((p: any) => p[0]).join("").slice(0, 2).toUpperCase() ||
                    peer?.email?.[0].toUpperCase() || "U";
                    
                  return (
                    <div
                      key={req.id}
                      className="flex items-center justify-between p-3 bg-white border border-slate-200 rounded-xl shadow-sm gap-2"
                    >
                      <div className="flex items-center gap-3 flex-1 min-w-0">
                        <div className="flex-shrink-0">
                          <Avatar className="h-10 w-10 border border-slate-100">
                            <AvatarFallback className="bg-blue-50 font-semibold text-blue-700 text-sm">
                              {initials}
                            </AvatarFallback>
                          </Avatar>
                        </div>
                        <div className="flex flex-col min-w-0 flex-1">
                          <h4 className="text-sm font-semibold text-slate-900 truncate">{peer?.full_name || "Unknown"}</h4>
                          <span className="text-xs text-slate-500 truncate">{peer?.email}</span>
                        </div>
                      </div>
                      
                      <div className="flex-shrink-0 flex items-center gap-1.5">
                        {tab === "incoming" ? (
                          <>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => rejectMutation.mutate(req.id)}
                              disabled={rejectMutation.isPending}
                              id={`reject-req-${req.id}`}
                              className="h-8 text-xs px-2.5"
                            >
                              Reject
                            </Button>
                            <Button
                              size="sm"
                              onClick={() => acceptMutation.mutate(req.id)}
                              disabled={acceptMutation.isPending}
                              id={`accept-req-${req.id}`}
                              className="h-8 text-xs px-2.5 bg-blue-600 hover:bg-blue-700 text-white shadow-sm"
                            >
                              Accept
                            </Button>
                          </>
                        ) : (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => cancelMutation.mutate(req.id)}
                            disabled={cancelMutation.isPending}
                            id={`cancel-req-${req.id}`}
                            className="h-8 text-xs px-2.5"
                          >
                            Cancel
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
        <div className="flex flex-col h-full overflow-hidden px-6 py-6 bg-background">
          <div className="mb-6 shrink-0 border-b border-border pb-4">
            <h2 className="text-base font-semibold mb-4 flex items-center gap-2 text-foreground">
              <Users size={16} />
              {isSearchMode ? "Search Results" : "People"}
            </h2>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={16} />
              <Input
                id="people-search-input"
                type="text"
                placeholder="Search by name, email, or phone number..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 bg-background"
              />
            </div>
          </div>

          <div className="flex-1 overflow-y-auto scrollbar-thin pr-2 pb-4">
            {isSearching ? (
              <div className="text-sm text-muted-foreground">Searching...</div>
            ) : searchError ? (
              <div className="text-sm text-red-500">{searchError}</div>
            ) : displayPeople.length === 0 ? (
              <div className="text-sm text-muted-foreground text-center py-8">
                {isSearchMode ? "No users found." : "No friends yet. Search to find people."}
              </div>
            ) : (
              <div className="flex flex-col gap-3 w-full">
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
  );
}

// ─── AI Matchmaker View ────────────────────────────────────────────────────
function AIMatchmakerView() {
  const [selectedRecommendationId, setSelectedRecommendationId] = useState<string | null>(null);
  const { features, isLoading } = useAISettings();
  const router = useRouter();

  if (!isLoading && !features.recommendation) {
    return (
      <div className="flex h-full w-full flex-col bg-slate-50 items-center justify-center">
        <div className="flex flex-col items-center gap-4 p-8 text-center bg-white border border-gray-200 rounded-2xl max-w-md shadow-sm">
          <Lock className="text-slate-400" size={48} />
          <h1 className="text-xl font-bold text-slate-800">Recommendations Disabled</h1>
          <p className="text-sm text-slate-500">
            AI Connection Recommendations have been disabled in the AI Hub settings.
          </p>
          <button onClick={() => router.push("/ai-hub")} className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-semibold hover:bg-blue-700 transition-colors">
            Go to AI Settings
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-1 flex-col h-full overflow-hidden bg-background">
      {/* Top Header */}
      <header className="flex items-center justify-between border-b border-border bg-card px-6 py-3.5 shrink-0">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary/10 text-primary shadow-sm">
            <Star size={18} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-sm font-bold text-foreground">Gợi ý kết nối (AI Matchmaker)</h1>
              <Badge variant="outline" className="text-[10px] font-semibold text-primary border-primary/20 bg-primary/5">
                Sắp xếp theo điểm tương thích
              </Badge>
            </div>
            <p className="text-[11px] text-muted-foreground">
              AI đánh giá và xếp hạng người dùng thật có tiềm năng hợp tác cao nhất lên đầu
            </p>
          </div>
        </div>
        <div className="hidden sm:flex items-center gap-2 rounded-xl border bg-muted px-3 py-1.5 text-xs text-muted-foreground">
          <Sparkles className="h-3.5 w-3.5 text-primary" />
          <span>Real-time Dynamic Matching</span>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 overflow-hidden p-4 sm:p-6">
        {selectedRecommendationId ? (
          /* Split View (Master-Detail) when a card is selected */
          <div className="flex h-full w-full gap-5 overflow-hidden">
            {/* Left Column: Compact Connection List */}
            <div className="w-full lg:w-[45%] xl:w-[40%] flex flex-col h-full overflow-y-auto pr-2 scrollbar-thin">
              <ConnectionList
                selectedId={selectedRecommendationId}
                onViewDetails={(id) => setSelectedRecommendationId(id)}
              />
            </div>

            {/* Right Column: Sliding Connection Detail Panel */}
            <div className="hidden lg:flex lg:w-[55%] xl:w-[60%] flex-col h-full overflow-hidden">
              <ConnectionDetailPanel
                recommendationId={selectedRecommendationId}
                onClose={() => setSelectedRecommendationId(null)}
              />
            </div>

            {/* Mobile Fallback Drawer / Full-screen overlay for smaller screens */}
            <div className="lg:hidden fixed inset-0 z-50 bg-slate-50/95 backdrop-blur-sm p-4 flex flex-col">
              <ConnectionDetailPanel
                recommendationId={selectedRecommendationId}
                onClose={() => setSelectedRecommendationId(null)}
              />
            </div>
          </div>
        ) : (
          /* Single Column (Full/Centered View) when no card is selected */
          <div className="mx-auto max-w-4xl h-full overflow-y-auto scrollbar-thin space-y-5">
            {/* Explanatory Banner */}
            <div className="flex items-start gap-3.5 rounded-xl border bg-card text-card-foreground p-4 shadow-sm">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
                <Sparkles className="h-4 w-4" />
              </div>
              <div className="min-w-0 flex-1">
                <h3 className="text-xs font-bold text-foreground">
                  Cơ chế xếp hạng và đề xuất người dùng phù hợp
                </h3>
                <p className="mt-0.5 text-xs leading-relaxed text-muted-foreground">
                  Hệ thống tự động so khớp hồ sơ của bạn với người dùng thật trong hệ thống, sắp xếp những người có <strong>điểm phù hợp cao nhất lên đầu</strong>. Bấm vào bất kỳ thẻ gợi ý nào để mở thanh phân tích chi tiết bên phải và bắt đầu trò chuyện trực tiếp.
                </p>
              </div>
            </div>

            {/* Full Width Connection List */}
            <ConnectionList
              selectedId={selectedRecommendationId}
              onViewDetails={(id) => setSelectedRecommendationId(id)}
            />
          </div>
        )}
      </main>
    </div>
  );
}

import { useSearchParams } from "next/navigation";

// ─── Main Page Component ───────────────────────────────────────────────────
function ConnectionsPageContent() {
  const searchParams = useSearchParams();
  const initialTab = searchParams?.get("tab") === "matchmaker" ? "matchmaker" : "network";
  const [activeTab, setActiveTab] = useState<"network" | "matchmaker">(initialTab);

  // Sync tab state when URL changes
  useEffect(() => {
    const tabParam = searchParams?.get("tab");
    if (tabParam === "matchmaker" || tabParam === "network") {
      setActiveTab(tabParam);
    }
  }, [searchParams]);

  return (
    <div className="flex h-full flex-col bg-background">
      <header className="flex h-16 shrink-0 items-center justify-between border-b border-border bg-card px-6">
        <h1 className="text-xl font-bold tracking-tight text-foreground">People</h1>
        <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as any)} className="w-auto">
          <TabsList className="h-10 bg-muted/50 p-1">
            <TabsTrigger 
              value="network" 
              className="gap-2 rounded-lg data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm data-[state=active]:font-medium transition-all"
            >
              <Users size={16} />
              My Network
              <span className="ml-1 rounded-full bg-muted-foreground/10 px-2 py-0.5 text-xs">24</span>
            </TabsTrigger>
            <TabsTrigger 
              value="matchmaker"
              className="gap-2 rounded-lg data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm data-[state=active]:font-medium transition-all"
            >
              <Sparkles size={16} className="text-indigo-500" />
              AI Matchmaker
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </header>

      {activeTab === "network" ? <MyNetworkView /> : <AIMatchmakerView />}
    </div>
  );
}

import { Suspense } from "react";

export default function ConnectionsPage() {
  return (
    <Suspense fallback={<div className="p-8 text-slate-500">Loading...</div>}>
      <ConnectionsPageContent />
    </Suspense>
  );
}
