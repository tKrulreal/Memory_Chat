"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { RefreshCw, Filter, Check, Clock, X, Sparkles, TrendingUp } from "lucide-react";
import { ConnectionCard } from "./ConnectionCard";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  getConnectionRecommendations,
  generateConnections,
} from "@/lib/api/recommendations";
import { toast } from "sonner";
import { RecommendationStatus, ConnectionRecommendation } from "@/types/recommendation";
import { cn } from "@/lib/utils";

interface ConnectionListProps {
  selectedId?: string | null;
  onViewDetails?: (id: string) => void;
}

type TabValue = RecommendationStatus | "ALL";

const TABS: { label: string; value: TabValue; icon: React.ComponentType<{ size?: number; className?: string }> }[] = [
  { label: "Chờ duyệt", value: "PENDING", icon: Clock },
  { label: "Đã kết nối", value: "ACCEPTED", icon: Check },
  { label: "Đã từ chối", value: "REJECTED", icon: X },
  { label: "Tất cả", value: "ALL", icon: Filter },
];

export function ConnectionList({ selectedId, onViewDetails }: ConnectionListProps) {
  const [activeTab, setActiveTab] = useState<TabValue>("PENDING");
  const queryClient = useQueryClient();

  const statusFilter: RecommendationStatus | undefined = activeTab === "ALL" ? undefined : activeTab;

  const {
    data: rawRecommendations = [],
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ["connection-recommendations", statusFilter],
    queryFn: () => getConnectionRecommendations(statusFilter, 30),
    enabled: true,
  });

  const generateMutation = useMutation({
    mutationFn: generateConnections,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["connection-recommendations"] });
      queryClient.invalidateQueries({ queryKey: ["user-profile"] });
      toast.success(data?.message || "Đã phân tích hồ sơ và cập nhật danh sách gợi ý!");
    },
    onError: (err: any) => {
      toast.error(err?.message || "Không thể quét gợi ý mới.");
    },
  });

  // Sort recommendations strictly from highest match score (confidence) to lowest
  const recommendations = [...rawRecommendations].sort((a, b) => {
    const scoreA = a.confidence ?? 0;
    const scoreB = b.confidence ?? 0;
    return scoreB - scoreA;
  });

  const handleAccept = (id: string) => {
    queryClient.setQueryData<ConnectionRecommendation[]>(
      ["connection-recommendations", statusFilter],
      (old) => old?.filter((r) => r.id !== id)
    );
  };

  const handleReject = (id: string) => {
    queryClient.setQueryData<ConnectionRecommendation[]>(
      ["connection-recommendations", statusFilter],
      (old) => old?.filter((r) => r.id !== id)
    );
  };

  const handleDismiss = (id: string) => {
    queryClient.setQueryData<ConnectionRecommendation[]>(
      ["connection-recommendations", statusFilter],
      (old) => old?.filter((r) => r.id !== id)
    );
  };

  const pendingCount = recommendations.filter((r) => r.status === "PENDING").length;

  return (
    <div className="space-y-4">
      {/* Action Toolbar & Filters */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-subtle pb-3">
        <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as TabValue)} className="w-full sm:w-auto">
          <TabsList className="h-9 w-full sm:w-auto">
            {TABS.map((tab) => {
              const Icon = tab.icon;
              return (
                <TabsTrigger key={tab.value} value={tab.value} className="flex items-center gap-1.5 px-3">
                  <Icon size={13} />
                  <span>{tab.label}</span>
                  {tab.value === "PENDING" && pendingCount > 0 && (
                    <span className="ml-1 rounded-full bg-accent/20 px-1.5 py-0.5 text-[10px] font-bold text-accent">
                      {pendingCount}
                    </span>
                  )}
                </TabsTrigger>
              );
            })}
          </TabsList>
        </Tabs>

        {/* Sort indicator & Generate Button */}
        <div className="flex items-center gap-2">
          <div className="hidden xl:flex items-center gap-1 text-[11px] text-muted-foreground bg-muted/50 px-2.5 py-1 rounded-lg border border-subtle/60">
            <TrendingUp size={12} className="text-accent" />
            <span>Điểm cao nhất lên đầu</span>
          </div>

          <Button
            variant="secondary"
            size="sm"
            onClick={() => generateMutation.mutate()}
            disabled={generateMutation.isPending}
            className="shrink-0 text-xs"
          >
            <RefreshCw
              size={13}
              className={cn("mr-1.5", generateMutation.isPending && "animate-spin")}
            />
            {generateMutation.isPending ? "AI đang quét..." : "Quét gợi ý mới"}
          </Button>
        </div>
      </div>

      {/* Content List */}
      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="rounded-2xl border border-subtle bg-card p-5 space-y-3">
              <div className="flex items-center justify-between">
                <Skeleton className="h-5 w-28 rounded-full" />
                <Skeleton className="h-4 w-16" />
              </div>
              <Skeleton className="h-16 w-full rounded-xl" />
              <div className="flex gap-2">
                <Skeleton className="h-8 flex-1 rounded-lg" />
                <Skeleton className="h-8 w-20 rounded-lg" />
              </div>
            </div>
          ))}
        </div>
      ) : isError ? (
        <div className="rounded-2xl border border-subtle bg-card p-8 text-center">
          <p className="text-sm font-medium text-foreground">Không thể tải danh sách gợi ý</p>
          <p className="mt-1 text-xs text-muted-foreground">{String(error)}</p>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => queryClient.invalidateQueries({ queryKey: ["connection-recommendations"] })}
            className="mt-4"
          >
            Thử lại
          </Button>
        </div>
      ) : recommendations.length === 0 ? (
        <div className="rounded-2xl border border-subtle bg-card p-12 text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-muted text-muted-foreground">
            <Sparkles size={22} />
          </div>
          <h3 className="text-sm font-semibold text-foreground mb-1">
            Không có gợi ý nào trong mục này
          </h3>
          <p className="mx-auto max-w-sm text-xs leading-relaxed text-muted-foreground mb-5">
            {activeTab === "PENDING"
              ? "Hệ thống AI sẽ tự động phân tích kỹ năng và nhu cầu của bạn để tìm những người dùng thật trong hệ thống phù hợp nhất."
              : `Bạn hiện không có gợi ý nào ở trạng thái ${activeTab.toLowerCase()}.`}
          </p>
          {activeTab === "PENDING" && (
            <Button
              variant="primary"
              size="sm"
              onClick={() => generateMutation.mutate()}
              disabled={generateMutation.isPending}
            >
              <RefreshCw size={13} className={cn("mr-1.5", generateMutation.isPending && "animate-spin")} />
              {generateMutation.isPending ? "Đang quét..." : "Quét tìm người phù hợp ngay"}
            </Button>
          )}
        </div>
      ) : (
        <div className="space-y-3.5">
          {recommendations.map((rec) => (
            <ConnectionCard
              key={rec.id}
              recommendation={rec}
              isSelected={rec.id === selectedId}
              onAccept={handleAccept}
              onReject={handleReject}
              onDismiss={handleDismiss}
              onViewDetails={onViewDetails}
            />
          ))}
        </div>
      )}
    </div>
  );
}
