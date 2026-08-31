"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Brain,
  Sparkles,
  MessageSquare,
  Lock,
  Tag as TagIcon,
  Plus,
  X,
  Clock,
  Sliders,
  CheckCircle2,
  Users,
  Database,
  Cpu,
  Layers,
  HelpCircle,
  Activity,
  Workflow,
  Search,
  Check,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { getSystemTags, createSystemTag, getAiConfigs, updateAiConfig } from "@/lib/api/tags";
import { getSettings, updateSettings } from "@/lib/api/settings";
import { useAuthStore } from "@/lib/stores/auth-store";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/hooks/use-language";

type AIHubTab = "overview" | "copilot" | "memory" | "recommendation" | "tags";

const POPULAR_TAGS = [
  "Developer",
  "Designer",
  "AI & Data",
  "Product Manager",
  "Startup & Founder",
  "Marketing",
  "Blockchain",
  "DevOps",
  "Investor",
];

export default function AIHubPage() {
  const user = useAuthStore((s) => s.user);
  const queryClient = useQueryClient();
  const { language } = useLanguage();
  const l = (vi: string, en: string) => language === "en" ? en : vi;

  const [activeTab, setActiveTab] = useState<AIHubTab>("overview");
  const [newTagName, setNewTagName] = useState("");
  const [newTagCategory, setNewTagCategory] = useState("general");
  const [tagSearchQuery, setTagSearchQuery] = useState("");
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  // ── Queries ──
  const { data: tags = [], isLoading: loadingTags } = useQuery({
    queryKey: ["system-tags"],
    queryFn: getSystemTags,
  });

  const { data: settings, isLoading: loadingSettings } = useQuery({
    queryKey: ["my-settings"],
    queryFn: getSettings,
  });

  const { data: configs = [], isLoading: loadingConfigs } = useQuery({
    queryKey: ["system-configs"],
    queryFn: getAiConfigs,
  });

  // ── Mutations ──
  const createTagMutation = useMutation({
    mutationFn: () => createSystemTag(newTagName.trim(), newTagCategory),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["system-tags"] });
      setNewTagName("");
      showToast(l("Đã thêm thẻ mới thành công!", "Tag added successfully!"));
    },
    onError: () => {
      showToast(l("Lỗi khi thêm thẻ. Vui lòng thử lại!", "Could not add the tag. Please try again!"));
    }
  });

  const deleteTagMutation = useMutation({
    mutationFn: async (tagId: string) => {
      const res = await fetch(`/api/proxy/api/v1/tags/${tagId}`, { method: "DELETE" });
      if (!res.ok) throw new Error("Failed to delete tag");
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["system-tags"] });
      showToast(l("Đã xóa thẻ!", "Tag deleted!"));
    },
  });

  const updateSettingsMutation = useMutation({
    mutationFn: (data: any) => updateSettings(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["my-settings"] });
      showToast(l("Cập nhật cài đặt AI thành công!", "AI settings updated successfully!"));
    },
    onError: () => {
      showToast(l("Lỗi khi lưu cài đặt. Vui lòng thử lại!", "Could not save settings. Please try again!"));
    }
  });

  const updateConfigMutation = useMutation({
    mutationFn: (data: { key: string; value: any; desc?: string }) =>
      updateAiConfig(data.key, data.value, data.desc),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["system-configs"] });
      showToast(l("Cập nhật cấu hình hệ thống AI thành công!", "AI system configuration updated successfully!"));
    },
  });

  const handleUpdateSetting = (key: string, value: any) => {
    updateSettingsMutation.mutate({ [key]: value });
  };

  const handleCreateTag = (e: React.FormEvent) => {
    e.preventDefault();
    if (newTagName.trim()) {
      createTagMutation.mutate();
    }
  };

  // Helper configs
  const aiSettingsConfig = configs.find((c: any) => c.key === "ai_settings");
  const defaultSettings = {
    features: {
      copilot: true,
      recommendation: true,
      memory: true,
      tagging: true,
    },
    tag_limit: 3,
    min_matching_score: 50,
  };

  const currentConfigs = aiSettingsConfig?.value
    ? {
        ...defaultSettings,
        ...aiSettingsConfig.value,
        features: {
          ...defaultSettings.features,
          ...(aiSettingsConfig.value.features || {}),
        },
      }
    : defaultSettings;

  const updateConfigSetting = (key: string, value: any, isFeature: boolean = false) => {
    const newSettings = { ...currentConfigs };
    if (isFeature) {
      newSettings.features[key] = value;
    } else {
      newSettings[key] = value;
    }
    updateConfigMutation.mutate({
      key: "ai_settings",
      value: newSettings,
      desc: "Global AI Settings",
    });
  };

  const filteredTags = tags.filter((t: any) =>
    t.name.toLowerCase().includes(tagSearchQuery.toLowerCase())
  );

  const TABS = [
    { id: "overview", label: l("Tổng quan & Quyền riêng tư", "Overview & Privacy"), icon: Brain, desc: l("Cài đặt chung, bảo mật & mô hình AI", "General, privacy, and AI model settings") },
    { id: "copilot", label: "AI Copilot", icon: Sparkles, desc: l("Trợ lý gợi ý câu trả lời trong hội thoại", "Suggested replies and in-chat assistance") },
    { id: "memory", label: l("Trí nhớ AI (Memory)", "AI Memory"), icon: Database, desc: l("Tự động ghi nhớ và thấu hiểu người dùng", "Automatically remember and understand users") },
    { id: "recommendation", label: l("Gợi ý kết nối (Matchmaker)", "Connection Suggestions"), icon: Users, desc: l("Thuật toán tìm kiếm bạn bè & đối tác", "Find compatible friends and partners") },
    { id: "tags", label: l("Hệ thống Thẻ (Taxonomy)", "Tag System (Taxonomy)"), icon: TagIcon, desc: l("Quản lý nhãn phân loại người dùng", "Manage user classification labels") },
  ] as const;

  return (
    <main className="ai-hub-page flex-1 overflow-y-auto bg-background p-6 md:p-10">
      <div className="mx-auto max-w-5xl space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-200 pb-5">
          <div>
            <div className="flex items-center gap-2.5">
              <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-accent shadow-md shadow-accent/20 text-accent-foreground">
                <Brain className="h-6 w-6" />
              </div>
              <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
                {l("AI Hub & Trợ lý Thông minh", "AI Hub & Intelligent Assistant")}
              </h1>
            </div>
            <p className="text-sm text-slate-500 mt-1.5 leading-relaxed">
              {l("Cấu hình chuyên sâu mô hình AI, Bộ nhớ Memory, Copilot, Gợi ý kết nối & Hệ thống phân loại dữ liệu.", "Configure AI models, Memory, Copilot, connection suggestions, and data classification.")}
            </p>
          </div>

          {/* Engine Status Badges */}
          <div className="flex items-center gap-2 flex-wrap">
            <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 border border-emerald-200 px-3 py-1 text-xs font-semibold text-emerald-700 shadow-2xs">
              <Activity size={12} className="text-emerald-600 animate-pulse" />
              {l("LangGraph Engine đang hoạt động", "LangGraph Engine Active")}
            </span>
            <span className="inline-flex items-center gap-1.5 rounded-full bg-accent/10 border border-accent/30 px-3 py-1 text-xs font-semibold text-accent shadow-2xs">
              <Cpu size={12} className="text-accent" />
              Qdrant Vector DB
            </span>
          </div>
        </div>

        {/* Global Toast */}
        {toastMessage && (
          <div className="fixed bottom-6 right-6 z-50 flex items-center gap-2.5 rounded-2xl bg-slate-900 text-white px-5 py-3.5 shadow-xl border border-slate-700 animate-in fade-in slide-in-from-bottom-5">
            <CheckCircle2 size={18} className="text-emerald-400" />
            <span className="text-sm font-medium">{toastMessage}</span>
          </div>
        )}

        {/* Main Grid: Sidebar Tabs + Content Panel */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-start">
          {/* Navigation Sidebar */}
          <div className="md:col-span-4 space-y-2">
            <Card className="rounded-3xl border-slate-100 bg-white p-2.5 shadow-sm space-y-1">
              {TABS.map((tab) => {
                const Icon = tab.icon;
                const active = activeTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    type="button"
                    onClick={() => setActiveTab(tab.id as AIHubTab)}
                    className={cn(
                      "w-full flex items-start gap-3.5 p-3 rounded-2xl text-left transition-all duration-200 cursor-pointer",
                      active
                        ? "bg-accent text-accent-foreground shadow-md shadow-accent/20"
                        : "hover:bg-slate-100/80 text-slate-700"
                    )}
                  >
                    <div className={cn(
                      "p-2 rounded-xl shrink-0 transition-colors",
                      active ? "bg-white/15 text-white" : "bg-slate-100 text-slate-600"
                    )}>
                      <Icon size={18} />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className={cn("text-sm font-bold truncate", active ? "text-accent-foreground" : "text-slate-900")}>
                        {tab.label}
                      </p>
                      <p className={cn("text-xs truncate mt-0.5", active ? "text-accent-foreground/80" : "text-slate-500")}>
                        {tab.desc}
                      </p>
                    </div>
                  </button>
                );
              })}
            </Card>

            {/* Quick Engine Info Card */}
            <Card className="rounded-3xl border-slate-100 bg-gradient-to-br from-slate-900 to-slate-800 p-5 text-white shadow-sm space-y-3">
              <div className="flex items-center gap-2 text-accent">
                <Workflow size={16} />
                <span className="text-xs font-bold uppercase tracking-wider">{l("Kiến trúc AI 5 Bước", "5-Step AI Architecture")}</span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                {l("Hệ thống kết hợp SQL Hard Filter, Vector Search (Qdrant), Feature Engineering 5 trọng số, và LLM Re-ranker để đưa ra gợi ý chuẩn xác nhất.", "The system combines SQL hard filters, Qdrant vector search, five-factor feature engineering, and an LLM re-ranker for precise suggestions.")}
              </p>
              <div className="pt-2 border-t border-slate-700/60 flex items-center justify-between text-[11px] text-slate-400">
                <span>{l("Trạng thái: Ổn định", "Status: Stable")}</span>
                <span className="text-emerald-400 font-semibold">{l("100% Sẵn sàng", "100% Ready")}</span>
              </div>
            </Card>
          </div>

          {/* Right Content Area */}
          <div className="md:col-span-8 space-y-6">
            {loadingSettings || loadingConfigs ? (
              <Card className="rounded-3xl border-slate-100 bg-white p-8 space-y-6">
                <Skeleton className="h-7 w-48 rounded-xl" />
                <Skeleton className="h-16 w-full rounded-2xl" />
                <Skeleton className="h-16 w-full rounded-2xl" />
              </Card>
            ) : null}

            {/* ================================================================= */}
            {/* TAB 1: TỔNG QUAN & QUYỀN RIÊNG TƯ */}
            {/* ================================================================= */}
            {!loadingSettings && !loadingConfigs && activeTab === "overview" && (
              <div className="space-y-6">
                <Card className="rounded-3xl border-slate-100 bg-white p-6 md:p-8 space-y-6 shadow-sm">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-4">
                    <h2 className="text-base font-bold text-slate-800 flex items-center gap-2">
                      <Brain size={18} className="text-accent" />
                      {l("Quyền riêng tư & Kích hoạt AI Tổng", "Privacy & Master AI Controls")}
                    </h2>
                    <Badge variant="outline" className="text-xs border-accent/30 text-accent bg-accent/10">
                      Core Privacy
                    </Badge>
                  </div>

                  {/* Master AI Assistant Toggle */}
                  <div className="flex items-center justify-between gap-4 p-5 rounded-2xl bg-accent/5 border border-accent/20">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <Sparkles size={18} className="text-accent" />
                        <p className="text-sm font-bold text-slate-900">{l("Kích hoạt Trợ lý AI (Master AI Switch)", "Enable AI Assistant (Master Switch)")}</p>
                      </div>
                      <p className="text-xs text-slate-600 leading-relaxed">
                        {l("Bật/tắt toàn bộ tính năng AI (Copilot, gợi ý tin nhắn, matchmaker, tự động phân tích trí nhớ).", "Enable or disable all AI features, including Copilot, reply suggestions, Matchmaker, and automatic memory analysis.")}
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer shrink-0">
                      <input
                        type="checkbox"
                        className="sr-only peer"
                        checked={settings?.ai_enabled !== false}
                        onChange={(e) => handleUpdateSetting("ai_enabled", e.target.checked)}
                      />
                      <div className="w-12 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600 shadow-inner"></div>
                    </label>
                  </div>

                  {settings?.ai_enabled !== false && (
                    <>
                      {/* TOGGLE CHO PHÉP AI TRÍCH XUẤT ĐOẠN CHAT */}
                      <div className="flex items-center justify-between gap-4 p-5 rounded-2xl bg-slate-50 border border-slate-200/80">
                        <div className="space-y-1 max-w-md">
                          <div className="flex items-center gap-2">
                            <MessageSquare size={16} className="text-blue-600" />
                            <p className="text-sm font-bold text-slate-900">
                              {l("Cho phép AI trích xuất phân tích đoạn chat", "Allow AI to analyze chat content")}
                            </p>
                          </div>
                          <p className="text-xs text-slate-500 leading-relaxed">
                            {settings?.ai_extract_chat !== false
                              ? l("BẬT: Trợ lý AI và Memory Worker sẽ học hỏi thông tin quan trọng từ hội thoại để trợ giúp bạn nhanh chóng.", "ON: The AI Assistant and Memory Worker can learn important information from conversations to assist you faster.")
                              : l("TẮT (Bảo mật tối đa): AI bị khóa hoàn toàn quyền đọc và trích xuất tin nhắn chat của bạn.", "OFF (Maximum privacy): AI cannot read or extract content from your chat messages.")}
                          </p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer shrink-0">
                          <input
                            type="checkbox"
                            className="sr-only peer"
                            checked={settings?.ai_extract_chat !== false}
                            onChange={(e) => handleUpdateSetting("ai_extract_chat", e.target.checked)}
                          />
                          <div className="w-12 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600 shadow-inner"></div>
                        </label>
                      </div>

                      {/* Allow AI to Read Profile */}
                      <div className="flex items-center justify-between gap-4 p-4 rounded-2xl bg-white border border-slate-100 hover:border-slate-200 transition-colors">
                        <div className="space-y-0.5">
                          <p className="text-sm font-semibold text-slate-800">{l("Cho phép AI đọc Hồ sơ cá nhân (Profile Matching)", "Allow AI to read your profile (Profile Matching)")}</p>
                          <p className="text-xs text-slate-500">
                            {l("Cho phép thuật toán AI Matchmaker đọc kỹ năng, kinh nghiệm để gợi ý bạn bè và đối tác phù hợp.", "Allow AI Matchmaker to use your skills and experience to suggest compatible friends and partners.")}
                          </p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer shrink-0">
                          <input
                            type="checkbox"
                            className="sr-only peer"
                            checked={settings?.ai_read_profile !== false}
                            onChange={(e) => handleUpdateSetting("ai_read_profile", e.target.checked)}
                          />
                          <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600 shadow-inner"></div>
                        </label>
                      </div>
                    </>
                  )}
                </Card>
              </div>
            )}

            {/* ================================================================= */}
            {/* TAB 2: AI COPILOT */}
            {/* ================================================================= */}
            {!loadingSettings && !loadingConfigs && activeTab === "copilot" && (
              <div className="space-y-6">
                <Card className="rounded-3xl border-slate-100 bg-white p-6 md:p-8 space-y-6 shadow-sm">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-4">
                    <h2 className="text-base font-bold text-slate-800 flex items-center gap-2">
                      <Sparkles size={18} className="text-blue-600" />
                      {l("Cấu hình AI Copilot (Trợ lý trò chuyện)", "AI Copilot Configuration")}
                    </h2>
                    <Badge variant="outline" className="text-xs border-indigo-200 text-indigo-700 bg-indigo-50">
                      In-chat Assistant
                    </Badge>
                  </div>

                  {/* Enable AI Copilot Feature */}
                  <div className="flex items-center justify-between gap-4 p-4 rounded-2xl bg-slate-50 border border-slate-200/80">
                    <div className="space-y-0.5">
                      <p className="text-sm font-bold text-slate-900">{l("Bật AI Copilot trong cửa sổ chat", "Enable AI Copilot in chats")}</p>
                      <p className="text-xs text-slate-500">
                        {l("Hiển thị thanh công cụ Copilot bên cạnh khung trò chuyện để tóm tắt và hỗ trợ phản hồi.", "Show Copilot beside conversations for summaries and reply assistance.")}
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer shrink-0">
                      <input
                        type="checkbox"
                        className="sr-only peer"
                        checked={currentConfigs.features.copilot}
                        onChange={(e) => updateConfigSetting("copilot", e.target.checked, true)}
                      />
                      <div className="w-12 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600 shadow-inner"></div>
                    </label>
                  </div>

                  {currentConfigs.features.copilot && (
                    <>
                      {/* Context Turns */}
                      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 p-4 rounded-2xl bg-white border border-slate-100">
                        <div className="space-y-0.5">
                          <p className="text-sm font-semibold text-slate-800">{l("Số tin nhắn ngữ cảnh (Context Turns)", "Context Messages")}</p>
                          <p className="text-xs text-slate-500">
                            {l("Số lượng tin nhắn gần nhất AI Copilot tham khảo để hiểu ngữ cảnh cuộc trò chuyện.", "The number of recent messages AI Copilot uses to understand the conversation.")}
                          </p>
                        </div>
                        <select
                          value={settings?.ai_copilot_context_turns ?? 10}
                          onChange={(e) => handleUpdateSetting("ai_copilot_context_turns", parseInt(e.target.value))}
                          className="h-10 rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-1.5 text-xs font-semibold text-slate-700 focus:border-blue-500 focus:outline-none shadow-xs"
                        >
                          <option value="5">{l("5 tin nhắn gần nhất", "5 recent messages")}</option>
                          <option value="10">{l("10 tin nhắn (Mặc định)", "10 messages (Default)")}</option>
                          <option value="20">{l("20 tin nhắn", "20 messages")}</option>
                          <option value="50">{l("50 tin nhắn", "50 messages")}</option>
                          <option value="0">{l("Toàn bộ cuộc trò chuyện", "Entire conversation")}</option>
                        </select>
                      </div>

                      {/* Smart Reply Suggestion */}
                      <div className="flex items-center justify-between gap-4 p-4 rounded-2xl bg-white border border-slate-100">
                        <div className="space-y-0.5">
                          <p className="text-sm font-semibold text-slate-800">{l("Gợi ý câu trả lời thông minh (Smart Reply)", "Smart Reply Suggestions")}</p>
                          <p className="text-xs text-slate-500">
                            {l("Tự động đưa ra các câu trả lời ngắn phù hợp ngay khi nhận tin nhắn mới.", "Automatically suggest short, relevant replies when new messages arrive.")}
                          </p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer shrink-0">
                          <input
                            type="checkbox"
                            className="sr-only peer"
                            checked={currentConfigs.features.reply_suggestions !== false}
                            onChange={(e) => updateConfigSetting("reply_suggestions", e.target.checked, true)}
                          />
                          <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600 shadow-inner"></div>
                        </label>
                      </div>
                    </>
                  )}
                </Card>
              </div>
            )}

            {/* ================================================================= */}
            {/* TAB 3: TRÍ NHỚ AI (MEMORY) */}
            {/* ================================================================= */}
            {!loadingSettings && !loadingConfigs && activeTab === "memory" && (
              <div className="space-y-6">
                <Card className="rounded-3xl border-slate-100 bg-white p-6 md:p-8 space-y-6 shadow-sm">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-4">
                    <h2 className="text-base font-bold text-slate-800 flex items-center gap-2">
                      <Database size={18} className="text-blue-600" />
                      {l("Cấu hình Bộ nhớ AI (Memory Engine)", "AI Memory Configuration")}
                    </h2>
                    <Badge variant="outline" className="text-xs border-amber-200 text-amber-700 bg-amber-50">
                      Long-term Memory
                    </Badge>
                  </div>

                  {/* Enable AI Memory */}
                  <div className="flex items-center justify-between gap-4 p-4 rounded-2xl bg-slate-50 border border-slate-200/80">
                    <div className="space-y-0.5">
                      <p className="text-sm font-bold text-slate-900">{l("Kích hoạt AI Memory", "Enable AI Memory")}</p>
                      <p className="text-xs text-slate-500">
                        {l("Cho phép hệ thống lưu trữ và trích xuất thực thể, điểm quan tâm, thông tin liên lạc.", "Allow the system to store and retrieve entities, interests, and contact information.")}
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer shrink-0">
                      <input
                        type="checkbox"
                        className="sr-only peer"
                        checked={currentConfigs.features.memory}
                        onChange={(e) => updateConfigSetting("memory", e.target.checked, true)}
                      />
                      <div className="w-12 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600 shadow-inner"></div>
                    </label>
                  </div>

                  {currentConfigs.features.memory && (
                    <>
                      {/* Memory Refresh Interval */}
                      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 p-4 rounded-2xl bg-white border border-slate-100">
                        <div className="space-y-0.5">
                          <p className="text-sm font-semibold text-slate-800">{l("Chu kỳ cập nhật Trí nhớ (Refresh Interval)", "Memory Refresh Interval")}</p>
                          <p className="text-xs text-slate-500">{l("Tần suất hệ thống tổng hợp thông tin mới từ tin nhắn.", "How often the system extracts new information from messages.")}</p>
                        </div>
                        <select
                          value={settings?.ai_memory_refresh_interval || "realtime"}
                          onChange={(e) => handleUpdateSetting("ai_memory_refresh_interval", e.target.value)}
                          className="h-10 rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-1.5 text-xs font-semibold text-slate-700 focus:border-blue-500 focus:outline-none shadow-xs"
                        >
                          <option value="realtime">{l("Tức thì (Realtime)", "Immediately (Real-time)")}</option>
                          <option value="5_mins">{l("Mỗi 5 phút sau khi chat", "Every 5 minutes after chatting")}</option>
                          <option value="hourly">{l("Hàng giờ", "Hourly")}</option>
                          <option value="daily">{l("Hàng ngày", "Daily")}</option>
                          <option value="weekly">{l("Hàng tuần", "Weekly")}</option>
                        </select>
                      </div>

                      {/* Analysis Window */}
                      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 p-4 rounded-2xl bg-white border border-slate-100">
                        <div className="space-y-0.5">
                          <p className="text-sm font-semibold text-slate-800">{l("Cửa sổ thời gian phân tích (Analysis Window)", "Analysis Window")}</p>
                          <p className="text-xs text-slate-500">{l("Khoảng thời gian tin nhắn tối đa được AI phân tích vào bộ nhớ.", "The maximum message history period analyzed for memory.")}</p>
                        </div>
                        <select
                          value={settings?.ai_memory_window || "1m"}
                          onChange={(e) => handleUpdateSetting("ai_memory_window", e.target.value)}
                          className="h-10 rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-1.5 text-xs font-semibold text-slate-700 focus:border-blue-500 focus:outline-none shadow-xs"
                        >
                          <option value="1d">{l("1 ngày gần nhất", "Last day")}</option>
                          <option value="1w">{l("1 tuần gần nhất", "Last week")}</option>
                          <option value="1m">{l("1 tháng gần nhất (Mặc định)", "Last month (Default)")}</option>
                          <option value="3m">{l("3 tháng gần nhất", "Last 3 months")}</option>
                          <option value="6m">{l("6 tháng gần nhất", "Last 6 months")}</option>
                          <option value="1y">{l("1 năm gần nhất", "Last year")}</option>
                        </select>
                      </div>
                    </>
                  )}
                </Card>
              </div>
            )}

            {/* ================================================================= */}
            {/* TAB 4: GỢI Ý KẾT NỐI (RECOMMENDATION) */}
            {/* ================================================================= */}
            {!loadingSettings && !loadingConfigs && activeTab === "recommendation" && (
              <div className="space-y-6">
                <Card className="rounded-3xl border-slate-100 bg-white p-6 md:p-8 space-y-6 shadow-sm">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-4">
                    <h2 className="text-base font-bold text-slate-800 flex items-center gap-2">
                      <Users size={18} className="text-blue-600" />
                      {l("Gợi ý kết nối thông minh (AI Matchmaker)", "Intelligent Connection Suggestions (AI Matchmaker)")}
                    </h2>
                    <Badge variant="outline" className="text-xs border-emerald-200 text-emerald-700 bg-emerald-50">
                      Multi-Stage Pipeline
                    </Badge>
                  </div>

                  {/* Enable AI Recommendation */}
                  <div className="flex items-center justify-between gap-4 p-4 rounded-2xl bg-slate-50 border border-slate-200/80">
                    <div className="space-y-0.5">
                      <p className="text-sm font-bold text-slate-900">{l("Kích hoạt AI Recommendation", "Enable AI Recommendations")}</p>
                      <p className="text-xs text-slate-500">
                        {l("Tự động tìm kiếm và gợi ý bạn bè, đối tác phù hợp dựa trên kỹ năng, sở thích và vị trí.", "Automatically suggest compatible friends and partners based on skills, interests, and location.")}
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer shrink-0">
                      <input
                        type="checkbox"
                        className="sr-only peer"
                        checked={currentConfigs.features.recommendation}
                        onChange={(e) => updateConfigSetting("recommendation", e.target.checked, true)}
                      />
                      <div className="w-12 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600 shadow-inner"></div>
                    </label>
                  </div>

                  {currentConfigs.features.recommendation && (
                    <>
                      {/* Notification Interval */}
                      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 p-4 rounded-2xl bg-white border border-slate-100">
                        <div className="space-y-0.5">
                          <p className="text-sm font-semibold text-slate-800">{l("Tần suất thông báo gợi ý kết nối", "Connection Suggestion Frequency")}</p>
                          <p className="text-xs text-slate-500">{l("Khoảng thời gian cách nhau giữa các lần thông báo matching.", "Time between Matchmaker notifications.")}</p>
                        </div>
                        <select
                          value={currentConfigs.notification_interval || "24h"}
                          onChange={(e) => {
                            updateConfigSetting("notification_interval", e.target.value);
                            handleUpdateSetting("ai_recommendation_interval", e.target.value);
                          }}
                          className="h-10 rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-1.5 text-xs font-semibold text-slate-700 focus:border-blue-500 focus:outline-none shadow-xs"
                        >
                          <option value="realtime">{l("Ngay khi phát hiện (Realtime)", "As detected (Real-time)")}</option>
                          <option value="1h">{l("Mỗi 1 giờ", "Every hour")}</option>
                          <option value="6h">{l("Mỗi 6 giờ", "Every 6 hours")}</option>
                          <option value="12h">{l("Mỗi 12 giờ", "Every 12 hours")}</option>
                          <option value="24h">{l("Hàng ngày (24 giờ - Đề xuất)", "Daily (24 hours - Recommended)")}</option>
                          <option value="weekly">{l("Hàng tuần", "Weekly")}</option>
                          <option value="off">{l("Tắt thông báo", "Notifications off")}</option>
                        </select>
                      </div>

                      {/* Minimum Matching Score */}
                      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 p-4 rounded-2xl bg-white border border-slate-100">
                        <div className="space-y-0.5">
                          <p className="text-sm font-semibold text-slate-800">{l("Ngưỡng % tương thích tối thiểu", "Minimum Compatibility Score")}</p>
                          <p className="text-xs text-slate-500">{l("Chỉ gửi thông báo kết nối khi độ tương thích đạt từ mức này.", "Only notify you when compatibility meets this threshold.")}</p>
                        </div>
                        <select
                          value={currentConfigs.min_matching_score || 50}
                          onChange={(e) => updateConfigSetting("min_matching_score", parseInt(e.target.value))}
                          className="h-10 rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-1.5 text-xs font-semibold text-slate-700 focus:border-blue-500 focus:outline-none shadow-xs"
                        >
                          <option value="50">{l("50% (Tiêu chuẩn)", "50% (Standard)")}</option>
                          <option value="60">{l("60% (Phù hợp khá)", "60% (Good fit)")}</option>
                          <option value="70">{l("70% (Tương thích cao)", "70% (High compatibility)")}</option>
                          <option value="80">{l("80% (Rất cao)", "80% (Very high)")}</option>
                          <option value="90">{l("90% (Tuyệt đối)", "90% (Exceptional)")}</option>
                        </select>
                      </div>
                    </>
                  )}
                </Card>
              </div>
            )}

            {/* ================================================================= */}
            {/* TAB 5: HỆ THỐNG GẮN THẺ & TAXONOMY (TAGS) */}
            {/* ================================================================= */}
            {!loadingSettings && !loadingConfigs && activeTab === "tags" && (
              <div className="space-y-6">
                <Card className="rounded-3xl border-slate-100 bg-white p-6 md:p-8 space-y-6 shadow-sm">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-4">
                    <h2 className="text-base font-bold text-slate-800 flex items-center gap-2">
                      <TagIcon size={18} className="text-blue-600" />
                      {l("Quản lý Thẻ phân loại (AI Taxonomy & Tags)", "Classification Tags (AI Taxonomy & Tags)")}
                    </h2>
                    <Badge variant="outline" className="text-xs border-purple-200 text-purple-700 bg-purple-50">
                      {tags.length} {l("Thẻ hoạt động", "Active Tags")}
                    </Badge>
                  </div>

                  {/* Enable AI Tagging & Limit */}
                  <div className="space-y-4">
                    <div className="flex items-center justify-between gap-4 p-4 rounded-2xl bg-slate-50 border border-slate-200/80">
                      <div className="space-y-0.5">
                        <p className="text-sm font-bold text-slate-900">{l("Kích hoạt AI Tagging tự động", "Enable Automatic AI Tagging")}</p>
                        <p className="text-xs text-slate-500">
                          {l("Tự động gắn thẻ phân loại cho cuộc trò chuyện và hồ sơ.", "Automatically classify conversations and profiles with tags.")}
                        </p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer shrink-0">
                        <input
                          type="checkbox"
                          className="sr-only peer"
                          checked={currentConfigs.features.tagging}
                          onChange={(e) => updateConfigSetting("tagging", e.target.checked, true)}
                        />
                        <div className="w-12 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600 shadow-inner"></div>
                      </label>
                    </div>

                    {currentConfigs.features.tagging && (
                      <div className="flex items-center justify-between gap-4 p-4 rounded-2xl bg-white border border-slate-100">
                        <div className="space-y-0.5">
                          <p className="text-sm font-semibold text-slate-800">{l("Số lượng thẻ đề xuất tối đa", "Maximum Suggested Tags")}</p>
                          <p className="text-xs text-slate-500">{l("Giới hạn số tag AI gắn cho mỗi đối tượng.", "Limit the number of AI tags assigned to each item.")}</p>
                        </div>
                        <input
                          type="number"
                          min="1"
                          max="10"
                          value={currentConfigs.tag_limit || 3}
                          onChange={(e) => updateConfigSetting("tag_limit", parseInt(e.target.value) || 3)}
                          className="w-16 h-10 rounded-xl border border-slate-200 bg-slate-50 text-center font-bold text-sm text-slate-800 focus:border-blue-500 focus:outline-none shadow-xs"
                        />
                      </div>
                    )}
                  </div>

                  <hr className="border-slate-100" />

                  {/* Add Tag Form */}
                  <div className="space-y-3">
                    <p className="text-sm font-bold text-slate-900">{l("Thêm thẻ mới (Create Tag)", "Create Tag")}</p>
                    <form onSubmit={handleCreateTag} className="flex flex-col sm:flex-row gap-3">
                      <Input
                        type="text"
                        placeholder={l("Tên thẻ mới (vd: Frontend, AI Engineer, Blockchain...)", "New tag name (e.g. Frontend, AI Engineer, Blockchain...)")}
                        value={newTagName}
                        onChange={(e) => setNewTagName(e.target.value)}
                        className="h-11 rounded-2xl border-slate-200 bg-slate-50 text-sm focus:border-blue-500"
                      />
                      <Button
                        type="submit"
                        disabled={createTagMutation.isPending || !newTagName.trim()}
                        className="h-11 rounded-2xl px-6 bg-blue-600 hover:bg-blue-700 text-white font-semibold shrink-0 shadow-sm"
                      >
                        <Plus size={16} className="mr-1.5" />
                        {createTagMutation.isPending ? l("Đang thêm...", "Adding...") : l("Thêm thẻ", "Add Tag")}
                      </Button>
                    </form>

                    {/* Popular Quick Suggestions */}
                    <div className="pt-2">
                      <p className="text-xs font-semibold text-slate-400 mb-2">{l("Gợi ý thẻ phổ biến:", "Popular tag suggestions:")}</p>
                      <div className="flex flex-wrap gap-1.5">
                        {POPULAR_TAGS.map((popTag) => (
                          <button
                            key={popTag}
                            type="button"
                            onClick={() => setNewTagName(popTag)}
                            className="text-xs px-2.5 py-1 rounded-xl bg-slate-100 text-slate-600 hover:bg-blue-50 hover:text-blue-600 transition-colors border border-slate-200/60"
                          >
                            + #{popTag}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>

                  <hr className="border-slate-100" />

                  {/* Tag List & Search */}
                  <div className="space-y-4">
                    <div className="flex items-center justify-between gap-3">
                      <p className="text-sm font-bold text-slate-900">{l("Danh sách thẻ của bạn", "Your Tags")}</p>
                      <div className="relative w-48 sm:w-64">
                        <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                        <Input
                          type="search"
                          placeholder={l("Tìm thẻ...", "Search tags...")}
                          value={tagSearchQuery}
                          onChange={(e) => setTagSearchQuery(e.target.value)}
                          className="h-8.5 pl-8 text-xs rounded-xl bg-slate-50 border-slate-200"
                        />
                      </div>
                    </div>

                    {loadingTags ? (
                      <div className="flex gap-2">
                        <Skeleton className="h-8 w-20 rounded-xl" />
                        <Skeleton className="h-8 w-24 rounded-xl" />
                        <Skeleton className="h-8 w-16 rounded-xl" />
                      </div>
                    ) : filteredTags.length === 0 ? (
                      <p className="text-xs text-slate-400 italic py-3 text-center">
                        {tagSearchQuery ? l("Không tìm thấy thẻ phù hợp.", "No matching tags found.") : l("Chưa có thẻ nào. Hãy tạo thẻ đầu tiên!", "No tags yet. Create your first tag!")}
                      </p>
                    ) : (
                      <div className="flex flex-wrap gap-2.5 pt-1">
                        {filteredTags.map((tag: any) => (
                          <Badge
                            key={tag.id}
                            variant="secondary"
                            className="pl-3.5 pr-2 py-1.5 text-xs font-semibold bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-200/80 gap-2 shadow-2xs rounded-xl transition-all"
                          >
                            <span>#{tag.name}</span>
                            <button
                              type="button"
                              onClick={() => deleteTagMutation.mutate(tag.id)}
                              disabled={deleteTagMutation.isPending}
                              className="rounded-full p-0.5 text-blue-400 hover:text-red-600 hover:bg-blue-200/60 transition-colors"
                              title={l("Xóa thẻ", "Delete tag")}
                            >
                              <X size={13} />
                            </button>
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>
                </Card>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
