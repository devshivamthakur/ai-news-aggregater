export { api, SESSION_EXPIRED_EVENT } from "./api/client";
export type { User, TokenPairOut, NewsItem, NewsListOut, IngestionSource, AdminStatsOut, AdminUser, Category } from "./api/types";
export type { ApiResponse, ApiError } from "./api/client";

export interface SourceCreate {
  source_type: "rss" | "youtube" | "medium" | "twitter" | "reddit" | "podcast";
  display_name: string;
  identifier: string;
  description?: string;
  category?: string;
  is_active?: boolean;
  fetch_interval_minutes?: number;
  priority?: number;
  max_items_per_fetch?: number;
}

export interface SourcePatch {
  display_name?: string;
  identifier?: string;
  description?: string;
  category?: string;
  is_active?: boolean;
  fetch_interval_minutes?: number;
  priority?: number;
  max_items_per_fetch?: number;
}

export interface SyncDefaultsResult {
  created: number;
  updated: number;
  rss_feed_urls: number;
  youtube_channels: number;
  medium_sources: number;
}

export interface HealthOut {
  status: string;
  version: string;
  environment: string;
  scheduler_enabled: boolean;
  database_connected: boolean;
  uptime_seconds: number | null;
}

export interface JobAccepted {
  status: string;
  detail: string;
}
