"use client";

import { useState, useEffect, useRef, useCallback, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Check,
  X,
  MessageSquare,
  Search,
  UserPlus,
  UserMinus,
  Clock,
  Users,
  Sparkles,
  Star,
  Lock,
  MoreHorizontal,
  ExternalLink,
  Shield,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  getConnectionRequests,
  acceptConnectionRequest,
  rejectConnectionRequest,
  cancelConnectionRequest,
  sendConnectionRequest,
  unfriendUser,
  ConnectionRequest,
} from "@/lib/api/connection-requests";
import { searchUsers, SearchUser, UserRelation } from "@/lib/api/search";
import { getConversations } from "@/lib/api/conversations";
import { useAuthStore } from "@/lib/stores/auth-store";
import { useConversationStore } from "@/lib/stores/conversation-store";
import { usePresenceStore } from "@/lib/stores/presence-store";
import { ConnectionList, ConnectionDetailPanel, ConnectionDetailModal } from "@/components/recommendations";
import { cn } from "@/lib/utils";
import { useAISettings } from "@/hooks/use-ai-settings";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { toast } from "sonner";

// ─── Relation action button ────────────────────────────────────────────────

interface RelationButtonProps {
  user: SearchUser;
  loading: boolean;
  onAddFriend: (userId: string) => void;
  onAccept: (userId: string) => void;
  onChat: (conversationId: string) => void;
  onUnfriend?: (userId: string) => void;
}

function RelationButton({
  user,
  loading,
  onAddFriend,
  onAccept,
  onChat,
  onUnfriend,
}: RelationButtonProps) {
  const { relation, conversation_id } = user;

  if (relation === "none") {
    return (
      <Button
        size="sm"
        onClick={() => onAddFriend(user.id)}
        disabled={loading}
        id={`add-friend-${user.id}`}
        className="rounded-full bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs px-3.5 transition-colors shadow-xs cursor-pointer"
      >
        <UserPlus size={13} className="mr-1.5" />
        {loading ? "Đang gửi..." : "Kết bạn"}
      </Button>
    );
  }

  if (relation === "pending_sent") {
    return (
      <Button
        size="sm"
        variant="ghost"
        disabled
        id={`pending-${user.id}`}
        className="rounded-full text-xs font-semibold text-slate-400 bg-slate-100 hover:bg-slate-100 cursor-not-allowed"
      >
        <Clock size={13} className="mr-1.5 text-slate-400" />
        Đã gửi lời mời
      </Button>
    );
  }

  if (relation === "pending_received") {
    return (
      <Button
        size="sm"
        onClick={() => onAccept(user.id)}
        disabled={loading}
        id={`accept-${user.id}`}
        className="rounded-full bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs px-3.5 transition-colors shadow-xs cursor-pointer"
      >
        <Check size={13} className="mr-1.5" />
        {loading ? "Đang xử lý..." : "Chấp nhận"}
      </Button>
    );
  }

  // friend
  return (
    <div className="flex items-center gap-2">
      <Button
        size="sm"
        variant="outline"
        onClick={() => conversation_id && onChat(conversation_id)}
        disabled={!conversation_id}
        id={`chat-${user.id}`}
        className="rounded-full border-blue-200 text-blue-700 hover:bg-blue-50 text-xs font-semibold px-3.5 shadow-2xs cursor-pointer"
      >
        <MessageSquare size={13} className="mr-1.5 text-blue-600" />
        Nhắn tin
      </Button>
      {onUnfriend && (
        <Button
          size="sm"
          variant="outline"
          onClick={() => {
            if (confirm(`Bạn có chắc chắn muốn xóa bạn bè với ${user.full_name || user.email}?`)) {
              onUnfriend(user.id);
            }
          }}
          id={`unfriend-${user.id}`}
          className="rounded-full border-red-200 text-red-600 hover:bg-red-50 hover:text-red-700 text-xs font-semibold px-3 shadow-2xs cursor-pointer"
          title="Xóa bạn"
        >
          <UserMinus size={13} className="mr-1.5 text-red-500" />
          Xóa bạn
        </Button>
      )}
    </div>
  );
}

// ─── User card ─────────────────────────────────────────────────────────────

interface UserCardProps {
  user: SearchUser;
  loadingId: string | null;
  onAddFriend: (userId: string) => void;
  onAccept: (userId: string) => void;
  onChat: (conversationId: string) => void;
  onUnfriend: (userId: string) => void;
}

function UserCard({ user, loadingId, onAddFriend, onAccept, onChat, onUnfriend }: UserCardProps) {
  const router = useRouter();
  const onlineUserIds = usePresenceStore((s) => s.onlineUserIds);
  const isOnline = onlineUserIds.has(user.id);

  const initials =
    user.full_name?.split(" ").map((p) => p[0]).join("").slice(0, 2).toUpperCase() ||
    user.email[0].toUpperCase();

  return (
    <div className="flex items-center justify-between p-4 bg-white border border-slate-200/80 rounded-2xl shadow-xs hover:shadow-sm transition-all w-full">
      {/* Left side: Info */}
      <div className="flex items-center gap-3.5 min-w-0">
        <div className="relative shrink-0">
          <Avatar className="h-11 w-11 shrink-0 border border-slate-200">
            {user.avatar && <AvatarImage src={user.avatar} alt={user.full_name || ""} />}
            <AvatarFallback className="bg-blue-50 font-bold text-blue-700 text-xs">
              {initials}
            </AvatarFallback>
          </Avatar>
          {isOnline ? (
            <span className="absolute bottom-0 right-0 h-3.5 w-3.5 rounded-full bg-emerald-500 ring-2 ring-white" title="Đang hoạt động" />
          ) : (
            <span className="absolute bottom-0 right-0 h-3.5 w-3.5 rounded-full bg-slate-100 border-2 border-slate-400 ring-2 ring-white" title="Không hoạt động" />
          )}
        </div>
        <div className="min-w-0 flex flex-col justify-center">
          <p className="text-sm font-bold text-slate-900 truncate">
            {user.full_name || user.email.split("@")[0]}
          </p>
          <div className="flex items-center gap-2 mt-0.5 flex-wrap">
            <p className="text-xs text-slate-400 truncate">{user.email}</p>
            <div className="flex items-center gap-1 shrink-0">
              {user.relation === "friend" ? (
                <Badge variant="secondary" className="text-[10px] py-0 px-2 h-4 font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200/60">
                  Bạn bè
                </Badge>
              ) : user.relation === "pending_sent" ? (
                <Badge variant="secondary" className="text-[10px] py-0 px-2 h-4 font-semibold bg-amber-50 text-amber-700 border border-amber-200/60">
                  Đang chờ phản hồi
                </Badge>
              ) : user.relation === "pending_received" ? (
                <Badge variant="secondary" className="text-[10px] py-0 px-2 h-4 font-semibold bg-blue-50 text-blue-700 border border-blue-200/60">
                  Đã gửi lời mời cho bạn
                </Badge>
              ) : (
                <Badge variant="secondary" className="text-[10px] py-0 px-2 h-4 font-normal bg-slate-100 text-slate-600">
                  Người dùng
                </Badge>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Right side: Actions */}
      <div className="flex items-center gap-2 shrink-0 ml-3">
        <RelationButton
          user={user}
          loading={loadingId === user.id}
          onAddFriend={onAddFriend}
          onAccept={onAccept}
          onChat={onChat}
          onUnfriend={onUnfriend}
        />
        {user.relation === "friend" && (
          <DropdownMenu>
            <DropdownMenuTrigger className="h-8 w-8 rounded-xl shrink-0 inline-flex items-center justify-center hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors focus:outline-none cursor-pointer">
              <MoreHorizontal size={15} />
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="rounded-2xl shadow-lg border-slate-200 p-1 min-w-[160px]">
              <DropdownMenuItem
                onClick={() => router.push(`/profile/${user.id}`)}
                className="text-xs font-semibold cursor-pointer rounded-xl"
              >
                <ExternalLink size={13} className="mr-2" />
                Xem trang cá nhân
              </DropdownMenuItem>
              <DropdownMenuSeparator className="my-1 bg-slate-100" />
              <DropdownMenuItem
                onClick={() => {
                  if (confirm(`Bạn có chắc chắn muốn hủy kết bạn với ${user.full_name || user.email}?`)) {
                    onUnfriend(user.id);
                  }
                }}
                className="text-xs font-semibold cursor-pointer text-red-600 hover:text-red-700 hover:bg-red-50 rounded-xl"
              >
                <UserMinus size={13} className="mr-2" />
                Hủy kết bạn
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )}
      </div>
    </div>
  );
}

// ─── My Network View (Restored 2-Column Classic Layout) ─────────────────────
function MyNetworkView() {
  const [tab, setTab] = useState<string>("incoming");
  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [loadingUserId, setLoadingUserId] = useState<string | null>(null);
  const [searchError, setSearchError] = useState<string | null>(null);

  // People search result cache
  const [peopleResults, setPeopleResults] = useState<SearchUser[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  const queryClient = useQueryClient();
  const router = useRouter();
  const user = useAuthStore((s) => s.user);
  const setActiveConversation = useConversationStore((s) => s.setActiveConversation);
  const onlineUserIds = usePresenceStore((s) => s.onlineUserIds);

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

  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    if (debouncedQuery.length < 2) {
      setPeopleResults([]);
      setIsSearching(false);
      setSearchError(null);
      return;
    }

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
    enabled: !!user,
  });

  // Friends fallback (when search query is empty)
  const { data: conversations = [], isLoading: isLoadingFriends } = useQuery({
    queryKey: ["conversations"],
    queryFn: getConversations,
    enabled: !!user && debouncedQuery.length < 2,
  });

  const requests = data?.data || [];

  const friendsFromConvs: SearchUser[] = conversations.map((conv) => {
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
        queryClient.invalidateQueries({ queryKey: ["connection-requests"] });
        toast.success("Đã gửi lời mời kết bạn thành công!");
      } catch (err: any) {
        const msg: string = err.message || "";
        if (msg.includes("409") || msg.toLowerCase().includes("conflict") || msg.toLowerCase().includes("already") || msg.includes("đã")) {
          toast.warning(msg || "Lời mời kết bạn đã tồn tại hoặc hai bạn đã là bạn bè.");
          // Refresh user relation
          searchUsers(debouncedQuery).then((res) => {
            const fresh = res.items.find((u) => u.id === targetUserId);
            if (fresh) updateUserRelation(targetUserId, fresh);
          });
        } else {
          toast.error(msg || "Không thể gửi lời mời kết bạn.");
        }
      } finally {
        setLoadingUserId(null);
      }
    },
    [debouncedQuery, updateUserRelation, queryClient]
  );

  // ── Accept (from people list) ──────────────────────────────────────────────
  const handleAcceptFromPeople = useCallback(
    async (targetUserId: string) => {
      try {
        const allIncoming = await getConnectionRequests("incoming", "PENDING", 1, 100);
        const req = allIncoming.data.find(
          (r: ConnectionRequest) => r.sender_id === targetUserId
        );
        if (!req) return;

        setLoadingUserId(targetUserId);
        await acceptConnectionRequest(req.id);
        queryClient.invalidateQueries({ queryKey: ["conversations"] });
        queryClient.invalidateQueries({ queryKey: ["connection-requests"] });
        updateUserRelation(targetUserId, { relation: "friend" });
        toast.success("Đã chấp nhận lời mời kết bạn!");
        
        searchUsers(debouncedQuery).then((res) => {
          const fresh = res.items.find((u) => u.id === targetUserId);
          if (fresh) updateUserRelation(targetUserId, fresh);
        });
      } catch (err: any) {
        toast.error(err.message || "Lỗi khi chấp nhận lời mời.");
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

  // ── Request mutations ─────────────────────────────────────────────────────
  const acceptMutation = useMutation({
    mutationFn: acceptConnectionRequest,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["connection-requests"] });
      queryClient.invalidateQueries({ queryKey: ["conversations"] });
      toast.success("Đã chấp nhận kết bạn!");
    },
    onError: (err: any) => {
      toast.error(err?.message || "Không thể chấp nhận lời mời.");
    },
  });

  const rejectMutation = useMutation({
    mutationFn: rejectConnectionRequest,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["connection-requests"] });
      toast.info("Đã từ chối lời mời.");
    },
    onError: (err: any) => {
      toast.error(err?.message || "Lỗi xử lý.");
    },
  });

  const cancelMutation = useMutation({
    mutationFn: cancelConnectionRequest,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["connection-requests"] });
      toast.info("Đã hủy lời mời kết bạn.");
    },
    onError: (err: any) => {
      toast.error(err?.message || "Lỗi xử lý.");
    },
  });

  // ── Unfriend Mutation ─────────────────────────────────────────────────────
  const unfriendMutation = useMutation({
    mutationFn: (targetUserId: string) => unfriendUser(targetUserId),
    onSuccess: (_, targetUserId) => {
      queryClient.invalidateQueries({ queryKey: ["conversations"] });
      queryClient.invalidateQueries({ queryKey: ["connection-requests"] });
      queryClient.invalidateQueries({ queryKey: ["connections"] });
      updateUserRelation(targetUserId, { relation: "none", conversation_id: undefined });
      toast.success("Đã hủy kết bạn thành công.");
    },
    onError: (err: any) => {
      toast.error(err.message || "Lỗi khi hủy kết bạn.");
    },
  });

  const handleUnfriend = useCallback(
    (targetUserId: string) => {
      unfriendMutation.mutate(targetUserId);
    },
    [unfriendMutation]
  );

  // ── Display list ──────────────────────────────────────────────────────────
  const isSearchMode = debouncedQuery.length >= 2;
  const displayPeople = isSearchMode ? peopleResults : friendsFromConvs;

  return (
    <div className="flex-1 overflow-hidden">
      <div className="grid h-full grid-cols-1 lg:grid-cols-[360px_1fr] divide-y lg:divide-y-0 divide-slate-200">
        {/* LEFT PANEL: Connection Requests */}
        <div className="flex flex-col h-full overflow-hidden py-6 pl-6 pr-4 border-r border-slate-200 bg-white">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-sm text-slate-900 flex items-center gap-2">
              <Users size={16} className="text-blue-600" />
              Lời mời kết bạn (Requests)
            </h3>
          </div>

          <div className="flex p-1 bg-slate-100/90 rounded-2xl w-fit mb-4 shrink-0 border border-slate-200/50">
            <button
              className={
                tab === "incoming"
                  ? "px-4 py-1.5 text-xs font-bold bg-white text-slate-900 shadow-2xs rounded-xl transition-all"
                  : "px-4 py-1.5 text-xs font-semibold text-slate-500 hover:text-slate-800 rounded-xl transition-all"
              }
              onClick={() => setTab("incoming")}
            >
              Lời mời đến
            </button>
            <button
              className={
                tab === "outgoing"
                  ? "px-4 py-1.5 text-xs font-bold bg-white text-slate-900 shadow-2xs rounded-xl transition-all"
                  : "px-4 py-1.5 text-xs font-semibold text-slate-500 hover:text-slate-800 rounded-xl transition-all"
              }
              onClick={() => setTab("outgoing")}
            >
              Đã gửi
            </button>
          </div>

          <div className="flex-1 overflow-y-auto scrollbar-thin pr-2">
            {isLoadingReqs ? (
              <div className="text-xs text-slate-400 p-4">Đang tải danh sách...</div>
            ) : requests.length === 0 ? (
              <div className="text-xs text-slate-400 p-6 text-center">
                {tab === "incoming" ? "Không có lời mời kết bạn nào đang chờ." : "Bạn chưa gửi lời mời kết bạn nào."}
              </div>
            ) : (
              <div className="flex flex-col gap-3 w-full">
                {requests.map((req: ConnectionRequest) => {
                  const peer = tab === "incoming" ? req.sender : req.receiver;
                  const initials =
                    peer?.full_name?.split(" ").map((p: any) => p[0]).join("").slice(0, 2).toUpperCase() ||
                    peer?.email?.[0].toUpperCase() || "U";
                  const isPeerOnline = peer?.id ? onlineUserIds.has(peer.id) : false;

                  return (
                    <div
                      key={req.id}
                      className="flex items-center justify-between p-3.5 bg-white border border-slate-200/80 rounded-2xl shadow-2xs gap-2 hover:shadow-xs transition-all"
                    >
                      <div className="flex items-center gap-3 flex-1 min-w-0">
                        <div className="relative shrink-0">
                          <Avatar className="h-10 w-10 border border-slate-200">
                            {peer?.avatar && <AvatarImage src={peer.avatar} alt={peer.full_name || ""} />}
                            <AvatarFallback className="bg-blue-50 font-bold text-blue-700 text-xs">
                              {initials}
                            </AvatarFallback>
                          </Avatar>
                          {isPeerOnline ? (
                            <span className="absolute bottom-0 right-0 h-3 w-3 rounded-full bg-emerald-500 ring-2 ring-white" title="Đang hoạt động" />
                          ) : (
                            <span className="absolute bottom-0 right-0 h-3 w-3 rounded-full bg-slate-100 border-2 border-slate-400 ring-2 ring-white" title="Không hoạt động" />
                          )}
                        </div>
                        <div className="flex flex-col min-w-0 flex-1">
                          <h4 className="text-xs font-bold text-slate-900 truncate">
                            {peer?.full_name || peer?.email}
                          </h4>
                          <span className="text-[11px] text-slate-400 truncate">{peer?.email}</span>
                        </div>
                      </div>

                      <div className="shrink-0 flex items-center gap-1.5">
                        {tab === "incoming" ? (
                          <>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => rejectMutation.mutate(req.id)}
                              disabled={rejectMutation.isPending}
                              id={`reject-req-${req.id}`}
                              className="h-7.5 text-[11px] px-2.5 rounded-xl border-slate-200 hover:bg-slate-100"
                            >
                              Từ chối
                            </Button>
                            <Button
                              size="sm"
                              onClick={() => acceptMutation.mutate(req.id)}
                              disabled={acceptMutation.isPending}
                              id={`accept-req-${req.id}`}
                              className="h-7.5 text-[11px] px-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold shadow-2xs"
                            >
                              Chấp nhận
                            </Button>
                          </>
                        ) : (
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => cancelMutation.mutate(req.id)}
                            disabled={cancelMutation.isPending}
                            id={`cancel-req-${req.id}`}
                            className="h-7.5 text-[11px] px-2.5 rounded-xl text-slate-400 hover:text-red-600 hover:bg-red-50"
                          >
                            Hủy
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

        {/* RIGHT PANEL: People / Search Results */}
        <div className="flex flex-col h-full overflow-hidden px-6 py-6 bg-slate-50/50">
          <div className="mb-6 shrink-0 border-b border-slate-200/80 pb-4">
            <h2 className="text-base font-bold mb-3 flex items-center gap-2 text-slate-900">
              <Users size={16} className="text-blue-600" />
              {isSearchMode ? "Kết quả tìm kiếm người dùng" : "Bạn bè & Mạng lưới của bạn"}
            </h2>
            <div className="relative">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
              <Input
                id="people-search-input"
                type="search"
                placeholder="Tìm kiếm theo tên, email hoặc số điện thoại..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-4 h-10 rounded-2xl bg-white border-slate-200 text-xs focus:bg-white transition-colors"
              />
            </div>
          </div>

          <div className="flex-1 overflow-y-auto scrollbar-thin pr-2 pb-4">
            {isSearching ? (
              <div className="text-xs text-slate-400 p-4">Đang tìm kiếm...</div>
            ) : searchError ? (
              <div className="text-xs text-red-500 p-4">{searchError}</div>
            ) : displayPeople.length === 0 ? (
              <div className="text-xs text-slate-400 text-center py-12">
                {isSearchMode
                  ? "Không tìm thấy người dùng nào phù hợp."
                  : "Chưa có bạn bè nào. Hãy tìm kiếm để kết nối cùng mọi người!"}
              </div>
            ) : (
              <div className="flex flex-col gap-3 w-full max-w-4xl">
                {displayPeople.map((u) => (
                  <UserCard
                    key={u.id}
                    user={u}
                    loadingId={loadingUserId}
                    onAddFriend={handleAddFriend}
                    onAccept={handleAcceptFromPeople}
                    onChat={handleChat}
                    onUnfriend={handleUnfriend}
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
  const [modalRecommendationId, setModalRecommendationId] = useState<string | null>(null);
  const { features, isLoading } = useAISettings();
  const router = useRouter();

  if (!isLoading && !features.recommendation) {
    return (
      <div className="flex h-full w-full flex-col bg-slate-50 items-center justify-center">
        <div className="flex flex-col items-center gap-4 p-8 text-center bg-white border border-slate-200 rounded-3xl max-w-md shadow-sm">
          <Lock className="text-slate-400" size={48} />
          <h1 className="text-lg font-bold text-slate-800">Tính năng AI Matchmaker đang tắt</h1>
          <p className="text-xs text-slate-500 leading-relaxed">
            Gợi ý kết nối AI đã được tắt trong phần Cài đặt AI Hub. Bạn có thể bật lại để nhận các đề xuất ghép đôi.
          </p>
          <Button
            onClick={() => router.push("/ai-hub")}
            className="mt-2 rounded-2xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold px-5"
          >
            Đi đến AI Hub
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-1 flex-col h-full overflow-hidden bg-slate-50">
      {/* Top Header */}
      <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-3.5 shrink-0">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-600 text-white shadow-sm shadow-blue-500/20">
            <Sparkles size={18} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-sm font-bold text-slate-900">Gợi ý kết nối (AI Matchmaker)</h1>
              <Badge variant="outline" className="text-[10px] font-bold text-blue-700 border-blue-200 bg-blue-50">
                Sắp xếp theo điểm tương thích
              </Badge>
            </div>
            <p className="text-[11px] text-slate-500">
              AI đánh giá và xếp hạng người dùng thật có tiềm năng hợp tác cao nhất lên đầu.
            </p>
          </div>
        </div>
        <div className="hidden sm:flex items-center gap-2 rounded-2xl border border-blue-100 bg-blue-50/50 px-3.5 py-1.5 text-xs font-semibold text-blue-700">
          <Sparkles className="h-3.5 w-3.5 text-blue-600 animate-pulse" />
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
                onViewDetails={(id) => {
                  setSelectedRecommendationId(id);
                  setModalRecommendationId(id);
                }}
              />
            </div>

            {/* Right Column: Sliding Connection Detail Panel */}
            <div className="hidden lg:flex lg:w-[55%] xl:w-[60%] flex-col h-full overflow-hidden">
              <ConnectionDetailPanel
                recommendationId={selectedRecommendationId}
                onClose={() => setSelectedRecommendationId(null)}
              />
            </div>
          </div>
        ) : (
          /* Single Column when no card is selected */
          <div className="mx-auto max-w-4xl h-full overflow-y-auto scrollbar-thin space-y-5">
            {/* Explanatory Banner */}
            <div className="flex items-start gap-3.5 rounded-3xl border border-blue-100 bg-gradient-to-r from-blue-50/70 via-white to-indigo-50/70 p-5 shadow-xs">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-600 text-white shadow-xs">
                <Sparkles className="h-4 w-4" />
              </div>
              <div className="min-w-0 flex-1">
                <h3 className="text-xs font-bold text-slate-900">
                  Cơ chế xếp hạng và đề xuất người dùng phù hợp
                </h3>
                <p className="mt-1 text-xs leading-relaxed text-slate-600">
                  Hệ thống tự động so khớp hồ sơ của bạn với người dùng thật trong hệ thống, sắp xếp những người có <strong>điểm phù hợp cao nhất lên đầu</strong>. Bấm vào nút <strong>&quot;Chi tiết&quot;</strong> trên thẻ gợi ý để xem bảng so sánh chi tiết dạng pop-up và gửi lời mời kết bạn trực tiếp.
                </p>
              </div>
            </div>

            {/* Full Width Connection List */}
            <ConnectionList
              selectedId={selectedRecommendationId}
              onViewDetails={(id) => {
                setModalRecommendationId(id);
              }}
            />
          </div>
        )}
      </main>

      {/* POPUP COMPARISON MODAL */}
      {modalRecommendationId && (
        <ConnectionDetailModal
          recommendationId={modalRecommendationId}
          onClose={() => setModalRecommendationId(null)}
        />
      )}
    </div>
  );
}

// ─── Main Page Component ───────────────────────────────────────────────────
function ConnectionsPageContent() {
  const searchParams = useSearchParams();
  const initialTab = searchParams?.get("tab") === "matchmaker" ? "matchmaker" : "network";
  const [activeTab, setActiveTab] = useState<"network" | "matchmaker">(initialTab);

  const { data: incomingData } = useQuery({
    queryKey: ["connection-requests", "incoming"],
    queryFn: () => getConnectionRequests("incoming", "PENDING", 1, 50),
  });

  const incomingCount = incomingData?.data?.length || 0;

  // Sync tab state when URL changes
  useEffect(() => {
    const tabParam = searchParams?.get("tab");
    if (tabParam === "matchmaker" || tabParam === "network") {
      setActiveTab(tabParam);
    }
  }, [searchParams]);

  return (
    <div className="flex h-full flex-col bg-slate-50">
      <header className="flex h-16 shrink-0 items-center justify-between border-b border-slate-200 bg-white px-6">
        <h1 className="text-lg font-bold tracking-tight text-slate-900 flex items-center gap-2">
          <Users className="text-blue-600" size={20} />
          Kết nối & Mạng lưới (People)
        </h1>
        <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as any)} className="w-auto">
          <TabsList className="h-10 bg-slate-100 p-1 rounded-2xl border border-slate-200/60">
            <TabsTrigger
              value="network"
              className="gap-2 rounded-xl text-xs font-semibold data-[state=active]:bg-white data-[state=active]:text-slate-900 data-[state=active]:shadow-2xs transition-all cursor-pointer"
            >
              <Users size={14} />
              Mạng lưới của tôi
              {incomingCount > 0 && (
                <span className="ml-1 rounded-full bg-blue-600 px-1.5 py-0.2 text-[10px] font-bold text-white">
                  {incomingCount}
                </span>
              )}
            </TabsTrigger>
            <TabsTrigger
              value="matchmaker"
              className="gap-2 rounded-xl text-xs font-semibold data-[state=active]:bg-white data-[state=active]:text-slate-900 data-[state=active]:shadow-2xs transition-all cursor-pointer"
            >
              <Sparkles size={14} className="text-blue-600" />
              AI Matchmaker
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </header>

      {activeTab === "network" ? <MyNetworkView /> : <AIMatchmakerView />}
    </div>
  );
}

export default function ConnectionsPage() {
  return (
    <Suspense fallback={<div className="p-8 text-slate-500 text-xs">Đang tải trang kết nối...</div>}>
      <ConnectionsPageContent />
    </Suspense>
  );
}
