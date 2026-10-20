
import { Trash2, Newspaper, AlertTriangle } from "lucide-react";
import Button from "@/components/ui/Button";

interface MaintenanceTabProps {
  isDeletingNews?: boolean;
  onDeleteAllNews: () => void;
}

export default function MaintenanceTab({ isDeletingNews = false, onDeleteAllNews }: MaintenanceTabProps) {
  return (
    <div className="card">
      <div className="mb-5 flex items-center gap-2.5">
        <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-50 text-brand-600">
          <Trash2 className="h-4 w-4" />
        </span>
        <div>
          <h2 className="text-lg font-semibold text-slate-900">Maintenance</h2>
          <p className="text-xs text-slate-400">Big, rarely used actions</p>
        </div>
      </div>

      <div className="space-y-4">
        <div className="rounded-xl border border-red-100 bg-gradient-to-br from-red-50 to-white p-5">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="max-w-xl">
              <div className="mb-1.5 flex items-center gap-2">
                <Newspaper className="h-4 w-4 text-red-600" />
                <h3 className="font-semibold text-slate-900">Clear every story</h3>
              </div>
              <p className="text-sm leading-relaxed text-slate-600">
                Remove all collected stories from the archive. Their summaries and brief history go
                too, and it can&apos;t be undone.
              </p>
            </div>
            <Button
              variant="danger"
              icon={<Trash2 className="h-4 w-4" />}
              onClick={onDeleteAllNews}
              loading={isDeletingNews}
            >
              {isDeletingNews ? "Deleting…" : "Clear all stories"}
            </Button>
          </div>

          <p className="mt-3 flex items-start gap-1.5 text-xs text-red-600">
            <AlertTriangle className="mt-0.5 h-3.5 w-3.5 flex-shrink-0" />
            Double-check with your team before running this — it cannot be reversed.
          </p>
        </div>
      </div>
    </div>
  );
}
