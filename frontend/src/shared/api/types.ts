export interface User {
  id: number;
  email: string;
  name: string | null;
  role: string;
  status: string;
  digest_subscribed: boolean;
  digest_frequency: string;
  interests: string[];
  email_verified: boolean;
  last_login_at: string | null;
  created_at: string;
}

export interface TokenPairOut {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface NewsItem {
  id: number;
  title: string;
  summary: string | null;
  category: string | null;
  source: string | null;
  source_url: string | null;
  url: string;
  image_url: string | null;
  author: string | null;
  news_type: string;
  status: string;
  sentiment_score: number | null;
  keywords: string | null;
  reading_time_minutes: number | null;
  language: string;
  published_at: string | null;
  created_at: string;
}

export interface NewsListOut {
  items: NewsItem[];
  total: number;
  page: number;
  page_size: number;
  has_next: boolean;
}

export interface IngestionSource {
  id: number;
  source_type: string;
  display_name: string;
  identifier: string;
  description: string | null;
  category: string | null;
  status: string;
  is_active: boolean;
  fetch_interval_minutes: number;
  priority: number;
  max_items_per_fetch: number;
  last_fetched_at: string | null;
  last_error_at: string | null;
  consecutive_errors: number;
  total_fetches: number;
  total_items_fetched: number;
  created_at: string | null;
  updated_at: string | null;
}

export interface AdminStatsOut {
  total_users: number;
  active_users: number;
  suspended_users: number;
  total_admins: number;
  subscribed_users: number;
  total_news_items: number;
  pending_news_items: number;
  analyzed_news_items: number;
  total_sources: number;
  active_sources: number;
  error_sources: number;
  total_fetches: number;
  total_items_fetched: number;
  news_today: number;
  news_this_week: number;
}

export interface AdminUser {
  id: number;
  email: string;
  name: string | null;
  role: string;
  status: string;
  is_active: boolean;
  digest_subscribed: boolean;
  last_login_at: string | null;
  created_at: string;
}

export interface Category {
  id: number;
  name: string;
  description: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
