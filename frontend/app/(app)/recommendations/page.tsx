"use client";

import { useState } from "react";
import { ConnectionList, ConnectionDetailModal } from "@/components/recommendations";
import { Sparkles, Star } from "lucide-react";

export default function RecommendationsPage() {
  const [selectedRecommendationId, setSelectedRecommendationId] = useState<string | null>(null);

  return (
    <div className="flex flex-1 flex-col h-full bg-app min-w-0 overflow-hidden">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-subtle bg-surface px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-button bg-accent/15 text-accent">
            <Star size={20} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-semibold text-primary">Gợi ý kết nối (AI Matchmaker)</h1>
              <span className="rounded-full bg-elevated px-2 py-0.5 text-xs text-accent">
                User-to-User
              </span>
            </div>
            <p className="text-xs text-secondary">
              Khám phá những người dùng thật trong hệ thống phù hợp với nhu cầu và kỹ năng của bạn
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 rounded-button border border-subtle bg-elevated/50 px-3 py-1.5 text-xs text-secondary">
          <Sparkles className="h-3.5 w-3.5 text-accent" />
          <span>AI-Powered Insights</span>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto p-6 scrollbar-thin">
        <div className="mx-auto max-w-4xl space-y-6">
          {/* Info Banner */}
          <div className="flex items-start gap-4 rounded-button border border-subtle bg-surface p-4">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-button bg-elevated text-accent">
              <Sparkles className="h-4 w-4" />
            </div>
            <div className="min-w-0 flex-1">
              <h3 className="text-sm font-medium text-primary">
                Cơ chế tìm kiếm người dùng phù hợp của AI
              </h3>
              <p className="mt-1 text-xs leading-relaxed text-secondary">
                MemoryChat AI tự động phân tích hồ sơ, lịch sử hội thoại và các nhu cầu (needs) / thế mạnh (offers) của bạn để tìm kiếm các tài khoản người dùng khác trong hệ thống. Khi tìm thấy sự tương thích cao, AI sẽ gợi ý trực tiếp để bạn có thể gửi lời chào và bắt đầu trò chuyện ngay lập tức.
              </p>
            </div>
          </div>

          {/* Connection List */}
          <ConnectionList
            onViewDetails={(id) => setSelectedRecommendationId(id)}
          />
        </div>
      </main>

      {/* Detail Modal */}
      {selectedRecommendationId && (
        <ConnectionDetailModal
          recommendationId={selectedRecommendationId}
          onClose={() => setSelectedRecommendationId(null)}
        />
      )}
    </div>
  );
}
