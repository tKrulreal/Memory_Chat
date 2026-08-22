"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Brain, Settings, Tag as TagIcon, Plus, X } from "lucide-react";
import { Button } from "@/components/ui/button";
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

  const { data: settings, isLoading: loadingSettings } = useQuery({
    queryKey: ["my-settings"],
    queryFn: getSettings,
  });

  const { data: configs = [], isLoading: loadingConfigs } = useQuery({
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
    <main className="flex-1 overflow-y-auto bg-app p-6 md:p-10">
      <div className="mx-auto max-w-5xl space-y-8">
        <div>
          <h1 className="text-2xl font-bold text-primary flex items-center gap-2">
            <Brain className="h-7 w-7 text-accent" />
            AI Hub
          </h1>
          <p className="text-sm text-secondary mt-1">
            Manage your personal AI rules, personality, and taxonomy.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Tags Section */}
          <section className="rounded-card border border-subtle bg-surface p-6 space-y-4">
            <h2 className="text-lg font-semibold text-primary border-b border-subtle pb-2 flex items-center gap-2">
              <TagIcon size={18} className="text-accent" />
              My AI Tags
            </h2>
            
            <form onSubmit={handleCreateTag} className="flex gap-2">
              <input
                type="text"
                placeholder="Tag name"
                value={newTagName}
                onChange={(e) => setNewTagName(e.target.value)}
                className="flex-1 rounded-button border border-subtle bg-elevated px-3 py-2 text-sm focus:border-accent focus:outline-none"
              />
              <Button type="submit" disabled={createTagMutation.isPending || !newTagName.trim()} size="sm">
                <Plus size={16} /> Add
              </Button>
            </form>

            <div className="mt-4 space-y-2">
              {loadingTags ? (
                <p className="text-sm text-secondary">Loading...</p>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {tags.map((tag: any) => (
                    <span key={tag.id} className="inline-flex items-center gap-1.5 rounded-full bg-accent/10 pl-3 pr-1 py-1 text-xs font-medium text-accent border border-accent/20">
                      {tag.name}
                      <button
                        type="button"
                        onClick={() => deleteTagMutation.mutate(tag.id)}
                        disabled={deleteTagMutation.isPending}
                        className="rounded-full p-0.5 text-accent/70 hover:text-accent hover:bg-accent/20 transition-colors"
                      >
                        <X size={12} />
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </div>
          </section>

          {/* AI Settings Section */}
          <section className="rounded-card border border-subtle bg-surface p-6 space-y-4">
            <h2 className="text-lg font-semibold text-primary border-b border-subtle pb-2 flex items-center gap-2">
              <Settings size={18} className="text-accent" />
              AI Settings
            </h2>
            
            <div className="space-y-4">
              {loadingSettings || !settings || loadingConfigs ? (
                <p className="text-sm text-secondary">Loading...</p>
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
                        <h3 className="font-semibold text-sm text-primary">AI Assistant</h3>
                        
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-secondary">Enable AI Assistant</span>
                          <label className="relative inline-flex items-center cursor-pointer">
                            <input 
                              type="checkbox" 
                              className="sr-only peer" 
                              checked={settings.ai_enabled}
                              onChange={(e) => handleUpdateSetting("ai_enabled", e.target.checked)}
                            />
                            <div className="w-9 h-5 bg-subtle peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-accent"></div>
                          </label>
                        </div>
                      </div>

                      {settings.ai_enabled && (
                        <>
                          {/* --- AI MEMORY --- */}
                          <div className="space-y-3 pt-4 border-t border-subtle">
                            <h3 className="font-semibold text-sm text-primary">AI Memory</h3>
                            
                            <div className="flex items-center justify-between">
                              <span className="text-sm text-secondary">Enable AI Memory</span>
                              <label className="relative inline-flex items-center cursor-pointer">
                                <input 
                                  type="checkbox" 
                                  className="sr-only peer" 
                                  checked={oldConfigs.features.memory}
                                  onChange={(e) => updateConfigSetting("memory", e.target.checked, true)}
                                />
                                <div className="w-9 h-5 bg-subtle peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-accent"></div>
                              </label>
                            </div>

                            {oldConfigs.features.memory && (
                              <div className="pl-4 space-y-3 border-l-2 border-subtle mt-2">
                                <div className="flex items-center justify-between">
                                  <span className="text-sm text-secondary">Memory Refresh Interval</span>
                                  <select 
                                    value={settings.ai_memory_refresh_interval}
                                    onChange={(e) => handleUpdateSetting("ai_memory_refresh_interval", e.target.value)}
                                    className="rounded border border-subtle bg-elevated px-2 py-1 text-sm focus:border-accent focus:outline-none"
                                  >
                                    <option value="realtime">Realtime</option>
                                    <option value="5_mins">5 Minutes</option>
                                    <option value="hourly">Hourly</option>
                                    <option value="daily">Daily</option>
                                    <option value="weekly">Weekly</option>
                                  </select>
                                </div>
                                <div className="flex items-center justify-between">
                                  <span className="text-sm text-secondary">Memory Analysis Window</span>
                                  <select 
                                    value={settings.ai_memory_window}
                                    onChange={(e) => handleUpdateSetting("ai_memory_window", e.target.value)}
                                    className="rounded border border-subtle bg-elevated px-2 py-1 text-sm focus:border-accent focus:outline-none"
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
                          <div className="space-y-3 pt-4 border-t border-subtle">
                            <h3 className="font-semibold text-sm text-primary">AI Copilot</h3>
                            <div className="flex items-center justify-between">
                              <span className="text-sm text-secondary">Enable AI Copilot</span>
                              <label className="relative inline-flex items-center cursor-pointer">
                                <input 
                                  type="checkbox" 
                                  className="sr-only peer" 
                                  checked={oldConfigs.features.copilot}
                                  onChange={(e) => updateConfigSetting("copilot", e.target.checked, true)}
                                />
                                <div className="w-9 h-5 bg-subtle peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-accent"></div>
                              </label>
                            </div>
                          </div>

                          {/* --- AI TAGGING --- */}
                          <div className="space-y-3 pt-4 border-t border-subtle">
                            <h3 className="font-semibold text-sm text-primary">AI Tagging</h3>
                            
                            <div className="flex items-center justify-between">
                              <span className="text-sm text-secondary">Enable AI Tagging</span>
                              <label className="relative inline-flex items-center cursor-pointer">
                                <input 
                                  type="checkbox" 
                                  className="sr-only peer" 
                                  checked={oldConfigs.features.tagging}
                                  onChange={(e) => updateConfigSetting("tagging", e.target.checked, true)}
                                />
                                <div className="w-9 h-5 bg-subtle peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-accent"></div>
                              </label>
                            </div>

                            {oldConfigs.features.tagging && (
                              <div className="pl-4 mt-2 border-l-2 border-subtle">
                                <div className="flex items-center justify-between">
                                  <span className="text-sm text-secondary">Maximum AI Tag Suggestions</span>
                                  <input 
                                    type="number" 
                                    min="1" 
                                    max="20"
                                    value={oldConfigs.tag_limit || 3}
                                    onChange={(e) => updateConfigSetting("tag_limit", parseInt(e.target.value) || 3)}
                                    className="w-16 rounded border border-subtle bg-elevated px-2 py-1 text-sm text-center focus:border-accent focus:outline-none"
                                  />
                                </div>
                              </div>
                            )}
                          </div>

                          {/* --- AI RECOMMENDATION --- */}
                          <div className="space-y-3 pt-4 border-t border-subtle">
                            <h3 className="font-semibold text-sm text-primary">AI Recommendation</h3>
                            
                            <div className="flex items-center justify-between">
                              <span className="text-sm text-secondary">Enable AI Recommendation</span>
                              <label className="relative inline-flex items-center cursor-pointer">
                                <input 
                                  type="checkbox" 
                                  className="sr-only peer" 
                                  checked={oldConfigs.features.recommendation}
                                  onChange={(e) => updateConfigSetting("recommendation", e.target.checked, true)}
                                />
                                <div className="w-9 h-5 bg-subtle peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-accent"></div>
                              </label>
                            </div>

                            {oldConfigs.features.recommendation && (
                              <div className="pl-4 space-y-3 border-l-2 border-subtle mt-2">
                                <div className="flex items-center justify-between">
                                  <span className="text-sm text-secondary">Allow Profile Matching</span>
                                  <label className="relative inline-flex items-center cursor-pointer">
                                    <input 
                                      type="checkbox" 
                                      className="sr-only peer" 
                                      checked={settings.ai_read_profile}
                                      onChange={(e) => handleUpdateSetting("ai_read_profile", e.target.checked)}
                                    />
                                    <div className="w-9 h-5 bg-subtle peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-accent"></div>
                                  </label>
                                </div>
                                <div className="flex items-center justify-between">
                                  <span className="text-sm text-secondary">Minimum Match Percentage</span>
                                  <select 
                                    value={oldConfigs.min_matching_score || 50}
                                    onChange={(e) => updateConfigSetting("min_matching_score", parseInt(e.target.value))}
                                    className="rounded border border-subtle bg-elevated px-2 py-1 text-sm focus:border-accent focus:outline-none"
                                  >
                                    <option value="50">50%</option>
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
          </section>
        </div>
      </div>
    </main>
  );
}
