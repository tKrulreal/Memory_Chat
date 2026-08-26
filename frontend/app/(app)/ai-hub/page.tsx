"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Brain, Settings, Tag as TagIcon, Plus, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { getSystemTags, createSystemTag, getAiConfigs, updateAiConfig } from "@/lib/api/tags";
import { getSettings, updateSettings } from "@/lib/api/settings";
import { useAuthStore } from "@/lib/stores/auth-store";

export default function AIHubPage() {
  const user = useAuthStore((s) => s.user);
  const queryClient = useQueryClient();

  const [newTagName, setNewTagName] = useState("");

  const { data: tags = [], isLoading: loadingTags } = useQuery({
    queryKey: ["system-tags"],
    queryFn: getSystemTags,
  });

  const { data: settings, isLoading: loadingSettings, isError: settingsError } = useQuery({
    queryKey: ["my-settings"],
    queryFn: getSettings,
  });

  const { data: configs = [], isLoading: loadingConfigs, isError: configsError } = useQuery({
    queryKey: ["system-configs"],
    queryFn: getAiConfigs,
  });

  const createTagMutation = useMutation({
    mutationFn: () => createSystemTag(newTagName, ""),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["system-tags"] });
      setNewTagName("");
    },
  });

  const deleteTagMutation = useMutation({
    mutationFn: async (tagId: string) => {
      const res = await fetch(`/api/proxy/api/v1/tags/${tagId}`, { method: "DELETE" });
      if (!res.ok) throw new Error("Failed to delete tag");
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["system-tags"] });
    },
  });

  const updateSettingsMutation = useMutation({
    mutationFn: (data: any) => updateSettings(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["my-settings"] });
    },
  });

  const updateConfigMutation = useMutation({
    mutationFn: (data: { key: string, value: any, desc?: string }) => 
      updateAiConfig(data.key, data.value, data.desc),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["system-configs"] });
    },
  });

  const handleCreateTag = (e: React.FormEvent) => {
    e.preventDefault();
    if (newTagName.trim()) {
      createTagMutation.mutate();
    }
  };

  const handleUpdateSetting = (key: string, value: any) => {
    updateSettingsMutation.mutate({ [key]: value });
  };

  return (
    <main className="flex-1 overflow-y-auto bg-slate-50 p-6 md:p-10">
      <div className="mx-auto max-w-5xl space-y-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
            <Brain className="h-7 w-7 text-blue-600" />
            AI Hub
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Manage your personal AI rules, personality, and taxonomy.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Tags Section */}
          <Card className="rounded-3xl border-slate-100 bg-white p-6 md:p-8 space-y-5 shadow-sm">
            <h2 className="text-lg font-bold text-slate-800 border-b border-slate-100 pb-4 flex items-center gap-2">
              <TagIcon size={20} className="text-blue-600" />
              My AI Tags
            </h2>

            <form onSubmit={handleCreateTag} className="flex gap-3">
              <input
                type="text"
                placeholder="Tag name"
                value={newTagName}
                onChange={(e) => setNewTagName(e.target.value)}
                className="flex-1 rounded-xl border border-slate-200 bg-slate-50 px-4 py-2 text-sm text-slate-800 font-medium focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500/30"
              />
              <Button type="submit" disabled={createTagMutation.isPending || !newTagName.trim()} size="default" className="rounded-xl shadow-sm">
                <Plus size={16} className="mr-1.5" /> Add
              </Button>
            </form>

            <div className="mt-6 space-y-3">
              {loadingTags ? (
                <p className="text-sm text-slate-500">Loading...</p>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {tags.map((tag: any) => (
                    <Badge key={tag.id} variant="secondary" className="pl-3 pr-1.5 py-1 text-xs font-semibold bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-200 gap-1.5 shadow-sm">
                      {tag.name}
                      <button
                        type="button"
                        onClick={() => deleteTagMutation.mutate(tag.id)}
                        disabled={deleteTagMutation.isPending}
                        className="rounded-full p-0.5 text-blue-500 hover:text-blue-800 hover:bg-blue-200 transition-colors"
                      >
                        <X size={12} />
                      </button>
                    </Badge>
                  ))}
                </div>
              )}
            </div>
          </Card>

          {/* AI Settings Section */}
          <Card className="rounded-3xl border-slate-100 bg-white p-6 md:p-8 space-y-6 shadow-sm">
            <h2 className="text-lg font-bold text-slate-800 border-b border-slate-100 pb-4 flex items-center gap-2">
              <Settings size={20} className="text-blue-600" />
              AI Settings
            </h2>
            
            <div className="space-y-6">
              {loadingSettings || loadingConfigs ? (
                <p className="text-sm text-slate-500">Loading...</p>
              ) : settingsError || configsError ? (
                <p className="text-sm text-red-500">Could not load AI settings. Please check your connection and try again.</p>
              ) : !settings ? (
                <p className="text-sm text-slate-500">No settings found.</p>
              ) : (
                (() => {
                  // Setup old configs
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
                  
                  const oldConfigs = aiSettingsConfig?.value ? 
                    { ...defaultSettings, ...aiSettingsConfig.value, features: { ...defaultSettings.features, ...(aiSettingsConfig.value.features || {}) } } 
                    : defaultSettings;
  
                  const updateConfigSetting = (key: string, value: any, isFeature: boolean = false) => {
                    const newSettings = { ...oldConfigs };
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

                  return (
                    <div className="space-y-6">
                      {/* --- MASTER AI ASSISTANT TOGGLE --- */}
                      <div className="space-y-3">
                        <h3 className="font-semibold text-sm text-slate-800">AI Assistant</h3>
                        
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-slate-500">Enable AI Assistant</span>
                          <label className="relative inline-flex items-center cursor-pointer">
                            <input 
                              type="checkbox" 
                              className="sr-only peer" 
                              checked={settings.ai_enabled}
                              onChange={(e) => handleUpdateSetting("ai_enabled", e.target.checked)}
                            />
                            <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-500"></div>
                          </label>
                        </div>

                        <div className="flex items-center justify-between">
                          <div className="space-y-0.5">
                            <span className="text-sm text-slate-700 font-medium">Cho phép AI trích xuất đoạn chat</span>
                            <p className="text-[11px] text-slate-400">Phân tích tin nhắn để học thói quen và thông tin</p>
                          </div>
                          <label className="relative inline-flex items-center cursor-pointer">
                            <input 
                              type="checkbox" 
                              className="sr-only peer" 
                              checked={settings.ai_extract_chat !== false}
                              onChange={(e) => handleUpdateSetting("ai_extract_chat", e.target.checked)}
                            />
                            <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-500"></div>
                          </label>
                        </div>
                      </div>

                      {settings.ai_enabled && (
                        <>
                          {/* --- AI MEMORY --- */}
                          <div className="space-y-3 pt-4 border-t border-gray-200">
                            <h3 className="font-semibold text-sm text-slate-800">AI Memory</h3>
                            
                            <div className="flex items-center justify-between">
                              <span className="text-sm text-slate-500">Enable AI Memory</span>
                              <label className="relative inline-flex items-center cursor-pointer">
                                <input 
                                  type="checkbox" 
                                  className="sr-only peer" 
                                  checked={oldConfigs.features.memory}
                                  onChange={(e) => updateConfigSetting("memory", e.target.checked, true)}
                                />
                                <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-500"></div>
                              </label>
                            </div>

                            {oldConfigs.features.memory && (
                              <div className="pl-4 space-y-3 border-l-2 border-gray-200 mt-2">
                                <div className="flex items-center justify-between">
                                  <span className="text-sm text-slate-500">Memory Refresh Interval</span>
                                  <select 
                                    value={settings.ai_memory_refresh_interval}
                                    onChange={(e) => handleUpdateSetting("ai_memory_refresh_interval", e.target.value)}
                                    className="rounded border border-gray-200 bg-gray-100 px-2 py-1 text-sm focus:border-blue-500 focus:outline-none"
                                  >
                                    <option value="realtime">Realtime</option>
                                    <option value="5_mins">5 Minutes</option>
                                    <option value="hourly">Hourly</option>
                                    <option value="daily">Daily</option>
                                    <option value="weekly">Weekly</option>
                                  </select>
                                </div>
                                <div className="flex items-center justify-between">
                                  <span className="text-sm text-slate-500">Memory Analysis Window</span>
                                  <select 
                                    value={settings.ai_memory_window}
                                    onChange={(e) => handleUpdateSetting("ai_memory_window", e.target.value)}
                                    className="rounded border border-gray-200 bg-gray-100 px-2 py-1 text-sm focus:border-blue-500 focus:outline-none"
                                  >
                                    <option value="1d">1 day</option>
                                    <option value="1w">1 week</option>
                                    <option value="1m">1 month</option>
                                    <option value="3m">3 months</option>
                                    <option value="6m">6 months</option>
                                    <option value="1y">1 year</option>
                                  </select>
                                </div>
                              </div>
                            )}
                          </div>

                          {/* --- AI COPILOT --- */}
                          <div className="space-y-3 pt-4 border-t border-gray-200">
                            <h3 className="font-semibold text-sm text-slate-800">AI Copilot</h3>
                            <div className="flex items-center justify-between">
                              <span className="text-sm text-slate-500">Enable AI Copilot</span>
                              <label className="relative inline-flex items-center cursor-pointer">
                                <input 
                                  type="checkbox" 
                                  className="sr-only peer" 
                                  checked={oldConfigs.features.copilot}
                                  onChange={(e) => updateConfigSetting("copilot", e.target.checked, true)}
                                />
                                <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-500"></div>
                              </label>
                            </div>

                            {oldConfigs.features.copilot && (
                              <div className="pl-4 space-y-3 border-l-2 border-gray-200 mt-2">
                                <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
                                  <div>
                                    <span className="text-sm text-slate-700 font-medium">Số lượt chat ngữ cảnh (Context Turns)</span>
                                    <p className="text-[11px] text-slate-400">Số lượng tin nhắn gần nhất Copilot sẽ đọc để hiểu ngữ cảnh</p>
                                  </div>
                                  <select 
                                    value={settings.ai_copilot_context_turns ?? 10}
                                    onChange={(e) => handleUpdateSetting("ai_copilot_context_turns", parseInt(e.target.value))}
                                    className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-semibold text-slate-700 focus:border-blue-500 focus:outline-none"
                                  >
                                    <option value="5">5 tin nhắn gần nhất</option>
                                    <option value="10">10 tin nhắn (Mặc định)</option>
                                    <option value="20">20 tin nhắn</option>
                                    <option value="50">50 tin nhắn</option>
                                    <option value="0">Toàn bộ (Không giới hạn)</option>
                                  </select>
                                </div>
                              </div>
                            )}
                          </div>

                          {/* --- AI TAGGING --- */}
                          <div className="space-y-3 pt-4 border-t border-gray-200">
                            <h3 className="font-semibold text-sm text-slate-800">AI Tagging</h3>
                            
                            <div className="flex items-center justify-between">
                              <span className="text-sm text-slate-500">Enable AI Tagging</span>
                              <label className="relative inline-flex items-center cursor-pointer">
                                <input 
                                  type="checkbox" 
                                  className="sr-only peer" 
                                  checked={oldConfigs.features.tagging}
                                  onChange={(e) => updateConfigSetting("tagging", e.target.checked, true)}
                                />
                                <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-500"></div>
                              </label>
                            </div>

                            {oldConfigs.features.tagging && (
                              <div className="pl-4 mt-2 border-l-2 border-gray-200">
                                <div className="flex items-center justify-between">
                                  <span className="text-sm text-slate-500">Maximum AI Tag Suggestions</span>
                                  <input 
                                    type="number" 
                                    min="1" 
                                    max="20"
                                    value={oldConfigs.tag_limit || 3}
                                    onChange={(e) => updateConfigSetting("tag_limit", parseInt(e.target.value) || 3)}
                                    className="w-16 rounded border border-gray-200 bg-gray-100 px-2 py-1 text-sm text-center focus:border-blue-500 focus:outline-none"
                                  />
                                </div>
                              </div>
                            )}
                          </div>

                          {/* --- AI RECOMMENDATION --- */}
                          <div className="space-y-3 pt-4 border-t border-gray-200">
                            <h3 className="font-semibold text-sm text-slate-800">AI Recommendation</h3>
                            
                            <div className="flex items-center justify-between">
                              <span className="text-sm text-slate-500">Enable AI Recommendation</span>
                              <label className="relative inline-flex items-center cursor-pointer">
                                <input 
                                  type="checkbox" 
                                  className="sr-only peer" 
                                  checked={oldConfigs.features.recommendation}
                                  onChange={(e) => updateConfigSetting("recommendation", e.target.checked, true)}
                                />
                                <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-500"></div>
                              </label>
                            </div>

                            {oldConfigs.features.recommendation && (
                              <div className="pl-4 space-y-3.5 border-l-2 border-gray-200 mt-2">
                                <div className="flex items-center justify-between">
                                  <span className="text-sm text-slate-500">Allow Profile Matching</span>
                                  <label className="relative inline-flex items-center cursor-pointer">
                                    <input 
                                      type="checkbox" 
                                      className="sr-only peer" 
                                      checked={settings.ai_read_profile}
                                      onChange={(e) => handleUpdateSetting("ai_read_profile", e.target.checked)}
                                    />
                                    <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-500"></div>
                                  </label>
                                </div>

                                <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
                                  <div>
                                    <span className="text-sm text-slate-700 font-medium">Tần suất thông báo gợi ý</span>
                                    <p className="text-[11px] text-slate-400">Khoảng thời gian cách nhau giữa các lần thông báo matching</p>
                                  </div>
                                  <select 
                                    value={oldConfigs.notification_interval || "24h"}
                                    onChange={(e) => {
                                      updateConfigSetting("notification_interval", e.target.value);
                                      handleUpdateSetting("ai_recommendation_interval", e.target.value);
                                    }}
                                    className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-semibold text-slate-700 focus:border-blue-500 focus:outline-none"
                                  >
                                    <option value="realtime">Ngay khi phát hiện (Realtime)</option>
                                    <option value="1h">Mỗi 1 giờ</option>
                                    <option value="6h">Mỗi 6 giờ</option>
                                    <option value="12h">Mỗi 12 giờ</option>
                                    <option value="24h">Hàng ngày (24 giờ)</option>
                                    <option value="weekly">Hàng tuần</option>
                                    <option value="off">Tắt thông báo</option>
                                  </select>
                                </div>

                                <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
                                  <div>
                                    <span className="text-sm text-slate-700 font-medium">Ngưỡng % gửi thông báo</span>
                                    <p className="text-[11px] text-slate-400">Chỉ gửi thông báo khi độ tương thích đạt từ mức này</p>
                                  </div>
                                  <select 
                                    value={oldConfigs.min_matching_score || 50}
                                    onChange={(e) => updateConfigSetting("min_matching_score", parseInt(e.target.value))}
                                    className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-semibold text-slate-700 focus:border-blue-500 focus:outline-none"
                                  >
                                    <option value="50">50% (Đề xuất)</option>
                                    <option value="60">60%</option>
                                    <option value="70">70%</option>
                                    <option value="80">80%</option>
                                    <option value="90">90%</option>
                                  </select>
                                </div>
                              </div>
                            )}
                          </div>
                        </>
                      )}
                    </div>
                  );
                })()
              )}

            </div>
          </Card>
        </div>
      </div>
    </main>
  );
}
