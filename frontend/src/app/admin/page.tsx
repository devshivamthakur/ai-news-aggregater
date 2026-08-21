"use client";

import { useCallback, useEffect, useState, useTransition } from "react";
import dynamic from "next/dynamic";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";
import { api, IngestionSource, AdminStatsOut, AdminUser, Category, ApiError } from "@/lib/api";
import { RefreshCw } from "lucide-react";
import AdminTabs, { AdminTab } from "@/components/admin/AdminTabs";
import PageLoader from "@/components/ui/PageLoader";
import { StatCardSkeleton, ListRowSkeleton } from "@/components/ui/Skeleton";
import ConfirmDialog from "@/components/ui/ConfirmDialog";
import Button from "@/components/ui/Button";
import { useToast } from "@/components/ui/Toast";
import { withChunkRetry } from "@/lib/chunkRetry";
import { NewSourceInput } from "@/components/admin/SourcesTab";
import { NewCategoryInput } from "@/components/admin/CategoriesTab";

// Lazy-load tab bundles so only the active tab ships in the client bundle.
// withChunkRetry handles transient dev-mode chunk failures (stale URLs after
// a recompile) by retrying before surfacing to the error boundary.
const OverviewTab = dynamic(withChunkRetry(() => import("@/components/admin/OverviewTab")), {
  ssr: false,
  loading: () => (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {Array.from({ length: 8 }).map((_, i) => (
        <StatCardSkeleton key={i} />
      ))}
    </div>
  ),
});
const UsersTab = dynamic(withChunkRetry(() => import("@/components/admin/UsersTab")), {
  ssr: false,
  loading: () => <ListRowSkeleton rows={6} />,
});
const SourcesTab = dynamic(withChunkRetry(() => import("@/components/admin/SourcesTab")), {
  ssr: false,
  loading: () => <ListRowSkeleton rows={5} />,
});
const CategoriesTab = dynamic(withChunkRetry(() => import("@/components/admin/CategoriesTab")), {
  ssr: false,
  loading: () => <ListRowSkeleton rows={5} />,
});
const JobsTab = dynamic(withChunkRetry(() => import("@/components/admin/JobsTab")), {
  ssr: false,
  loading: () => <ListRowSkeleton rows={3} />,
});
const MaintenanceTab = dynamic(withChunkRetry(() => import("@/components/admin/MaintenanceTab")), {
  ssr: false,
  loading: () => <ListRowSkeleton rows={2} />,
});

interface ConfirmState {
  title: string;
  message: string;
  confirmLabel: string;
  danger?: boolean;
  action: () => Promise<void>;
}

export default function AdminPage() {
  const { isAuthenticated, isLoading: authLoading, isAdmin } = useAuth();
  const router = useRouter();
  const toast = useToast();

  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [stats, setStats] = useState<AdminStatsOut | null>(null);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [sources, setSources] = useState<IngestionSource[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [activeTab, setActiveTab] = useState<AdminTab>("overview");
  const [isPendingTab, startTabTransition] = useTransition();

  // Per-action pending states for button spinners.
  const [pendingAction, setPendingAction] = useState<{ type: string; id?: number } | null>(null);
  const [confirm, setConfirm] = useState<ConfirmState | null>(null);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, authLoading, router]);

  useEffect(() => {
    if (isAuthenticated && isAdmin) {
      fetchData();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, isAdmin]);

  const fetchData = useCallback(async ({ silent = false } = {}) => {
    if (silent) {
      setIsRefreshing(true);
    } else {
      setIsLoading(true);
    }
    setError("");

    try {
      // allSettled: one failing endpoint no longer blanks the whole dashboard.
      const [statsRes, usersRes, sourcesRes, categoriesRes] = await Promise.allSettled([
        api.get<AdminStatsOut>("/admin/stats"),
        api.get<AdminUser[]>("/admin/users"),
        api.get<IngestionSource[]>("/sources"),
        api.get<Category[]>("/categories", { active_only: false }),
      ]);

      if (statsRes.status === "fulfilled") setStats(statsRes.value);
      if (usersRes.status === "fulfilled") setUsers(usersRes.value);
      if (sourcesRes.status === "fulfilled") setSources(sourcesRes.value);
      if (categoriesRes.status === "fulfilled") setCategories(categoriesRes.value);

      const failed = [statsRes, usersRes, sourcesRes, categoriesRes].filter(
        (r) => r.status === "rejected"
      ).length;
      if (failed > 0) {
        setError(`Failed to load ${failed} of 4 data sections. Showing what we have.`);
      }
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  const runAction = useCallback(
    async (action: () => Promise<void>, onError?: string) => {
      setError("");
      try {
        await action();
        return true;
      } catch (err) {
        const apiError = err as ApiError;
        toast.error(apiError.detail || onError || "Action failed");
        return false;
      }
    },
    [toast]
  );

  const handleAddSource = async (data: NewSourceInput) => {
    setPendingAction({ type: "add-source" });
    const ok = await runAction(async () => {
      await api.post<IngestionSource>("/sources", data);
      await fetchData({ silent: true });
      toast.success("Source added successfully");
    });
    setPendingAction(null);
    if (!ok) throw new Error("add source failed");
  };

  const handleDeleteSource = async (id: number) => {
    setConfirm({
      title: "Delete source",
      message: "Are you sure you want to delete this source? This cannot be undone.",
      confirmLabel: "Delete",
      danger: true,
      action: async () => {
        setPendingAction({ type: "delete-source", id });
        await runAction(async () => {
          await api.delete(`/sources/${id}`);
          await fetchData({ silent: true });
          toast.success("Source deleted");
        });
        setPendingAction(null);
      },
    });
  };

  const handleAddCategory = async (data: NewCategoryInput) => {
    setPendingAction({ type: "add-category" });
    const ok = await runAction(async () => {
      await api.post<Category>("/categories", data);
      await fetchData({ silent: true });
      toast.success("Category added successfully");
    });
    setPendingAction(null);
    if (!ok) throw new Error("add category failed");
  };

  const handleDeleteCategory = async (id: number) => {
    setConfirm({
      title: "Delete category",
      message: "Are you sure you want to delete this category? This cannot be undone.",
      confirmLabel: "Delete",
      danger: true,
      action: async () => {
        setPendingAction({ type: "delete-category", id });
        await runAction(async () => {
          await api.delete(`/categories/${id}`);
          await fetchData({ silent: true });
          toast.success("Category deleted");
        });
        setPendingAction(null);
      },
    });
  };

  const handleToggleCategory = async (id: number, active: boolean) => {
    setPendingAction({ type: "toggle-category", id });
    await runAction(async () => {
      await api.patch<Category>(`/categories/${id}`, { is_active: active });
      await fetchData({ silent: true });
      toast.success(`Category ${active ? "activated" : "deactivated"}`);
    });
    setPendingAction(null);
  };

  const handleSyncDefaultCategories = async () => {
    setPendingAction({ type: "sync-categories" });
    await runAction(async () => {
      const result = await api.post<{ created: number; total: number }>("/categories/sync-defaults", null);
      await fetchData({ silent: true });
      toast.success(`Synced categories: ${result.created} created`);
    });
    setPendingAction(null);
  };

  const handleSyncDefaults = async () => {
    setPendingAction({ type: "sync-sources" });
    await runAction(async () => {
      const result = await api.post<{ created: number; updated: number }>("/sources/sync-defaults", null);
      await fetchData({ silent: true });
      toast.success(`Synced defaults: ${result.created} created, ${result.updated} updated`);
    });
    setPendingAction(null);
  };

  const handleTriggerJob = async () => {
    setPendingAction({ type: "trigger-job" });
    await runAction(async () => {
      await api.post("/jobs/aggregate", null);
      toast.success("Aggregation job triggered");
    });
    setPendingAction(null);
  };

  const handleFlushCache = async () => {
    setConfirm({
      title: "Flush Redis cache?",
      message: "This forces all data to be re-fetched from sources on the next request.",
      confirmLabel: "Flush Cache",
      danger: true,
      action: async () => {
        setPendingAction({ type: "flush-cache" });
        await runAction(async () => {
          const result = await api.post<{ status: string; deleted_keys: number }>("/admin/cache/flush", null);
          await fetchData({ silent: true });
          toast.success(`Cache flushed: ${result.deleted_keys} key(s) cleared`);
        });
        setPendingAction(null);
      },
    });
  };

  const handleDeleteAllNews = async () => {
    setConfirm({
      title: "Delete all news?",
      message: "This permanently removes every news article from the database. This cannot be undone.",
      confirmLabel: "Delete All News",
      danger: true,
      action: async () => {
        setPendingAction({ type: "delete-news" });
        await runAction(async () => {
          const result = await api.delete<{ message: string }>("/admin/news");
          await fetchData({ silent: true });
          toast.success(result.message || "All news deleted");
        });
        setPendingAction(null);
      },
    });
  };

  const changeTab = (tab: AdminTab) => {
    startTabTransition(() => setActiveTab(tab));
  };

  if (authLoading) {
    return <PageLoader label="Checking session" />;
  }

  const isActing = (type: string, id?: number) =>
    pendingAction?.type === type && (id === undefined || pendingAction.id === id);

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
          <p className="text-gray-600 mt-1">Manage your news aggregator</p>
        </div>
        <Button
          variant="secondary"
          icon={<RefreshCw className="w-4 h-4" />}
          onClick={() => fetchData({ silent: true })}
          loading={isRefreshing}
        >
          Refresh
        </Button>
      </div>

      <AdminTabs activeTab={activeTab} onChange={changeTab} isAdmin={isAdmin} />

      <div className={isPendingTab ? "opacity-60 transition-opacity duration-200" : "transition-opacity duration-200"}>
        {activeTab === "overview" &&
          (isLoading && !stats ? (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Array.from({ length: 8 }).map((_, i) => (
                <StatCardSkeleton key={i} />
              ))}
            </div>
          ) : stats ? (
            <OverviewTab stats={stats} />
          ) : null)}

        {activeTab === "users" && <UsersTab users={users} isLoading={isLoading} />}

        {activeTab === "sources" && (
          <SourcesTab
            sources={sources}
            isLoading={isLoading}
            isAdding={isActing("add-source")}
            isSyncing={isActing("sync-sources")}
            deletingId={isActing("delete-source") ? pendingAction?.id : undefined}
            onAddSource={handleAddSource}
            onDeleteSource={handleDeleteSource}
            onSyncDefaults={handleSyncDefaults}
          />
        )}

        {activeTab === "categories" && (
          <CategoriesTab
            categories={categories}
            isLoading={isLoading}
            isAdding={isActing("add-category")}
            isSyncing={isActing("sync-categories")}
            deletingId={isActing("delete-category") ? pendingAction?.id : undefined}
            togglingId={isActing("toggle-category") ? pendingAction?.id : undefined}
            onAddCategory={handleAddCategory}
            onDeleteCategory={handleDeleteCategory}
            onToggleCategory={handleToggleCategory}
            onSyncDefaults={handleSyncDefaultCategories}
          />
        )}

        {activeTab === "jobs" && (
          <JobsTab
            isTriggering={isActing("trigger-job")}
            isFlushing={isActing("flush-cache")}
            onTriggerJob={handleTriggerJob}
            onFlushCache={handleFlushCache}
          />
        )}

        {activeTab === "maintenance" && (
          <MaintenanceTab
            isDeletingNews={isActing("delete-news")}
            onDeleteAllNews={handleDeleteAllNews}
          />
        )}
      </div>

      {/* Global error banner */}
      {error && (
        <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm animate-fade-in">
          <span className="flex-1">{error}</span>
          <Button variant="secondary" size="sm" onClick={() => fetchData()}>
            Retry
          </Button>
        </div>
      )}

      <ConfirmDialog
        open={confirm !== null}
        title={confirm?.title ?? ""}
        message={confirm?.message ?? ""}
        confirmLabel={confirm?.confirmLabel}
        danger={confirm?.danger}
        loading={pendingAction !== null}
        onConfirm={async () => {
          if (confirm) {
            await confirm.action();
            setConfirm(null);
          }
        }}
        onCancel={() => setConfirm(null)}
      />
    </div>
  );
}
