"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Brain, Settings, Tag as TagIcon, Plus, Save, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { getSystemTags, createSystemTag, getAiConfigs, updateAiConfig } from "@/lib/api/tags";
import { useAuthStore } from "@/lib/stores/auth-store";
import { AISystemConfig } from "@/types";

export default function AIHubPage() {
  const user = useAuthStore((s) => s.user);
  const queryClient = useQueryClient();

  const [newTagName, setNewTagName] = useState("");
  const [editingConfig, setEditingConfig] = useState<string | null>(null);
  const [editConfigValue, setEditConfigValue] = useState("");
  const [editConfigDesc, setEditConfigDesc] = useState("");

  const { data: tags = [], isLoading: loadingTags } = useQuery({
    queryKey: ["system-tags"],
    queryFn: getSystemTags,
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

  const updateConfigMutation = useMutation({
    mutationFn: (data: { key: string, value: any, desc?: string }) => 
      updateAiConfig(data.key, data.value, data.desc),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["system-configs"] });
      setEditingConfig(null);
    },
  });

  const handleCreateTag = (e: React.FormEvent) => {
    e.preventDefault();
    if (newTagName.trim()) {
      createTagMutation.mutate();
    }
  };

  const startEditConfig = (config: AISystemConfig) => {
    setEditingConfig(config.key);
    setEditConfigValue(typeof config.value === 'string' ? config.value : JSON.stringify(config.value, null, 2));
    setEditConfigDesc(config.description || "");
  };

  const handleUpdateConfig = () => {
    if (editingConfig) {
      let parsedValue = editConfigValue;
      try {
        parsedValue = JSON.parse(editConfigValue);
      } catch (e) {
        // If it can't be parsed, we send it as string or notify user.
        // For AI Rules, backend expects dict, so if it's invalid JSON, we might want to alert the user.
        alert("Invalid JSON format");
        return;
      }
      
      updateConfigMutation.mutate({
        key: editingConfig,
        value: parsedValue,
        desc: editConfigDesc,
      });
    }
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
            Manage system-wide AI rules and taxonomy.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Tags Section */}
          <section className="rounded-card border border-subtle bg-surface p-6 space-y-4">
            <h2 className="text-lg font-semibold text-primary border-b border-subtle pb-2 flex items-center gap-2">
              <TagIcon size={18} className="text-accent" />
              System Tags
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
              {loadingConfigs ? (
                <p className="text-sm text-secondary">Loading...</p>
              ) : (() => {
                const aiSettingsConfig = configs.find((c: any) => c.key === "ai_settings");
                const defaultSettings = {
                  features: {
                    copilot: true,
                    recommendation: true,
                    memory: true,
                    tagging: true,
                  },
                  tag_limit: 3,
                  memory_timeframe: "1 month"
                };
                
                const settings = aiSettingsConfig?.value ? 
                  { ...defaultSettings, ...aiSettingsConfig.value, features: { ...defaultSettings.features, ...(aiSettingsConfig.value.features || {}) } } 
                  : defaultSettings;

                const updateSetting = (key: string, value: any, isFeature: boolean = false) => {
                  const newSettings = { ...settings };
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
                    <div className="space-y-3">
                      <h3 className="font-semibold text-sm text-primary">AI Features</h3>
                      {Object.entries(settings.features).map(([featureKey, isEnabled]) => (
                        <div key={featureKey} className="flex items-center justify-between">
                          <span className="text-sm text-secondary capitalize">AI {featureKey}</span>
                          <label className="relative inline-flex items-center cursor-pointer">
                            <input 
                              type="checkbox" 
                              className="sr-only peer" 
                              checked={isEnabled as boolean}
                              onChange={(e) => updateSetting(featureKey, e.target.checked, true)}
                            />
                            <div className="w-9 h-5 bg-subtle peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-accent"></div>
                          </label>
                        </div>
                      ))}
                    </div>

                    <div className="space-y-3 pt-2 border-t border-subtle">
                      <h3 className="font-semibold text-sm text-primary">AI Tagging</h3>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-secondary">Maximum AI Tag Suggestions</span>
                        <input 
                          type="number" 
                          min="1" 
                          max="10"
                          value={settings.tag_limit}
                          onChange={(e) => updateSetting("tag_limit", parseInt(e.target.value) || 3)}
                          className="w-16 rounded border border-subtle bg-elevated px-2 py-1 text-sm text-center focus:border-accent focus:outline-none"
                        />
                      </div>
                    </div>

                    <div className="space-y-3 pt-2 border-t border-subtle">
                      <h3 className="font-semibold text-sm text-primary">Memory</h3>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-secondary">Memory Context Timeframe</span>
                        <select 
                          value={settings.memory_timeframe}
                          onChange={(e) => updateSetting("memory_timeframe", e.target.value)}
                          className="rounded border border-subtle bg-elevated px-2 py-1 text-sm focus:border-accent focus:outline-none"
                        >
                          <option value="1 week">1 week</option>
                          <option value="1 month">1 month</option>
                          <option value="3 months">3 months</option>
                          <option value="6 months">6 months</option>
                          <option value="1 year">1 year</option>
                        </select>
                      </div>
                    </div>
                  </div>
                );
              })()}
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}
