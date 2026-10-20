
import { useState } from "react";
import { IngestionSource } from "@/shared/api";
import { Plus, Trash2, RefreshCw, Rss, CalendarDays } from "lucide-react";
import Button from "@/components/ui/Button";
import { ListRowSkeleton } from "@/components/ui/Skeleton";
import EmptyState from "@/components/ui/EmptyState";
import { cn } from "@/shared/cn";

export interface NewSourceInput {
  source_type: "rss" | "youtube" | "medium";
  display_name: string;
  identifier: string;
  is_active: boolean;
}

interface SourcesTabProps {
  sources: IngestionSource[];
  isLoading: boolean;
  isAdding?: boolean;
  isSyncing?: boolean;
  deletingId?: number;
  onAddSource: (data: NewSourceInput) => Promise<void>;
  onDeleteSource: (id: number) => void;
  onSyncDefaults: () => void;
}

const EMPTY_SOURCE: NewSourceInput = {
  source_type: "rss",
  display_name: "",
  identifier: "",
  is_active: true,
};

export default function SourcesTab({
  sources,
  isLoading,
  isAdding = false,
  isSyncing = false,
  deletingId,
  onAddSource,
  onDeleteSource,
  onSyncDefaults,
}: SourcesTabProps) {
  const [showAdd, setShowAdd] = useState(false);
  const [newSource, setNewSource] = useState<NewSourceInput>(EMPTY_SOURCE);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await onAddSource(newSource);
      setNewSource(EMPTY_SOURCE);
      setShowAdd(false);
    } catch {
      // Keep the form open; the parent surfaces the error via toast.
    }
  };

  const statusStyle = (status: string) =>
    status === "active"
      ? "bg-emerald-50 text-emerald-700 ring-emerald-100"
      : status === "error"
        ? "bg-red-50 text-red-700 ring-red-100"
        : "bg-slate-100 text-slate-600 ring-slate-200";

  return (
    <div className="card">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2.5">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-50 text-brand-600">
            <Rss className="h-4 w-4" />
          </span>
          <div>
            <h2 className="text-lg font-semibold text-slate-900">Sources we follow</h2>
            <p className="text-xs text-slate-400">Where the stories come from</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="secondary"
            size="sm"
            icon={<RefreshCw className="h-4 w-4" />}
            onClick={onSyncDefaults}
            loading={isSyncing}
          >
            Sync defaults
          </Button>
          <Button size="sm" icon={<Plus className="h-4 w-4" />} onClick={() => setShowAdd((show) => !show)}>
            {showAdd ? "Cancel" : "Add source"}
          </Button>
        </div>
      </div>

      {showAdd && (
        <form onSubmit={handleSubmit} className="animate-fade-in mb-4 space-y-3 rounded-xl bg-slate-50 p-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Type</label>
              <select
                value={newSource.source_type}
                onChange={(e) =>
                  setNewSource({ ...newSource, source_type: e.target.value as NewSourceInput["source_type"] })
                }
                className="input"
              >
                <option value="rss">RSS feed</option>
                <option value="youtube">YouTube channel</option>
                <option value="medium">Medium publication</option>
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Display name</label>
              <input
                type="text"
                value={newSource.display_name}
                onChange={(e) => setNewSource({ ...newSource, display_name: e.target.value })}
                className="input"
                placeholder="My source"
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
            <Button type="submit" size="sm" loading={isAdding}>
              Add source
            </Button>
            <Button variant="secondary" size="sm" onClick={() => setShowAdd(false)} disabled={isAdding}>
              Cancel
            </Button>
          </div>
        </form>
      )}

      {isLoading ? (
        <ListRowSkeleton rows={5} />
      ) : sources.length === 0 ? (
        <EmptyState
          icon={<Rss className="h-7 w-7" />}
          title="No sources configured"
          description="Add one above or sync the defaults to get started."
        />
      ) : (
        <div className="space-y-2">
          {sources.map((source) => (
            <div
              key={source.id}
              className="flex items-center justify-between gap-3 rounded-xl bg-slate-50 p-3 transition-colors hover:bg-slate-100/70"
            >
              <div className="flex min-w-0 items-center gap-3">
                <span
                  className={cn(
                    "badge ring-1 ring-inset",
                    source.source_type === "rss"
                      ? "bg-brand-50 text-brand-700 ring-brand-100"
                      : "bg-emerald-50 text-emerald-700 ring-emerald-100"
                  )}
                >
                  {source.source_type}
                </span>
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium text-slate-900">{source.display_name}</p>
                  <p className="max-w-md truncate text-xs text-slate-400">{source.identifier}</p>
                  <div className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-0.5">
                    <span className="text-xs text-slate-400">
                      Fetched {source.total_fetches || 0} times
                    </span>
                    {source.last_fetched_at && (
                      <span className="inline-flex items-center gap-1 text-xs text-slate-400">
                        <CalendarDays className="h-3 w-3" />
                        {new Date(source.last_fetched_at).toLocaleDateString()}
                      </span>
                    )}
                    {source.consecutive_errors > 0 && (
                      <span className="text-xs font-medium text-red-500">
                        {source.consecutive_errors} errors
                      </span>
                    )}
                  </div>
                </div>
              </div>
              <div className="flex flex-shrink-0 items-center gap-2">
                <span className={cn("badge ring-1 ring-inset", statusStyle(source.status))}>
                  {source.status}
                </span>
                <button
                  onClick={() => onDeleteSource(source.id)}
                  disabled={deletingId === source.id}
                  className="rounded-lg p-1.5 text-slate-400 transition-colors hover:bg-red-50 hover:text-red-500 disabled:opacity-50"
                  aria-label={`Delete ${source.display_name}`}
                >
                  <Trash2 className={cn("h-4 w-4", deletingId === source.id && "animate-pulse")} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
