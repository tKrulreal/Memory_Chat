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
};

export type Message = {
  id: string;
  conversation_id: string;
  sender_user_id: string;
  content: string;
  created_at: string;
  client_message_id?: string | null;
  deleted_at?: string | null;
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
  id: string;
  user_id: string;
  theme: string;
  notifications_enabled: boolean;
  ai_enabled: boolean;
  ai_memory_window: string;
};

export type Tag = {
  id: string;
  name: string;
  category: string;
  is_active: boolean;
};

export type AISystemConfig = {
  key: string;
  value: string;
  description: string | null;
};
