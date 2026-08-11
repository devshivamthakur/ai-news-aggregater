"use client";

import { useState } from "react";
import { IngestionSource } from "@/lib/api";
import { Plus, Trash2, RefreshCw } from "lucide-react";
import Button from "@/components/ui/Button";
import { ListRowSkeleton } from "@/components/ui/Skeleton";

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

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Ingestion Sources</h2>
        <div className="flex items-center gap-2">
          <Button
            variant="secondary"
            size="sm"
            icon={<RefreshCw className="w-4 h-4" />}
            onClick={onSyncDefaults}
            loading={isSyncing}
          >
            Sync Defaults
          </Button>
          <Button
            variant="primary"
            size="sm"
            icon={<Plus className="w-4 h-4" />}
            onClick={() => setShowAdd((show) => !show)}
          >
            {showAdd ? "Cancel" : "Add Source"}
          </Button>
        </div>
      </div>

      {showAdd && (
        <form onSubmit={handleSubmit} className="mb-4 p-4 bg-gray-50 rounded-lg space-y-3 animate-fade-in">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
              <select
                value={newSource.source_type}
                onChange={(e) => setNewSource({ ...newSource, source_type: e.target.value as NewSourceInput["source_type"] })}
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
              {newSource.source_type === "rss" ? "RSS URL" :
               newSource.source_type === "medium" ? "Medium RSS URL" : "Channel ID"}
            </label>
            <input
              type="text"
              value={newSource.identifier}
              onChange={(e) => setNewSource({ ...newSource, identifier: e.target.value })}
              className="input"
              placeholder={
                newSource.source_type === "rss" ? "https://example.com/feed.xml" :
                newSource.source_type === "medium" ? "https://medium.com/feed/@publication" :
                "UCxxxxxxxxxxxxxxxx"
              }
              required
            />
          </div>
          <div className="flex items-center gap-2">
            <Button type="submit" size="sm" loading={isAdding}>
              Add Source
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
        <p className="text-gray-500 text-center py-8">No sources configured. Add one above or sync defaults.</p>
      ) : (
        <div className="space-y-2">
          {sources.map((source) => (
            <div key={source.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100/70 transition-colors">
              <div className="flex items-center gap-3">
                <span className={`badge ${
                  source.source_type === "rss" ? "badge-brand" :
                  source.source_type === "medium" ? "badge-green" : "badge-green"
                }`}>
                  {source.source_type}
                </span>
                <div>
                  <p className="font-medium text-gray-900 text-sm">{source.display_name}</p>
                  <p className="text-xs text-gray-500 truncate max-w-md">{source.identifier}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs text-gray-400">
                      Fetched: {source.total_fetches || 0} times
                    </span>
                    {source.last_fetched_at && (
                      <span className="text-xs text-gray-400">
                        Last: {new Date(source.last_fetched_at).toLocaleDateString()}
                      </span>
                    )}
                    {source.consecutive_errors > 0 && (
                      <span className="text-xs text-red-500">
                        {source.consecutive_errors} errors
                      </span>
                    )}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className={`badge ${
                  source.status === "active" ? "badge-green" :
                  source.status === "error" ? "badge-gray" : "badge-gray"
                }`}>
                  {source.status}
                </span>
                <button
                  onClick={() => onDeleteSource(source.id)}
                  disabled={deletingId === source.id}
                  className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
                  aria-label={`Delete ${source.display_name}`}
                >
                  <Trash2 className={`w-4 h-4 ${deletingId === source.id ? "animate-pulse" : ""}`} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
