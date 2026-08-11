"use client";

import { useState } from "react";
import { Category } from "@/lib/api";
import { Plus, Trash2, RefreshCw } from "lucide-react";
import Button from "@/components/ui/Button";
import { ListRowSkeleton } from "@/components/ui/Skeleton";

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
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Manage Categories</h2>
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
            {showAdd ? "Cancel" : "Add Category"}
          </Button>
        </div>
      </div>

      {showAdd && (
        <form onSubmit={handleSubmit} className="mb-4 p-4 bg-gray-50 rounded-lg space-y-3 animate-fade-in">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Category Name</label>
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
              <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <input
                type="text"
                value={newCategory.description}
                onChange={(e) => setNewCategory({ ...newCategory, description: e.target.value })}
                className="input"
                placeholder="Short description"
              />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button type="submit" size="sm" loading={isAdding}>
              Add Category
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
        <p className="text-gray-500 text-center py-8">No categories configured. Sync defaults or add one above.</p>
      ) : (
        <div className="space-y-2">
          {categories.map((category) => (
            <div key={category.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100/70 transition-colors">
              <div>
                <p className="font-medium text-gray-900 text-sm">{category.name}</p>
                {category.description && (
                  <p className="text-xs text-gray-500">{category.description}</p>
                )}
              </div>
              <div className="flex items-center gap-4">
                <button
                  onClick={() => onToggleCategory(category.id, !category.is_active)}
                  disabled={togglingId === category.id}
                  className={`badge ${category.is_active ? "badge-green" : "badge-gray"} cursor-pointer disabled:opacity-50 transition-opacity`}
                >
                  {togglingId === category.id ? "Updating…" : category.is_active ? "Active" : "Inactive"}
                </button>
                <button
                  onClick={() => onDeleteCategory(category.id)}
                  disabled={deletingId === category.id}
                  className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
                  aria-label={`Delete ${category.name}`}
                >
                  <Trash2 className={`w-4 h-4 ${deletingId === category.id ? "animate-pulse" : ""}`} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
