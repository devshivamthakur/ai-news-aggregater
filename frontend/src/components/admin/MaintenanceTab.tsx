"use client";

import { Trash2, Newspaper } from "lucide-react";
import Button from "@/components/ui/Button";

interface MaintenanceTabProps {
  isDeletingNews?: boolean;
  onDeleteAllNews: () => void;
}

export default function MaintenanceTab({
  isDeletingNews = false,
  onDeleteAllNews,
}: MaintenanceTabProps) {
  return (
    <div className="card">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Database Maintenance</h2>
      <div className="space-y-4">
        <div className="p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <Newspaper className="w-5 h-5 text-red-600" />
            <h3 className="font-medium text-gray-900">Delete All News</h3>
          </div>
          <p className="text-sm text-gray-600 mb-3">
            Permanently remove every news article from the database. This cannot be undone and will
            also clear associated analysis and digest history.
          </p>
          <Button
            variant="danger"
            icon={<Trash2 className="w-4 h-4" />}
            onClick={onDeleteAllNews}
            loading={isDeletingNews}
          >
            {isDeletingNews ? "Deleting…" : "Delete All News"}
          </Button>
        </div>
      </div>
    </div>
  );
}
