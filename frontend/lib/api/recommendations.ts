/**
 * API service for Connection Recommendations
 */

export type {
  ConnectionRecommendation,
  ConnectionRecommendationDetail,
  GenerateConnectionsResponse,
  RecommendationStatus,
} from "@/types/recommendation";

import {
  ConnectionRecommendation,
  ConnectionRecommendationDetail,
  GenerateConnectionsResponse,
  RecommendationStatus,
} from "@/types/recommendation";

const BASE_PATH = "/api/proxy/api/v1/recommendations/connections";

export async function getConnectionRecommendations(
  status: RecommendationStatus = "PENDING",
  limit = 20
): Promise<ConnectionRecommendation[]> {
  const url = `${BASE_PATH}?status=${status}&limit=${limit}`;
  const response = await fetch(url);

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Failed to fetch recommendations");
  }

  return response.json();
}

export async function getConnectionDetail(
  id: string
): Promise<ConnectionRecommendationDetail> {
  const response = await fetch(`${BASE_PATH}/${id}`);

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Failed to fetch recommendation detail");
  }

  return response.json();
}

export async function acceptConnection(
  id: string,
  customMessage?: string
): Promise<ConnectionRecommendation> {
  const response = await fetch(`${BASE_PATH}/${id}/accept`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(customMessage ? { custom_message: customMessage } : {}),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Failed to accept recommendation");
  }

  return response.json();
}

export async function rejectConnection(
  id: string
): Promise<ConnectionRecommendation> {
  const response = await fetch(`${BASE_PATH}/${id}/reject`, {
    method: "POST",
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Failed to reject recommendation");
  }

  return response.json();
}

export async function dismissConnection(
  id: string
): Promise<ConnectionRecommendation> {
  const response = await fetch(`${BASE_PATH}/dismiss/${id}`, {
    method: "POST",
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Failed to dismiss recommendation");
  }

  return response.json();
}

export async function generateConnections(): Promise<GenerateConnectionsResponse> {
  const response = await fetch(`${BASE_PATH}/generate`, {
    method: "POST",
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Failed to generate connections");
  }

  return response.json();
}
