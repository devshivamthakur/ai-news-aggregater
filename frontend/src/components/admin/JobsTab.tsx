
import { Zap, Database, CalendarClock, RefreshCcw } from "lucide-react";
import Button from "@/components/ui/Button";

interface JobsTabProps {
  isTriggering?: boolean;
  isFlushing?: boolean;
  onTriggerJob: () => void;
  onFlushCache: () => void;
}

export default function JobsTab({
  isTriggering = false,
  isFlushing = false,
  onTriggerJob,
  onFlushCache,
}: JobsTabProps) {
  return (
    <div className="card">
      <div className="mb-5 flex items-center gap-2.5">
        <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-50 text-brand-600">
          <Zap className="h-4 w-4" />
        </span>
        <div>
          <h2 className="text-lg font-semibold text-slate-900">Jobs</h2>
          <p className="text-xs text-slate-400">When and how fresh stories arrive</p>
        </div>
      </div>

      <div className="space-y-4">
        {/* Manual run */}
        <div className="rounded-xl border border-brand-100 bg-gradient-to-br from-brand-50 to-white p-5">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="max-w-xl">
              <div className="mb-1.5 flex items-center gap-2">
                <RefreshCcw className="h-4 w-4 text-brand-600" />
                <h3 className="font-semibold text-slate-900">Run a refresh now</h3>
              </div>
              <p className="text-sm leading-relaxed text-slate-600">
                Pull the latest stories from every source, summarize them, and send out any queued
                briefs — all in one go.
              </p>
            </div>
            <Button icon={<Zap className="h-4 w-4" />} onClick={onTriggerJob} loading={isTriggering}>
              {isTriggering ? "Running…" : "Run now"}
            </Button>
          </div>
        </div>

        {/* Scheduled */}
        <div className="rounded-xl border border-slate-100 bg-slate-50 p-5">
          <div className="mb-1.5 flex items-center gap-2">
            <CalendarClock className="h-4 w-4 text-slate-500" />
            <h3 className="font-semibold text-slate-900">Automatic daily refresh</h3>
          </div>
          <p className="text-sm leading-relaxed text-slate-600">
            Stories are gathered on their own every day at the configured hour (default 8:00 AM UTC).
            You can also trigger it from a scheduled task that posts to{" "}
            <code className="rounded bg-slate-200 px-1.5 py-0.5 text-xs">/api/v1/jobs/aggregate</code>.
          </p>
        </div>

        {/* Cache */}
        <div className="rounded-xl border border-slate-100 bg-slate-50 p-5">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="max-w-xl">
              <div className="mb-1.5 flex items-center gap-2">
                <Database className="h-4 w-4 text-slate-500" />
                <h3 className="font-semibold text-slate-900">Clear cached responses</h3>
              </div>
              <p className="text-sm leading-relaxed text-slate-600">
                Handy after changing data by hand — everything is re-fetched fresh on the next load.
              </p>
            </div>
            <Button
              variant="secondary"
              icon={<Database className="h-4 w-4" />}
              onClick={onFlushCache}
              loading={isFlushing}
            >
              {isFlushing ? "Clearing…" : "Clear cache"}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
