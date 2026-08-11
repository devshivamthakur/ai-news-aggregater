"use client";

import { Zap, Database } from "lucide-react";
import Button from "@/components/ui/Button";

interface JobsTabProps {
  isTriggering?: boolean;
  isFlushing?: boolean;
  onTriggerJob: () => void;
  onFlushCache: () => void;
}

export default function JobsTab({ isTriggering = false, isFlushing = false, onTriggerJob, onFlushCache }: JobsTabProps) {
  return (
    <div className="card">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Background Jobs</h2>
      <div className="space-y-4">
        <div className="p-4 bg-gray-50 rounded-lg">
          <h3 className="font-medium text-gray-900 mb-2">Manual Aggregation</h3>
          <p className="text-sm text-gray-600 mb-3">
            Trigger a full aggregation cycle: fetch from all active sources, analyze with AI, store in database, and send email digests.
          </p>
          <Button icon={<Zap className="w-4 h-4" />} onClick={onTriggerJob} loading={isTriggering}>
            {isTriggering ? "Running…" : "Run Aggregation Now"}
          </Button>
        </div>
        <div className="p-4 bg-gray-50 rounded-lg">
          <h3 className="font-medium text-gray-900 mb-2">Scheduled Aggregation</h3>
          <p className="text-sm text-gray-600">
            The scheduler runs automatically at the configured hour (default: 8:00 UTC) daily.
            You can also use an external cron service to POST to <code className="bg-gray-200 px-1 rounded">/api/v1/jobs/aggregate</code>.
          </p>
        </div>
        <div className="p-4 bg-gray-50 rounded-lg">
          <h3 className="font-medium text-gray-900 mb-2">Cache Management</h3>
          <p className="text-sm text-gray-600 mb-3">
            Clear the Redis response cache. Useful after manual database changes to force fresh data on the next request.
          </p>
          <Button
            variant="secondary"
            icon={<Database className="w-4 h-4" />}
            onClick={onFlushCache}
            loading={isFlushing}
          >
            {isFlushing ? "Flushing…" : "Flush Redis Cache"}
          </Button>
        </div>
      </div>
    </div>
  );
}
