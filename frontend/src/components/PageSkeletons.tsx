import { NewsCardSkeleton, StatCardSkeleton, ListRowSkeleton, Skeleton } from "./ui/Skeleton";

/** Route-level skeletons shown while a lazy page chunk loads. */

export function NewsPageSkeleton() {
  return (
    <div className="space-y-6" aria-busy="true" aria-label="Loading news">
      <div className="space-y-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <NewsCardSkeleton key={i} />
        ))}
      </div>
    </div>
  );
}

export function AdminPageSkeleton() {
  return (
    <div className="space-y-6" aria-busy="true" aria-label="Loading admin dashboard">
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <StatCardSkeleton key={i} />
        ))}
      </div>
      <ListRowSkeleton rows={3} />
    </div>
  );
}

export function SettingsPageSkeleton() {
  return (
    <div className="mx-auto max-w-4xl space-y-6" aria-busy="true" aria-label="Loading settings">
      <Skeleton className="h-9 w-48" />
      <div className="flex gap-1 rounded-2xl border border-slate-200 bg-white p-1.5">
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="h-9 flex-1 rounded-xl" />
        ))}
      </div>
      <div className="card space-y-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="flex items-center justify-between py-2">
            <div className="space-y-2">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-5 w-40" />
            </div>
            <Skeleton className="h-8 w-20" />
          </div>
        ))}
      </div>
    </div>
  );
}
