"use client";

import { useCallback, useEffect, useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";
import { api, User, IngestionSource, SourceCreate, ApiError } from "@/lib/api";
import {
  Settings as SettingsIcon,
  Mail,
  Rss,
  Plus,
  Trash2,
  RefreshCw,
  ToggleLeft,
  ToggleRight,
  Tag,
  Clock,
  Check,
} from "lucide-react";
import PageLoader from "@/components/ui/PageLoader";
import Button from "@/components/ui/Button";
import { ListRowSkeleton, Skeleton } from "@/components/ui/Skeleton";
import ConfirmDialog from "@/components/ui/ConfirmDialog";
import { useToast } from "@/components/ui/Toast";
import { cn } from "@/lib/cn";

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

export default function SettingsPage() {
  const { user, isAuthenticated, isLoading: authLoading, isAdmin, refreshUser, updateProfile } = useAuth();
  const router = useRouter();
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
      router.push("/login");
    }
  }, [isAuthenticated, authLoading, router]);

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
    return <PageLoader label="Checking session" />;
  }

  const TABS: { id: SettingsTab; label: string; icon: React.ReactNode; adminOnly?: boolean }[] = [
    { id: "profile", label: "Profile", icon: <SettingsIcon className="w-4 h-4" /> },
    { id: "interests", label: "Interests", icon: <Tag className="w-4 h-4" /> },
    { id: "sources", label: "Sources", icon: <Rss className="w-4 h-4" />, adminOnly: true },
  ];

  return (
    <div className="space-y-6 max-w-4xl mx-auto animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-1">Manage your account and preferences</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-gray-200 pb-2 overflow-x-auto">
        {TABS.filter((tab) => !tab.adminOnly || isAdmin).map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap",
              activeTab === tab.id ? "bg-brand-100 text-brand-700" : "text-gray-600 hover:bg-gray-100"
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
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <SettingsIcon className="w-5 h-5" />
              Profile
            </h2>
            <div className="space-y-3">
              <div className="flex items-center justify-between py-2">
                <div>
                  <p className="text-sm text-gray-600">Name</p>
                  <p className="font-medium text-gray-900">{user?.name || "Not set"}</p>
                </div>
              </div>
              <div className="flex items-center justify-between py-2">
                <div>
                  <p className="text-sm text-gray-600">Email</p>
                  <p className="font-medium text-gray-900">{user?.email}</p>
                </div>
              </div>
              <div className="flex items-center justify-between py-2">
                <div>
                  <p className="text-sm text-gray-600">Role</p>
                  <span className="badge badge-brand">{user?.role}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Subscription Section */}
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Mail className="w-5 h-5" />
              Email Digest
            </h2>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-900">Daily Digest Subscription</p>
                <p className="text-sm text-gray-600">Receive personalized news digests via email</p>
              </div>
              <button
                onClick={handleToggleSubscription}
                disabled={pending === "subscription"}
                className="flex items-center gap-2 text-brand-600 hover:text-brand-700 disabled:opacity-50 transition-all"
                aria-label="Toggle digest subscription"
                aria-pressed={user?.digest_subscribed}
              >
                {user?.digest_subscribed ? (
                  <ToggleRight className="w-8 h-8" />
                ) : (
                  <ToggleLeft className="w-8 h-8" />
                )}
              </button>
            </div>
            {user?.digest_subscribed && (
              <div className="mt-4 pt-4 border-t border-gray-100">
                <p className="text-sm text-gray-600">
                  Frequency:{" "}
                  <span className="font-medium text-gray-900">{user?.digest_frequency || "daily"}</span>
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Interests Tab */}
      {activeTab === "interests" && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Tag className="w-5 h-5" />
            Your Interests
          </h2>
          <p className="text-sm text-gray-600 mb-4">
            Select topics you care about. We&apos;ll personalize your news feed and digests based on these.
          </p>
          {isLoading ? (
            <div className="flex flex-wrap gap-2 mb-6" aria-busy="true" aria-label="Loading categories">
              {Array.from({ length: 8 }).map((_, i) => (
                <Skeleton key={i} className="h-9 w-24 rounded-full" />
              ))}
            </div>
          ) : (
            <div className="flex flex-wrap gap-2 mb-6">
              {categories.map((category) => {
                const active = selectedInterests.includes(category.name);
                return (
                  <button
                    key={category.id}
                    onClick={() => toggleInterest(category.name)}
                    className={cn(
                      "px-4 py-2 rounded-full text-sm font-medium transition-all duration-200",
                      active
                        ? "bg-brand-600 text-white shadow-sm shadow-brand-600/30"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                    )}
                    aria-pressed={active}
                  >
                    {category.name}
                  </button>
                );
              })}
            </div>
          )}
          <div className="flex items-center justify-between pt-4 border-t border-gray-100">
            <p className="text-sm text-gray-500">{selectedInterests.length} interests selected</p>
            <Button size="sm" onClick={handleSaveInterests} loading={pending === "save-interests"}>
              Save Interests
            </Button>
          </div>
        </div>
      )}

      {/* Sources Tab */}
      {isAdmin && activeTab === "sources" && (
        <div className="card">
          <div className="flex flex-wrap items-center justify-between gap-2 mb-4">
            <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <Rss className="w-5 h-5" />
              Ingestion Sources
            </h2>
            <div className="flex items-center gap-2">
              <Button
                variant="secondary"
                size="sm"
                icon={<RefreshCw className="w-4 h-4" />}
                onClick={handleSyncDefaults}
                loading={pending === "sync-defaults"}
              >
                Sync Defaults
              </Button>
              <Button
                size="sm"
                icon={<Plus className="w-4 h-4" />}
                onClick={() => setShowAddSource((show) => !show)}
              >
                {showAddSource ? "Cancel" : "Add Source"}
              </Button>
            </div>
          </div>

          {showAddSource && (
            <form onSubmit={handleAddSource} className="mb-4 p-4 bg-gray-50 rounded-lg space-y-3 animate-fade-in">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
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
                  <label className="block text-sm font-medium text-gray-700 mb-1">Display Name</label>
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
                <label className="block text-sm font-medium text-gray-700 mb-1">
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
                  Add Source
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
            <p className="text-gray-500 text-center py-8">
              No sources configured. Add one above or sync defaults.
            </p>
          ) : (
            <div className="space-y-2">
              {sources.map((source) => {
                const deleting = pending === `delete-source-${source.id}`;
                return (
                  <div
                    key={source.id}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100/70 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <span
                        className={`badge ${
                          source.source_type === "rss"
                            ? "badge-brand"
                            : "badge-green"
                        }`}
                      >
                        {source.source_type}
                      </span>
                      <div>
                        <p className="font-medium text-gray-900 text-sm">{source.display_name}</p>
                        <p className="text-xs text-gray-500 truncate max-w-xs">{source.identifier}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-xs text-gray-400 flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {source.total_fetches || 0} fetches
                          </span>
                          {source.consecutive_errors > 0 && (
                            <span className="text-xs text-red-500">{source.consecutive_errors} errors</span>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span
                        className={`badge ${
                          source.status === "active" ? "badge-green" : "badge-gray"
                        }`}
                      >
                        {source.status}
                      </span>
                      <button
                        onClick={() => setConfirmDeleteId(source.id)}
                        disabled={deleting}
                        className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
                        aria-label={`Delete ${source.display_name}`}
                      >
                        <Trash2 className={`w-4 h-4 ${deleting ? "animate-pulse" : ""}`} />
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
