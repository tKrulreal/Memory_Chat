import { Tag, AISystemConfig } from "@/types";

export async function getSystemTags(): Promise<Tag[]> {
  const response = await fetch("/api/proxy/api/v1/tags");
  if (!response.ok) {
    throw new Error("Failed to fetch tags");
  }
  return response.json();
}

export async function createSystemTag(name: string, category: string): Promise<Tag> {
  const response = await fetch("/api/proxy/api/v1/tags", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, category }),
  });
  if (!response.ok) {
    throw new Error("Failed to create tag");
  }
  return response.json();
}

export async function getMyTags(): Promise<Tag[]> {
  const response = await fetch("/api/proxy/api/v1/users/me/tags");
  if (!response.ok) {
    throw new Error("Failed to fetch my tags");
  }
  return response.json();
}

export async function addMyTag(tagId: string): Promise<void> {
  const response = await fetch("/api/proxy/api/v1/users/me/tags", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tag_id: tagId }),
  });
  if (!response.ok) {
    throw new Error("Failed to add tag");
  }
}

export async function removeMyTag(tagId: string): Promise<void> {
  const response = await fetch(`/api/proxy/api/v1/users/me/tags/${tagId}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    throw new Error("Failed to remove tag");
  }
}

export async function getAiConfigs(): Promise<AISystemConfig[]> {
  const response = await fetch("/api/proxy/api/v1/ai-config");
  if (!response.ok) {
    throw new Error("Failed to fetch AI configs");
  }
  return response.json();
}

export async function updateAiConfig(key: string, value: string, description?: string): Promise<AISystemConfig> {
  const response = await fetch(`/api/proxy/api/v1/ai-config/${key}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ value, description }),
  });
  if (!response.ok) {
    throw new Error("Failed to update AI config");
  }
  return response.json();
}
