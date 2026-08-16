"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { RefreshCw, Filter, Check, Clock, X, Sparkles } from "lucide-react";
import { ConnectionCard } from "./ConnectionCard";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  getConnectionRecommendations,
  generateConnections,
} from "@/lib/api/recommendations";
import { RecommendationStatus, ConnectionRecommendation } from "@/types/recommendation";
import { cn } from "@/lib/utils";

interface ConnectionListProps {
  onViewDetails?: (id: string) => void;
}

type TabValue = RecommendationStatus | "ALL";

const TABS: { label: string; value: TabValue; icon: React.ComponentType<{ size?: number; className?: string }> }[] = [
  { label: "Chờ duyệt", value: "PENDING", icon: Clock },
  { label: "Đã kết nối", value: "ACCEPTED", icon: Check },
  { label: "Đã từ chối", value: "REJECTED", icon: X },
  { label: "Tất cả", value: "ALL", icon: Filter },
];

export function ConnectionList({ onViewDetails }: ConnectionListProps) {
  const [activeTab, setActiveTab] = useState<TabValue>("PENDING");
  const queryClient = useQueryClient();

  const statusFilter: RecommendationStatus | undefined = activeTab === "ALL" ? undefined : activeTab;

  const {
    data: recommendations = [],
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ["connection-recommendations", statusFilter],
    queryFn: () => getConnectionRecommendations(statusFilter, 20),
    enabled: true,
  });

  const generateMutation = useMutation({
    mutationFn: generateConnections,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["connection-recommendations"] });
    },
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
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-subtle pb-4">
        {/* Tab switcher */}
        <div className="flex items-center gap-1 rounded-button bg-surface border border-subtle p-1">
          {TABS.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.value;
            return (
              <button
                key={tab.value}
                type="button"
                onClick={() => setActiveTab(tab.value)}
                className={cn(
                  "flex items-center gap-1.5 rounded-button px-3 py-1.5 text-xs font-medium transition-colors",
                  isActive
                    ? "bg-elevated text-primary shadow-sm"
                    : "text-secondary hover:text-primary hover:bg-elevated/50"
                )}
              >
                <Icon size={14} />
                <span>{tab.label}</span>
                {tab.value === "PENDING" && pendingCount > 0 && (
                  <span className="ml-1 rounded-full bg-accent/20 px-1.5 py-0.2 text-[10px] font-semibold text-accent">
                    {pendingCount}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* Generate / Refresh Button */}
        <Button
          variant="secondary"
          size="sm"
          onClick={() => generateMutation.mutate()}
          disabled={generateMutation.isPending}
          className="shrink-0"
        >
          <RefreshCw
            size={14}
            className={cn("mr-1.5", generateMutation.isPending && "animate-spin")}
          />
          {generateMutation.isPending ? "AI đang quét tìm người phù hợp..." : "Tìm gợi ý kết nối mới"}
        </Button>
      </div>

      {/* Content List */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="rounded-button border border-subtle bg-surface p-5 space-y-3">
              <div className="flex items-center justify-between">
                <Skeleton className="h-5 w-28 rounded-full" />
                <Skeleton className="h-4 w-16" />
              </div>
              <Skeleton className="h-20 w-full rounded-button" />
              <div className="flex gap-2">
                <Skeleton className="h-8 flex-1 rounded-button" />
                <Skeleton className="h-8 w-20 rounded-button" />
              </div>
            </div>
          ))}
        </div>
      ) : isError ? (
        <div className="rounded-button border border-subtle bg-surface p-8 text-center">
          <p className="text-sm font-medium text-primary">Không thể tải danh sách gợi ý</p>
          <p className="mt-1 text-xs text-secondary">{String(error)}</p>
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
        <div className="rounded-button border border-subtle bg-surface p-12 text-center">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-elevated text-secondary">
            <Sparkles size={24} />
          </div>
          <h3 className="text-base font-semibold text-primary mb-1">
            Không có gợi ý nào trong mục này
          </h3>
          <p className="mx-auto max-w-sm text-xs leading-relaxed text-secondary mb-6">
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
              <RefreshCw size={14} className={cn("mr-1.5", generateMutation.isPending && "animate-spin")} />
              {generateMutation.isPending ? "Đang quét..." : "Quét tìm người phù hợp ngay"}
            </Button>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          {recommendations.map((rec) => (
            <ConnectionCard
              key={rec.id}
              recommendation={rec}
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
