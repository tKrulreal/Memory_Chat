"use client";

import { useState } from "react";
import { ConnectionList, ConnectionDetailPanel } from "@/components/recommendations";
import { Sparkles, Star, Users, Info } from "lucide-react";
import { cn } from "@/lib/utils";

export default function RecommendationsPage() {
  const [selectedRecommendationId, setSelectedRecommendationId] = useState<string | null>(null);

  return (
    <div className="flex flex-1 flex-col h-full bg-app min-w-0 overflow-hidden">
      {/* Top Header */}
      <header className="flex items-center justify-between border-b border-subtle bg-surface px-6 py-3.5 shrink-0">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-accent/15 text-accent shadow-sm">
            <Star size={18} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-sm font-bold text-primary">Gợi ý kết nối (AI Matchmaker)</h1>
              <span className="rounded-full bg-elevated px-2 py-0.5 text-[10px] font-semibold text-accent border border-subtle">
                Sắp xếp theo điểm tương thích
              </span>
            </div>
            <p className="text-[11px] text-secondary">
              AI đánh giá và xếp hạng người dùng thật có tiềm năng hợp tác cao nhất lên đầu
            </p>
          </div>
        </div>
        <div className="hidden sm:flex items-center gap-2 rounded-xl border border-subtle bg-elevated/50 px-3 py-1.5 text-xs text-secondary">
          <Sparkles className="h-3.5 w-3.5 text-accent" />
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
            <div className="lg:hidden fixed inset-0 z-50 bg-app/95 p-4 flex flex-col">
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
            <div className="flex items-start gap-3.5 rounded-2xl border border-subtle bg-surface p-4 shadow-sm">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-accent/15 text-accent">
                <Sparkles className="h-4 w-4" />
              </div>
              <div className="min-w-0 flex-1">
                <h3 className="text-xs font-bold text-primary">
                  Cơ chế xếp hạng và đề xuất người dùng phù hợp
                </h3>
                <p className="mt-0.5 text-xs leading-relaxed text-secondary">
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
