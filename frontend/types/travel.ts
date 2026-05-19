export type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

export type RetrievedContext = {
  score?: number;
  search_mode?: string;
  title?: string;
  city?: string;
  category?: string;
  address?: string;
  best_time?: string;
  budget?: string;
  suitable_for?: string[];
  tips?: string;
  text?: string;
  source_url?: string;
  source_file?: string;
  latitude?: number | null;
  longitude?: number | null;
};

export type RoutePlan = {
  strategy?: string;
  ordered_places?: RetrievedContext[];
  missing_coordinate_places?: string[];
  route_summary?: {
    provider?: string;
    profile?: string;
    total_distance_km?: number;
    total_duration_minutes?: number;
    note?: string;
    segments?: {
      from?: string;
      to?: string;
      distance_km?: number;
      duration_minutes_estimate?: number;
      method?: string;
    }[];
  };
};

export type GroundingGuard = {
  has_retrieved_contexts?: boolean;
  allowed_place_names?: string[];
  route_provider?: string;
  is_route_estimate_only?: boolean;
  warnings?: string[];
  policy?: {
    only_use_retrieved_places?: boolean;
    no_realtime_claims?: boolean;
    must_disclose_missing_data?: boolean;
    must_disclose_route_estimate?: boolean;
  };
};

export type PostProcessingGuard = {
  was_modified?: boolean;
  removed_items?: string[];
  warnings?: string[];
  blocked_items?: string[];
  guard_applied?: boolean;
};

export type AgentResponse = {
  answer: string;
  trip_requirements: Record<string, unknown>;
  retrieved_contexts: RetrievedContext[];
  route_plan: RoutePlan;
  budget_plan: Record<string, unknown>;
  grounding_guard?: GroundingGuard;
  post_processing_guard?: PostProcessingGuard;
  critique: string;
  saved_memories?: {
    id: number;
    memory_type: string;
    content: string;
    confidence?: number;
  }[];
};

export type UserPreferences = {
  travelStyle: string;
  budgetLevel: string;
  walkingLevel: string;
  favoritePlaces: string;
  avoidPlaces: string;
};