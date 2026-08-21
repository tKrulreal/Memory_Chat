"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Brain, Settings, Tag as TagIcon, Plus, Save } from "lucide-react";
import { Button } from "@/components/ui/button";
import { getSystemTags, createSystemTag, getAiConfigs, updateAiConfig } from "@/lib/api/tags";
import { useAuthStore } from "@/lib/stores/auth-store";
import { AISystemConfig } from "@/types";

export default function AIHubPage() {
  const user = useAuthStore((s) => s.user);
  const queryClient = useQueryClient();

  const [newTagName, setNewTagName] = useState("");
  const [newTagCategory, setNewTagCategory] = useState("skill");
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
    mutationFn: () => createSystemTag(newTagName, newTagCategory),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["system-tags"] });
      setNewTagName("");
    },
  });

  const updateConfigMutation = useMutation({
    mutationFn: (data: { key: string, value: string, desc?: string }) => 
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
    setEditConfigValue(config.value);
    setEditConfigDesc(config.description || "");
  };

  const handleUpdateConfig = () => {
    if (editingConfig) {
      updateConfigMutation.mutate({
        key: editingConfig,
        value: editConfigValue,
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
              <select
                value={newTagCategory}
                onChange={(e) => setNewTagCategory(e.target.value)}
                className="w-24 rounded-button border border-subtle bg-elevated px-2 py-2 text-sm focus:border-accent focus:outline-none"
              >
                <option value="skill">Skill</option>
                <option value="interest">Interest</option>
                <option value="need">Need</option>
              </select>
              <Button type="submit" disabled={createTagMutation.isPending || !newTagName.trim()} size="sm">
                <Plus size={16} /> Add
              </Button>
            </form>

            <div className="mt-4 space-y-2">
              {loadingTags ? (
                <p className="text-sm text-secondary">Loading...</p>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {tags.map((tag) => (
                    <span key={tag.id} className="inline-flex items-center gap-1.5 rounded-full bg-accent/10 px-3 py-1 text-xs font-medium text-accent border border-accent/20">
                      {tag.name}
                      <span className="text-[10px] text-accent/60 opacity-75">({tag.category})</span>
                    </span>
                  ))}
                </div>
              )}
            </div>
          </section>

          {/* AI Configs Section */}
          <section className="rounded-card border border-subtle bg-surface p-6 space-y-4">
            <h2 className="text-lg font-semibold text-primary border-b border-subtle pb-2 flex items-center gap-2">
              <Settings size={18} className="text-accent" />
              AI Rules & Configuration
            </h2>
            
            <div className="space-y-4">
              {loadingConfigs ? (
                <p className="text-sm text-secondary">Loading...</p>
              ) : (
                configs.map((config) => (
                  <div key={config.key} className="rounded-button border border-subtle bg-elevated p-4 space-y-2">
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="font-semibold text-sm text-primary">{config.key}</h3>
                        {editingConfig !== config.key && (
                          <p className="text-xs text-secondary mt-1">{config.description}</p>
                        )}
                      </div>
                      {editingConfig !== config.key && (
                        <Button variant="ghost" size="sm" onClick={() => startEditConfig(config)}>
                          Edit
                        </Button>
                      )}
                    </div>
                    
                    {editingConfig === config.key ? (
                      <div className="space-y-3 pt-2">
                        <textarea
                          value={editConfigValue}
                          onChange={(e) => setEditConfigValue(e.target.value)}
                          className="w-full rounded-button border border-subtle bg-input px-3 py-2 text-sm focus:border-accent focus:outline-none min-h-[100px] resize-y"
                        />
                        <input
                          type="text"
                          value={editConfigDesc}
                          onChange={(e) => setEditConfigDesc(e.target.value)}
                          placeholder="Description"
                          className="w-full rounded-button border border-subtle bg-input px-3 py-2 text-sm focus:border-accent focus:outline-none"
                        />
                        <div className="flex justify-end gap-2">
                          <Button variant="ghost" size="sm" onClick={() => setEditingConfig(null)}>
                            Cancel
                          </Button>
                          <Button size="sm" onClick={handleUpdateConfig} disabled={updateConfigMutation.isPending}>
                            <Save size={14} className="mr-1" /> Save
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <div className="bg-app/50 p-2 rounded text-xs font-mono break-all text-secondary overflow-hidden">
                        {config.value.length > 150 ? config.value.substring(0, 150) + "..." : config.value}
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}
