/**
 * Types for Connection Recommendations (User-to-User Networking)
 */

export type ConnectionRecommendation = {
  id: string;
  owner_user_id: string;
  target_user_id: string | null;
  reason: string;
  priority: "HIGH" | "MEDIUM" | "LOW";
  confidence: number;
  status: "PENDING" | "ACCEPTED" | "REJECTED" | "DISMISSED";
  created_at: string;
  expires_at: string | null;

  // Recommended User Profile
  target_user_name: string | null;
  target_user_email: string | null;
  target_user_avatar: string | null;
  target_user_profession: string | null;
  target_user_company: string | null;
  target_user_location: string | null;
  target_user_skills: string[];
  target_user_interests: string[];
  target_user_needs?: string[];
  target_user_offers?: string[];

  // Legacy fallback fields
  contact_name?: string | null;
  target_contact_name?: string | null;
  conversation_id?: string | null;
};


export type ConnectionRecommendationDetail = {
  id: string;
  reason: string;
  priority: "HIGH" | "MEDIUM" | "LOW";
  confidence: number;
  status: "PENDING" | "ACCEPTED" | "REJECTED" | "DISMISSED";
  created_at: string;

  // Current User (You)
  current_user_id: string;
  current_user_name: string;
  current_user_email?: string | null;
  current_user_avatar?: string | null;
  current_user_profession?: string | null;
  current_user_company?: string | null;
  current_user_location?: string | null;
  current_user_skills: string[];
  current_user_interests: string[];
  current_user_needs: string[];   // Looking for
  current_user_offers: string[];  // Offering

  // Target User (Recommended Person)
  target_user_id: string;
  target_user_name: string;
  target_user_email?: string | null;
  target_user_avatar?: string | null;
  target_user_profession?: string | null;
  target_user_company?: string | null;
  target_user_location?: string | null;
  target_user_skills: string[];
  target_user_interests: string[];
  target_user_needs: string[];    // Looking for
  target_user_offers: string[];   // Offering

  // Suggested message & conversation ID
  suggested_intro: string | null;
  conversation_id: string | null;
  target_user_bio?: string | null;
  complementary_aspects?: string[];
  shared_interests?: string[];


  // Legacy aliases
  contact_a_name?: string | null;
  contact_b_name?: string | null;
};

export type GenerateConnectionsResponse = {
  generated: number;
  total_pending: number;
  message: string;
};

export type RecommendationStatus = "PENDING" | "ACCEPTED" | "REJECTED" | "DISMISSED";
