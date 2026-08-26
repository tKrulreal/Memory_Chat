/**
 * API service for User Profile Management
 */

import type { UserProfile, PublicUserProfile, ExperienceItem, EducationItem } from "@/types";

export interface ProfileUpdatePayload {
  full_name?: string | null;
  avatar?: string | null;
  gender?: string | null;
  phone?: string | null;
  profession?: string | null;
  company?: string | null;
  location?: string | null;
  skills?: string[];
  interests?: string[];
  looking_for?: string[];
  offering?: string[];
  bio?: string | null;
  is_public?: boolean;
  github?: string | null;
  linkedin?: string | null;
  website?: string | null;
  experience?: ExperienceItem[];
  education?: EducationItem[];
}

const BASE_PATH = "/api/proxy/api/v1/profile";

export async function getMyProfile(): Promise<UserProfile> {
  const response = await fetch(`${BASE_PATH}/me`);
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Không thể tải thông tin hồ sơ");
  }
  return response.json();
}

export async function updateMyProfile(payload: ProfileUpdatePayload): Promise<UserProfile> {
  const response = await fetch(`${BASE_PATH}/me`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Không thể cập nhật hồ sơ");
  }
  return response.json();
}

export async function getUserPublicProfile(userId: string): Promise<PublicUserProfile> {
  const response = await fetch(`${BASE_PATH}/${userId}`);
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Không thể tải hồ sơ người dùng");
  }
  return response.json();
}
