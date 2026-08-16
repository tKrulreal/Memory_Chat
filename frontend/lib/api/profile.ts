/**
 * API service for User Profile Management
 */

export interface UserProfileData {
  user_id: string;
  email: string;
  full_name: string | null;
  avatar: string | null;
  profession: string | null;
  company: string | null;
  location: string | null;
  skills: string[];
  interests: string[];
  looking_for: string[];
  offering: string[];
  bio: string | null;
  is_custom_profile: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface ProfileUpdatePayload {
  full_name?: string | null;
  avatar?: string | null;
  profession?: string | null;
  company?: string | null;
  location?: string | null;
  skills?: string[];
  interests?: string[];
  looking_for?: string[];
  offering?: string[];
  bio?: string | null;
}

const BASE_PATH = "/api/proxy/api/v1/profile";

export async function getMyProfile(): Promise<UserProfileData> {
  const response = await fetch(`${BASE_PATH}/me`);
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Không thể tải thông tin hồ sơ");
  }
  return response.json();
}

export async function updateMyProfile(payload: ProfileUpdatePayload): Promise<UserProfileData> {
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
