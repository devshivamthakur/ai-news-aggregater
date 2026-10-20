
import { useCallback, useDeferredValue, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { api, NewsItem, NewsListOut, ApiError, Category } from "@/shared/api";
import {
  ExternalLink,
  Search,
  RefreshCw,
  AlertCircle,
  Newspaper,
  ChevronLeft,
  ChevronRight,
  Clock,
  Sparkles,
  X,
  Filter,
} from "lucide-react";
import PageLoader from "@/components/ui/PageLoader";
import { NewsCardSkeleton } from "@/components/ui/Skeleton";
import EmptyState from "@/components/ui/EmptyState";
import Button from "@/components/ui/Button";
import { cn } from "@/shared/cn";

const PAGE_SIZE = 20;
const SEARCH_DEBOUNCE_MS = 400;

export default function NewsPage() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const navigate = useNavigate();

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
      navigate("/login");
    }
  }, [isAuthenticated, authLoading, navigate]);

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
    return <PageLoader label="Checking your session" />;
  }

  return (
    <div className="animate-fade-in space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-brand-500 to-accent-500 text-white shadow-glow">
              <Newspaper className="h-5 w-5" />
            </span>
            <div>
              <h1 className="text-3xl font-bold tracking-tight text-slate-900">Your news</h1>
              <p className="mt-0.5 text-slate-500">
                {totalItems > 0
                  ? `${totalItems.toLocaleString()} stories worth your time`
                  : "Here's what's worth your time today."}
              </p>
            </div>
          </div>
        </div>
        <Button
          variant="secondary"
          icon={<RefreshCw className={cn("h-4 w-4", isRefreshing && "animate-spin")} />}
          onClick={() => fetchNews({ silent: true })}
          loading={isRefreshing}
        >
          Refresh
        </Button>
      </div>

      {/* Filters */}
      <div className="card flex flex-col gap-4 sm:flex-row sm:items-center">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search stories…"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input pl-10"
            aria-label="Search stories"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery("")}
              className="absolute right-3 top-1/2 -translate-y-1/2 rounded-md p-1 text-slate-400 transition-colors hover:text-slate-600"
              aria-label="Clear search"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>

        <div className="flex items-center gap-2">
          <div className="relative">
            <Filter className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="input w-full appearance-none pl-10 pr-9 sm:w-52"
              aria-label="Filter by topic"
            >
              <option value="all">All topics</option>
              {categoryOptions.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
            <ChevronRight className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 rotate-90 text-slate-400" />
          </div>
          {hasFilters && (
            <Button variant="ghost" size="sm" onClick={clearFilters}>
              Clear
            </Button>
          )}
        </div>
      </div>

      {error && (
        <div className="animate-fade-in flex items-center gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          <AlertCircle className="h-4 w-4 flex-shrink-0" />
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
          icon={<Newspaper className="h-7 w-7" />}
          title={hasFilters ? "Nothing matches your filters" : "No stories yet"}
          description={
            hasFilters
              ? "Try a different search or clear the filters."
              : "Stories will show up here as soon as we gather them."
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
              "stagger space-y-4",
              isLoading && "pointer-events-none opacity-60 transition-opacity duration-300"
            )}
            aria-busy={isLoading}
          >
            {news.map((item) => (
              <article
                key={item.id}
                className="card card-hover group flex items-start gap-5"
              >
                {item.image_url && (
                  <div className="relative hidden h-28 w-28 flex-shrink-0 overflow-hidden rounded-xl bg-slate-100 sm:block">
                    <img
                      src={item.image_url}
                      alt={item.title}
                      loading="lazy"
                      className="absolute inset-0 h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
                    />
                  </div>
                )}

                <div className="min-w-0 flex-1">
                  <div className="mb-2 flex flex-wrap items-center gap-2">
                    {item.source && <span className="badge-brand">{item.source}</span>}
                    {item.category && <span className="badge-green">{item.category}</span>}
                    {item.news_type && <span className="badge-gray">{item.news_type}</span>}
                    {item.reading_time_minutes ? (
                      <span className="inline-flex items-center gap-1 text-xs text-slate-400">
                        <Clock className="h-3 w-3" />
                        {item.reading_time_minutes} min read
                      </span>
                    ) : null}
                  </div>

                  <h2 className="text-lg font-semibold text-slate-900">
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="group/title flex items-start gap-1 transition-colors hover:text-brand-600"
                    >
                      <span className="line-clamp-2">{item.title}</span>
                      <ExternalLink className="mt-1 h-4 w-4 flex-shrink-0 -translate-x-1 opacity-0 transition-all duration-200 group-hover/title:translate-x-0 group-hover/title:opacity-100" />
                    </a>
                  </h2>

                  {item.summary && (
                    <p className="mt-1.5 line-clamp-3 text-sm leading-relaxed text-slate-600">
                      {item.summary}
                    </p>
                  )}

                  <div className="mt-3 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-slate-400">
                    {item.author && <span>By {item.author}</span>}
                    {item.published_at && (
                      <span>{new Date(item.published_at).toLocaleDateString()}</span>
                    )}
                    <span className="inline-flex items-center gap-1 text-brand-500">
                      <Sparkles className="h-3 w-3" /> Summarized for you
                    </span>
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
                icon={<ChevronLeft className="h-4 w-4" />}
                onClick={() => goToPage(page - 1)}
                disabled={page === 1 || isLoading}
              >
                Previous
              </Button>
              <span className="text-sm text-slate-500 tabular-nums">
                Page {page} of {totalPages} · {totalItems.toLocaleString()} stories
              </span>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => goToPage(page + 1)}
                disabled={page === totalPages || isLoading}
              >
                Next
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
