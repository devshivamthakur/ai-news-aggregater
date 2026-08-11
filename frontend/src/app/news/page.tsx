"use client";

import { useCallback, useDeferredValue, useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { useAuth } from "@/context/AuthContext";
import { api, NewsItem, NewsListOut, ApiError, Category } from "@/lib/api";
import {
  ExternalLink,
  Search,
  RefreshCw,
  AlertCircle,
  Newspaper,
  ChevronLeft,
  ChevronRight,
  Clock,
  X,
} from "lucide-react";
import PageLoader from "@/components/ui/PageLoader";
import { NewsCardSkeleton } from "@/components/ui/Skeleton";
import EmptyState from "@/components/ui/EmptyState";
import Button from "@/components/ui/Button";
import { cn } from "@/lib/cn";

const PAGE_SIZE = 20;
const SEARCH_DEBOUNCE_MS = 400;

export default function NewsPage() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const router = useRouter();

  const [news, setNews] = useState<NewsItem[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);

  const abortControllerRef = useRef<AbortController | null>(null);

  // Keeps the UI responsive while typing; the search itself happens server-side.
  const deferredSearch = useDeferredValue(searchQuery);

  // Redirect unauthenticated users after auth resolves.
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, authLoading, router]);

  const fetchNews = useCallback(
    async ({ silent = false } = {}) => {
      abortControllerRef.current?.abort();
      const controller = new AbortController();
      abortControllerRef.current = controller;

      if (silent) {
        setIsRefreshing(true);
      } else {
        setIsLoading(true);
      }
      setError("");

      try {
        const params: Record<string, unknown> = { page, page_size: PAGE_SIZE };
        if (deferredSearch.trim()) params.q = deferredSearch.trim();
        if (selectedCategory !== "all") params.category = selectedCategory;

        const data = await api.get<NewsListOut>("/news", params, { signal: controller.signal });
        setNews(data.items);
        setTotalItems(data.total);
        setTotalPages(Math.max(1, Math.ceil(data.total / PAGE_SIZE)));
      } catch (err) {
        // Ignore aborted requests (superseded by a newer fetch). The axios
        // interceptor normalizes cancellations to { detail: "canceled" }, so
        // checking the signal is the reliable way to detect them.
        if (controller.signal.aborted) return;
        const apiError = err as ApiError;
        if (apiError && typeof apiError.detail === "string" && apiError.detail) {
          setError(apiError.detail);
        }
      } finally {
        // Only the latest request may clear the loading state.
        if (!controller.signal.aborted) {
          setIsLoading(false);
          setIsRefreshing(false);
        }
      }
    },
    [page, deferredSearch, selectedCategory]
  );

  // Load the category list once for the filter dropdown (from the API, not the current page).
  useEffect(() => {
    api
      .get<Category[]>("/categories", { active_only: true })
      .then(setCategories)
      .catch(() => {
        /* Categories are non-critical; the feed still works without them. */
      });
  }, []);

  // Fetch news whenever the page, search or category changes.
  useEffect(() => {
    if (!authLoading && isAuthenticated) {
      fetchNews();
    }
  }, [fetchNews, authLoading, isAuthenticated]);

  // Debounced server-side search: reset to page 1 after the user stops typing.
  useEffect(() => {
    const handler = setTimeout(() => setPage(1), SEARCH_DEBOUNCE_MS);
    return () => clearTimeout(handler);
  }, [deferredSearch, selectedCategory]);

  const goToPage = useCallback(
    (nextPage: number) => {
      setPage(Math.min(Math.max(1, nextPage), totalPages));
      window.scrollTo({ top: 0, behavior: "smooth" });
    },
    [totalPages]
  );

  const clearFilters = useCallback(() => {
    setSearchQuery("");
    setSelectedCategory("all");
  }, []);

  const hasFilters = deferredSearch.trim() !== "" || selectedCategory !== "all";
  const showSkeleton = isLoading && news.length === 0;

  const categoryOptions = useMemo(() => {
    const fromApi = categories.map((c) => c.name);
    const fromPage = news.map((n) => n.category).filter(Boolean) as string[];
    return Array.from(new Set([...fromApi, ...fromPage])).sort();
  }, [categories, news]);

  if (authLoading) {
    return <PageLoader label="Checking session" />;
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Latest News</h1>
          <p className="text-gray-600 mt-1">
            {totalItems > 0
              ? `${totalItems.toLocaleString()} AI-curated articles available`
              : "Stay updated with AI-curated articles"}
          </p>
        </div>
        <Button
          variant="secondary"
          icon={<RefreshCw className={cn("w-4 h-4", isRefreshing && "animate-spin")} />}
          onClick={() => fetchNews({ silent: true })}
          loading={isRefreshing}
        >
          Refresh
        </Button>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
            <input
              type="text"
              placeholder="Search articles..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="input pl-10"
              aria-label="Search articles"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery("")}
                className="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-gray-400 hover:text-gray-600 transition-colors"
                aria-label="Clear search"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
          <div className="flex items-center gap-2">
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="input w-full sm:w-auto"
              aria-label="Filter by category"
            >
              <option value="all">All Categories</option>
              {categoryOptions.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
            {hasFilters && (
              <Button variant="ghost" size="sm" onClick={clearFilters}>
                Clear
              </Button>
            )}
          </div>
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm animate-fade-in">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <p className="flex-1">{error}</p>
          <Button variant="secondary" size="sm" onClick={() => fetchNews()}>
            Retry
          </Button>
        </div>
      )}

      {showSkeleton ? (
        <div className="space-y-4" aria-busy="true" aria-label="Loading news">
          {Array.from({ length: 6 }).map((_, i) => (
            <NewsCardSkeleton key={i} />
          ))}
        </div>
      ) : news.length === 0 ? (
        <EmptyState
          icon={<Newspaper className="w-7 h-7" />}
          title={hasFilters ? "No articles match your filters" : "No articles found"}
          description={
            hasFilters
              ? "Try adjusting your search or clearing the filters"
              : "News will appear here once aggregation runs"
          }
          action={
            hasFilters ? (
              <Button variant="secondary" size="sm" onClick={clearFilters}>
                Clear filters
              </Button>
            ) : undefined
          }
        />
      ) : (
        <>
          <div
            className={cn(
              "space-y-4 stagger",
              isLoading && "opacity-60 pointer-events-none transition-opacity duration-300"
            )}
            aria-busy={isLoading}
          >
            {news.map((item) => (
              <article
                key={item.id}
                className="card hover:shadow-md hover:border-brand-100 transition-all duration-300 group"
              >
                <div className="flex items-start justify-between gap-4">
                  {item.image_url && (
                    <div className="relative w-24 h-24 flex-shrink-0 rounded-lg overflow-hidden bg-gray-100">
                      <Image
                        src={item.image_url}
                        alt={item.title}
                        fill
                        sizes="96px"
                        loading="lazy"
                        className="object-cover group-hover:scale-105 transition-transform duration-500"
                      />
                    </div>
                  )}
                  <div className="flex-1 min-w-0">
                    <div className="flex flex-wrap items-center gap-2 mb-2">
                      {item.source && <span className="badge-brand">{item.source}</span>}
                      {item.category && <span className="badge-green">{item.category}</span>}
                      <span className="badge-gray">{item.news_type}</span>
                      {item.reading_time_minutes ? (
                        <span className="text-xs text-gray-500 flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {item.reading_time_minutes} min read
                        </span>
                      ) : null}
                    </div>
                    <h2 className="text-lg font-semibold text-gray-900 mb-2">
                      <a
                        href={item.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="hover:text-brand-600 transition-colors flex items-center gap-1 group/title"
                      >
                        <span className="line-clamp-2">{item.title}</span>
                        <ExternalLink className="w-4 h-4 flex-shrink-0 opacity-0 -translate-x-1 group-hover/title:opacity-100 group-hover/title:translate-x-0 transition-all duration-200" />
                      </a>
                    </h2>
                    {item.summary && <p className="text-gray-600 text-sm line-clamp-3">{item.summary}</p>}
                    {item.author && <p className="text-xs text-gray-500 mt-2">By {item.author}</p>}
                  </div>
                </div>
              </article>
            ))}
          </div>

          {/* Skeleton shimmer below the list during page transitions (stale-while-revalidate). */}
          {isLoading && news.length > 0 && (
            <div className="space-y-4">
              {Array.from({ length: 2 }).map((_, i) => (
                <NewsCardSkeleton key={`stale-${i}`} />
              ))}
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex flex-wrap items-center justify-center gap-4 py-2">
              <Button
                variant="secondary"
                size="sm"
                icon={<ChevronLeft className="w-4 h-4" />}
                onClick={() => goToPage(page - 1)}
                disabled={page === 1 || isLoading}
              >
                Previous
              </Button>
              <span className="text-sm text-gray-600 tabular-nums">
                Page {page} of {totalPages} · {totalItems.toLocaleString()} items
              </span>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => goToPage(page + 1)}
                disabled={page === totalPages || isLoading}
              >
                Next
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
