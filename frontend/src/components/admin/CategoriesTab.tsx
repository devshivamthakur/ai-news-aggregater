
import { useState } from "react";
import { Category } from "@/shared/api";
import { Plus, Trash2, RefreshCw, Tag } from "lucide-react";
import Button from "@/components/ui/Button";
import { ListRowSkeleton } from "@/components/ui/Skeleton";
import EmptyState from "@/components/ui/EmptyState";
import { cn } from "@/shared/cn";

export interface NewCategoryInput {
  name: string;
  description: string;
  is_active: boolean;
}

interface CategoriesTabProps {
  categories: Category[];
  isLoading: boolean;
  isAdding?: boolean;
  isSyncing?: boolean;
  deletingId?: number;
  togglingId?: number;
  onAddCategory: (data: NewCategoryInput) => Promise<void>;
  onDeleteCategory: (id: number) => void;
  onToggleCategory: (id: number, active: boolean) => void;
  onSyncDefaults: () => void;
}

const EMPTY_CATEGORY: NewCategoryInput = {
  name: "",
  description: "",
  is_active: true,
};

export default function CategoriesTab({
  categories,
  isLoading,
  isAdding = false,
  isSyncing = false,
  deletingId,
  togglingId,
  onAddCategory,
  onDeleteCategory,
  onToggleCategory,
  onSyncDefaults,
}: CategoriesTabProps) {
  const [showAdd, setShowAdd] = useState(false);
  const [newCategory, setNewCategory] = useState<NewCategoryInput>(EMPTY_CATEGORY);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await onAddCategory(newCategory);
      setNewCategory(EMPTY_CATEGORY);
      setShowAdd(false);
    } catch {
      // Keep the form open; the parent surfaces the error via toast.
    }
  };

  return (
    <div className="card">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2.5">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-50 text-brand-600">
            <Tag className="h-4 w-4" />
          </span>
          <div>
            <h2 className="text-lg font-semibold text-slate-900">Topics</h2>
            <p className="text-xs text-slate-400">How stories are grouped for readers</p>
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
            {showAdd ? "Cancel" : "Add topic"}
          </Button>
        </div>
      </div>

      {showAdd && (
        <form onSubmit={handleSubmit} className="animate-fade-in mb-4 space-y-3 rounded-xl bg-slate-50 p-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Topic name</label>
              <input
                type="text"
                value={newCategory.name}
                onChange={(e) => setNewCategory({ ...newCategory, name: e.target.value })}
                className="input"
                placeholder="e.g. AI, Space, Finance"
                required
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Description</label>
              <input
                type="text"
                value={newCategory.description}
                onChange={(e) => setNewCategory({ ...newCategory, description: e.target.value })}
                className="input"
                placeholder="A short line about it"
              />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button type="submit" size="sm" loading={isAdding}>
              Add topic
            </Button>
            <Button variant="secondary" size="sm" onClick={() => setShowAdd(false)} disabled={isAdding}>
              Cancel
            </Button>
          </div>
        </form>
      )}

      {isLoading ? (
        <ListRowSkeleton rows={5} />
      ) : categories.length === 0 ? (
        <EmptyState
          icon={<Tag className="h-7 w-7" />}
          title="No topics yet"
          description="Sync the defaults or add one above to start organizing stories."
        />
      ) : (
        <div className="space-y-2">
          {categories.map((category) => (
            <div
              key={category.id}
              className="flex items-center justify-between gap-3 rounded-xl bg-slate-50 p-3 transition-colors hover:bg-slate-100/70"
            >
              <div className="min-w-0">
                <p className="truncate text-sm font-medium text-slate-900">{category.name}</p>
                {category.description && (
                  <p className="truncate text-xs text-slate-400">{category.description}</p>
                )}
              </div>
              <div className="flex flex-shrink-0 items-center gap-4">
                <button
                  onClick={() => onToggleCategory(category.id, !category.is_active)}
                  disabled={togglingId === category.id}
                  className={cn(
                    "badge cursor-pointer ring-1 ring-inset transition-opacity disabled:opacity-50",
                    category.is_active
                      ? "bg-emerald-50 text-emerald-700 ring-emerald-100"
                      : "bg-slate-100 text-slate-600 ring-slate-200"
                  )}
                >
                  {togglingId === category.id
                    ? "Updating…"
                    : category.is_active
                      ? "Active"
                      : "Hidden"}
                </button>
                <button
                  onClick={() => onDeleteCategory(category.id)}
                  disabled={deletingId === category.id}
                  className="rounded-lg p-1.5 text-slate-400 transition-colors hover:bg-red-50 hover:text-red-500 disabled:opacity-50"
                  aria-label={`Delete ${category.name}`}
                >
                  <Trash2 className={cn("h-4 w-4", deletingId === category.id && "animate-pulse")} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
