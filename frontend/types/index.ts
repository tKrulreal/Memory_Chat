export type User = {
  id: string;
  email: string;
  full_name: string;
  avatar?: string | null;
  gender?: string | null;
  phone?: string | null;
};

export type Participant = {
  id: string;
  email: string;
  full_name: string | null;
  avatar: string | null;
  gender?: string | null;
  phone?: string | null;
};

export type Conversation = {
  id: string;
  user_a_id: string;
  user_b_id: string;
  status: string;
  last_message_at: string | null;
  last_message: string | null;
  unread_count?: number;
  user_a?: Participant;
  user_b?: Participant;
  tags?: { id: string; name: string; color?: string }[] | string[];
};

export type Message = {
  id: string;
  conversation_id: string;
  sender_user_id: string;
  content: string;
  created_at: string;
  client_message_id?: string | null;
  deleted_at?: string | null;
  is_read?: boolean;
  local_status?: "sending" | "sent" | "failed";
};

export type Pagination = {
  page: number;
  limit: number;
  total: number;
};

export type PaginatedResponse<T> = {
  data: T[];
  pagination: Pagination;
};

export type AIContextFact = {
  label: string;
  value: string;
};

export type AIRecommendation = {
  id: string;
  summary: string;
  suggested_action?: string;
};

export type CopilotResponse = {
  response: string;
  intent: string;
  tools_used: string[];
  sources: string[];
  is_valid: boolean;
};

export type WSMessageEvent = {
  type: "message.created" | "message.read" | "ping" | "pong" | "MESSAGE_RECALLED";
  payload?: Record<string, unknown>;
  conversation_id?: string;
  message_id?: string;
  deleted_at?: string | null;
};

export type SearchResult = {
  conversation_id: string;
  peer: Participant;
  summary_snippet: string | null;
  score: number;
};

export type Setting = {
  user_id: string;
  theme?: string;
  language?: string;
  notifications_enabled?: boolean;
  notification?: boolean;
  sound_enabled?: boolean;
  enter_is_send?: boolean;
  read_receipts?: boolean;
  online_status?: boolean;
  media_auto_download?: boolean;
  message_preview?: boolean;
  accent_color?: string;
  font_size?: string;
  ai_enabled?: boolean;
  ai_read_profile?: boolean;
  ai_extract_chat?: boolean;
  ai_memory_refresh_interval?: string;
  ai_memory_window?: string;
  ai_recommendation_interval?: string;
  ai_copilot_context_turns?: number;
};

export type BlockedUser = {
  id: string;
  email: string;
  full_name: string | null;
  avatar: string | null;
  blocked_at: string;
};

export type Tag = {
  id: string;
  name: string;
  category: string;
  is_active: boolean;
};

export type AISystemConfig = {
  key: string;
  value: any;
  description: string | null;
};

export type Notification = {
  id: string;
  user_id: string;
  type: string;
  title: string;
  content: string;
  status: string;
  data?: Record<string, any> | null;
  created_at: string;
};

export type ExperienceItem = {
  title: string;
  company: string;
  period?: string;
  description?: string;
};

export type EducationItem = {
  school: string;
  degree?: string;
  field?: string;
  year?: string;
};

export type UserProfile = {
  user_id: string;
  email: string;
  full_name: string | null;
  avatar: string | null;
  gender: string | null;
  phone: string | null;
  profession: string | null;
  company: string | null;
  location: string | null;
  skills: string[];
  interests: string[];
  looking_for: string[];
  offering: string[];
  bio: string | null;
  is_public: boolean;
  github?: string | null;
  linkedin?: string | null;
  website?: string | null;
  experience?: ExperienceItem[];
  education?: EducationItem[];
  is_custom_profile?: boolean;
  created_at?: string | null;
  updated_at?: string | null;
};

export type PublicUserProfile = {
  user_id: string;
  email?: string | null;
  full_name: string | null;
  avatar: string | null;
  gender?: string | null;
  phone?: string | null;
  profession?: string | null;
  company?: string | null;
  location?: string | null;
  skills: string[];
  interests: string[];
  looking_for: string[];
  offering: string[];
  bio: string | null;
  is_public: boolean;
  github?: string | null;
  linkedin?: string | null;
  website?: string | null;
  experience?: ExperienceItem[];
  education?: EducationItem[];
  connection_status: "CONNECTED" | "PENDING_SENT" | "PENDING_RECEIVED" | "NONE";
  conversation_id?: string | null;
  created_at?: string | null;
};
