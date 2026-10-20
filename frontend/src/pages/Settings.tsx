
import { useCallback, useEffect, useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { useNavigate } from "react-router-dom";
import { api, User, IngestionSource, SourceCreate, ApiError } from "@/shared/api";
import {
  Settings as SettingsIcon,
  Mail,
  Rss,
  Plus,
  Trash2,
  RefreshCw,
  Tag,
  Clock,
  User as UserIcon,
  Bell,
} from "lucide-react";
import PageLoader from "@/components/ui/PageLoader";
import Button from "@/components/ui/Button";
import { ListRowSkeleton, Skeleton } from "@/components/ui/Skeleton";
import ConfirmDialog from "@/components/ui/ConfirmDialog";
import { useToast } from "@/components/ui/Toast";
import { cn } from "@/shared/cn";

interface Category {
  id: number;
  name: string;
  description: string | null;
  is_active: boolean;
}

type SettingsTab = "profile" | "interests" | "sources";

const EMPTY_SOURCE: SourceCreate = {
  source_type: "rss",
  display_name: "",
  identifier: "",
  is_active: true,
};

function Switch({ checked, onChange, disabled }: { checked: boolean; onChange: () => void; disabled?: boolean }) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      aria-label="Toggle digest subscription"
      onClick={onChange}
      disabled={disabled}
      className={cn(
        "relative inline-flex h-7 w-12 flex-shrink-0 items-center rounded-full transition-colors duration-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
        checked ? "bg-brand-600" : "bg-slate-200"
      )}
    >
      <span
        className={cn(
          "inline-block h-5 w-5 transform rounded-full bg-white shadow transition-transform duration-300",
          checked ? "translate-x-6" : "translate-x-1"
        )}
      />
    </button>
  );
}

export default function SettingsPage() {
  const { user, isAuthenticated, isLoading: authLoading, isAdmin, refreshUser, updateProfile } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();

  const [isLoading, setIsLoading] = useState(true);
  const [sources, setSources] = useState<IngestionSource[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [showAddSource, setShowAddSource] = useState(false);
  const [newSource, setNewSource] = useState<SourceCreate>(EMPTY_SOURCE);
  const [selectedInterests, setSelectedInterests] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState<SettingsTab>("profile");

  // Per-action pending states for button spinners.
  const [pending, setPending] = useState<string | null>(null);
  const [confirmDeleteId, setConfirmDeleteId] = useState<number | null>(null);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      navigate("/login");
    }
  }, [isAuthenticated, authLoading, navigate]);

  useEffect(() => {
    if (!isAdmin && activeTab === "sources") {
      setActiveTab("profile");
    }
  }, [isAdmin, activeTab]);

  const fetchData = useCallback(async ({ silent = false } = {}) => {
    if (!silent) setIsLoading(true);
    try {
      const [sourcesData, categoriesData] = await Promise.all([
        api.get<IngestionSource[]>("/sources"),
        api.get<Category[]>("/categories", { active_only: true }),
      ]);
      setSources(sourcesData);
      setCategories(categoriesData);
    } catch (err) {
      const apiError = err as ApiError;
      toast.error(apiError.detail || "Failed to fetch settings data");
    } finally {
      setIsLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchData();
      setSelectedInterests(user?.interests || []);
    }
  }, [isAuthenticated, user?.interests, fetchData]);

  /** Toggle with a pending state — the button is disabled while the request runs. */
  const handleToggleSubscription = async () => {
    if (!user || pending === "subscription") return;
    const nextValue = !user.digest_subscribed;
    setPending("subscription");
    try {
      await api.patch<User>("/me/subscription", { digest_subscribed: nextValue });
      await refreshUser();
      toast.success(nextValue ? "Digest subscription enabled" : "Digest subscription disabled");
    } catch (err) {
      const apiError = err as ApiError;
      toast.error(apiError.detail || "Failed to update subscription");
    } finally {
      setPending(null);
    }
  };

  const handleAddSource = async (e: React.FormEvent) => {
    e.preventDefault();
    setPending("add-source");
    try {
      await api.post<IngestionSource>("/sources", newSource);
      setShowAddSource(false);
      setNewSource(EMPTY_SOURCE);
      await fetchData({ silent: true });
      toast.success("Source added successfully");
    } catch (err) {
      const apiError = err as ApiError;
      toast.error(apiError.detail || "Failed to add source");
    } finally {
      setPending(null);
    }
  };

  const handleDeleteSource = async () => {
    if (confirmDeleteId === null) return;
    setPending(`delete-source-${confirmDeleteId}`);
    try {
      await api.delete(`/sources/${confirmDeleteId}`);
      await fetchData({ silent: true });
      toast.success("Source deleted successfully");
      setConfirmDeleteId(null);
    } catch (err) {
      const apiError = err as ApiError;
      toast.error(apiError.detail || "Failed to delete source");
    } finally {
      setPending(null);
    }
  };

  const handleSyncDefaults = async () => {
    setPending("sync-defaults");
    try {
      const result = await api.post<{ created: number; updated: number }>("/sources/sync-defaults", null);
      await fetchData({ silent: true });
      toast.success(`Synced defaults: ${result.created} created, ${result.updated} updated`);
    } catch (err) {
      const apiError = err as ApiError;
      toast.error(apiError.detail || "Failed to sync defaults");
    } finally {
      setPending(null);
    }
  };

  const toggleInterest = (interest: string) => {
    setSelectedInterests((prev) =>
      prev.includes(interest) ? prev.filter((i) => i !== interest) : [...prev, interest]
    );
  };

  const handleSaveInterests = async () => {
    setPending("save-interests");
    try {
      await updateProfile({ interests: selectedInterests });
      toast.success("Interests updated successfully");
    } catch (err) {
      const apiError = err as ApiError;
      toast.error(apiError.detail || "Failed to update interests");
    } finally {
      setPending(null);
    }
  };

  if (authLoading) {
    return <PageLoader label="Checking your session" />;
  }

  const TABS: { id: SettingsTab; label: string; icon: React.ReactNode; adminOnly?: boolean }[] = [
    { id: "profile", label: "Profile", icon: <UserIcon className="h-4 w-4" /> },
    { id: "interests", label: "Topics", icon: <Tag className="h-4 w-4" /> },
    { id: "sources", label: "Sources", icon: <Rss className="h-4 w-4" />, adminOnly: true },
  ];

  return (
    <div className="mx-auto max-w-4xl animate-fade-in space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-brand-500 to-accent-500 text-white shadow-glow">
          <SettingsIcon className="h-5 w-5" />
        </span>
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">Settings</h1>
          <p className="mt-0.5 text-slate-500">Manage your account and your daily brief.</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 overflow-x-auto rounded-2xl border border-slate-200 bg-white p-1.5 shadow-sm">
        {TABS.filter((tab) => !tab.adminOnly || isAdmin).map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              "flex flex-1 items-center justify-center gap-2 whitespace-nowrap rounded-xl px-4 py-2.5 text-sm font-medium transition-all duration-200",
              activeTab === tab.id
                ? "bg-gradient-to-r from-brand-600 to-brand-700 text-white shadow-soft"
                : "text-slate-600 hover:bg-slate-100"
            )}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </div>

      {/* Profile Tab */}
      {activeTab === "profile" && (
        <div className="space-y-6">
          <div className="card">
            <h2 className="mb-5 flex items-center gap-2 text-lg font-semibold text-slate-900">
              <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-50 text-brand-600">
                <UserIcon className="h-4 w-4" />
              </span>
              Your profile
            </h2>
            <div className="divide-y divide-slate-100">
              <div className="flex items-center justify-between py-3">
                <p className="text-sm text-slate-500">Name</p>
                <p className="font-medium text-slate-900">{user?.name || "Not set"}</p>
              </div>
              <div className="flex items-center justify-between py-3">
                <p className="text-sm text-slate-500">Email</p>
                <p className="font-medium text-slate-900">{user?.email}</p>
              </div>
              <div className="flex items-center justify-between py-3">
                <p className="text-sm text-slate-500">Role</p>
                <span className="badge-brand">{user?.role}</span>
              </div>
            </div>
          </div>

          {/* Subscription */}
          <div className="card">
            <h2 className="mb-5 flex items-center gap-2 text-lg font-semibold text-slate-900">
              <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-50 text-brand-600">
                <Mail className="h-4 w-4" />
              </span>
              Your daily brief
            </h2>
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="font-medium text-slate-900">Email me my brief</p>
                <p className="text-sm text-slate-500">A short, friendly summary in your inbox</p>
              </div>
              <Switch
                checked={!!user?.digest_subscribed}
                onChange={handleToggleSubscription}
                disabled={pending === "subscription"}
              />
            </div>
            {user?.digest_subscribed && (
              <div className="mt-4 flex items-center gap-2 border-t border-slate-100 pt-4 text-sm text-slate-500">
                <Bell className="h-4 w-4 text-brand-500" />
                Arrives{" "}
                <span className="font-medium text-slate-900">{user?.digest_frequency || "daily"}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Interests Tab */}
      {activeTab === "interests" && (
        <div className="card">
          <h2 className="mb-2 flex items-center gap-2 text-lg font-semibold text-slate-900">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-50 text-brand-600">
              <Tag className="h-4 w-4" />
            </span>
            Topics you love
          </h2>
          <p className="mb-5 text-sm text-slate-500">
            Pick the subjects you care about — we&apos;ll shape your news feed and briefs around them.
          </p>

          {isLoading ? (
            <div className="mb-6 flex flex-wrap gap-2" aria-busy="true" aria-label="Loading topics">
              {Array.from({ length: 8 }).map((_, i) => (
                <Skeleton key={i} className="h-9 w-24 rounded-full" />
              ))}
            </div>
          ) : (
            <div className="mb-6 flex flex-wrap gap-2">
              {categories.map((category) => {
                const active = selectedInterests.includes(category.name);
                return (
                  <button
                    key={category.id}
                    onClick={() => toggleInterest(category.name)}
                    className={cn(
                      "rounded-full px-4 py-2 text-sm font-medium transition-all duration-200",
                      active
                        ? "bg-gradient-to-r from-brand-600 to-brand-700 text-white shadow-soft"
                        : "bg-slate-100 text-slate-700 hover:bg-slate-200"
                    )}
                    aria-pressed={active}
                  >
                    {category.name}
                  </button>
                );
              })}
            </div>
          )}

          <div className="flex items-center justify-between border-t border-slate-100 pt-4">
            <p className="text-sm text-slate-400">{selectedInterests.length} topics selected</p>
            <Button size="sm" onClick={handleSaveInterests} loading={pending === "save-interests"}>
              Save topics
            </Button>
          </div>
        </div>
      )}

      {/* Sources Tab */}
      {isAdmin && activeTab === "sources" && (
        <div className="card">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
            <h2 className="flex items-center gap-2 text-lg font-semibold text-slate-900">
              <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-50 text-brand-600">
                <Rss className="h-4 w-4" />
              </span>
              Sources we follow
            </h2>
            <div className="flex items-center gap-2">
              <Button
                variant="secondary"
                size="sm"
                icon={<RefreshCw className="h-4 w-4" />}
                onClick={handleSyncDefaults}
                loading={pending === "sync-defaults"}
              >
                Sync defaults
              </Button>
              <Button
                size="sm"
                icon={<Plus className="h-4 w-4" />}
                onClick={() => setShowAddSource((show) => !show)}
              >
                {showAddSource ? "Cancel" : "Add source"}
              </Button>
            </div>
          </div>

          {showAddSource && (
            <form onSubmit={handleAddSource} className="animate-fade-in mb-4 space-y-3 rounded-xl bg-slate-50 p-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="mb-1 block text-sm font-medium text-slate-700">Type</label>
                  <select
                    value={newSource.source_type}
                    onChange={(e) =>
                      setNewSource({ ...newSource, source_type: e.target.value as SourceCreate["source_type"] })
                    }
                    className="input"
                  >
                    <option value="rss">RSS Feed</option>
                    <option value="youtube">YouTube Channel</option>
                    <option value="medium">Medium Publication</option>
                  </select>
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-slate-700">Display name</label>
                  <input
                    type="text"
                    value={newSource.display_name}
                    onChange={(e) => setNewSource({ ...newSource, display_name: e.target.value })}
                    className="input"
                    placeholder="My Source"
                    required
                  />
                </div>
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-700">
                  {newSource.source_type === "rss"
                    ? "RSS URL"
                    : newSource.source_type === "medium"
                      ? "Medium RSS URL"
                      : "Channel ID"}
                </label>
                <input
                  type="text"
                  value={newSource.identifier}
                  onChange={(e) => setNewSource({ ...newSource, identifier: e.target.value })}
                  className="input"
                  placeholder={
                    newSource.source_type === "rss"
                      ? "https://example.com/feed.xml"
                      : newSource.source_type === "medium"
                        ? "https://medium.com/feed/@publication"
                        : "UCxxxxxxxxxxxxxxxx"
                  }
                  required
                />
              </div>
              <div className="flex items-center gap-2">
                <Button type="submit" size="sm" loading={pending === "add-source"}>
                  Add source
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => setShowAddSource(false)}
                  disabled={pending === "add-source"}
                >
                  Cancel
                </Button>
              </div>
            </form>
          )}

          {isLoading ? (
            <ListRowSkeleton rows={4} />
          ) : sources.length === 0 ? (
            <p className="py-8 text-center text-slate-500">
              No sources configured yet. Add one above or sync the defaults.
            </p>
          ) : (
            <div className="space-y-2">
              {sources.map((source) => {
                const deleting = pending === `delete-source-${source.id}`;
                return (
                  <div
                    key={source.id}
                    className="flex items-center justify-between rounded-xl bg-slate-50 p-3 transition-colors hover:bg-slate-100/70"
                  >
                    <div className="flex min-w-0 items-center gap-3">
                      <span
                        className={cn(
                          "badge",
                          source.source_type === "rss" ? "badge-brand" : "badge-green"
                        )}
                      >
                        {source.source_type}
                      </span>
                      <div className="min-w-0">
                        <p className="truncate text-sm font-medium text-slate-900">{source.display_name}</p>
                        <p className="max-w-xs truncate text-xs text-slate-400">{source.identifier}</p>
                        <div className="mt-1 flex items-center gap-2">
                          <span className="inline-flex items-center gap-1 text-xs text-slate-400">
                            <Clock className="h-3 w-3" />
                            {source.total_fetches || 0} fetches
                          </span>
                          {source.consecutive_errors > 0 && (
                            <span className="text-xs text-red-500">{source.consecutive_errors} errors</span>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex flex-shrink-0 items-center gap-2">
                      <span
                        className={cn(
                          "badge",
                          source.status === "active" ? "badge-green" : "badge-gray"
                        )}
                      >
                        {source.status}
                      </span>
                      <button
                        onClick={() => setConfirmDeleteId(source.id)}
                        disabled={deleting}
                        className="rounded-lg p-1.5 text-slate-400 transition-colors hover:bg-red-50 hover:text-red-500 disabled:opacity-50"
                        aria-label={`Delete ${source.display_name}`}
                      >
                        <Trash2 className={cn("h-4 w-4", deleting && "animate-pulse")} />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      <ConfirmDialog
        open={confirmDeleteId !== null}
        title="Delete source"
        message="Are you sure you want to delete this source? This cannot be undone."
        confirmLabel="Delete"
        danger
        loading={pending !== null && pending.startsWith("delete-source")}
        onConfirm={handleDeleteSource}
        onCancel={() => setConfirmDeleteId(null)}
      />
    </div>
  );
}
