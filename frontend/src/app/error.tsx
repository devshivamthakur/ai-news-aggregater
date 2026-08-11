"use client";

import { useEffect } from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";
import Button from "@/components/ui/Button";

const RELOAD_GUARD_KEY = "chunk-error-reloaded";

function isChunkLoadError(error: Error): boolean {
  const message = error?.message || "";
  return (
    error?.name === "ChunkLoadError" ||
    /loading chunk [\w-]+ failed/i.test(message) ||
    /loading css chunk/i.test(message) ||
    /failed to fetch dynamically imported module/i.test(message) ||
    /_next\/static\/chunks/.test(message)
  );
}

/**
 * Global route error boundary. A stale chunk reference (common in dev after
 * recompiles, or right after a deploy) is fixed by one fresh page load — we
 * do that automatically, guarded against infinite reload loops. All other
 * errors get a friendly screen with retry / reload actions.
 */
export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const isChunkError = isChunkLoadError(error);

  useEffect(() => {
    if (isChunkError && typeof window !== "undefined") {
      try {
        if (!sessionStorage.getItem(RELOAD_GUARD_KEY)) {
          sessionStorage.setItem(RELOAD_GUARD_KEY, "1");
          window.location.reload();
        }
      } catch {
        // sessionStorage unavailable (privacy mode) — fall through to the UI.
      }
    }
  }, [isChunkError]);

  return (
    <div className="flex items-center justify-center min-h-[60vh] px-4">
      <div className="card w-full max-w-md text-center animate-pop-in">
        <div className="w-14 h-14 bg-red-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <AlertTriangle className="w-7 h-7 text-red-600" />
        </div>
        <h1 className="text-xl font-bold text-gray-900 mb-2">
          {isChunkError ? "Just a hiccup" : "Something went wrong"}
        </h1>
        <p className="text-sm text-gray-600 mb-6">
          {isChunkError
            ? "A page module failed to load — this usually happens during a hot reload. Reload once to continue."
            : error?.message || "An unexpected error occurred. Please try again."}
        </p>
        <div className="flex justify-center gap-2">
          <Button
            onClick={() => {
              try {
                sessionStorage.removeItem(RELOAD_GUARD_KEY);
              } catch {
                /* ignore */
              }
              window.location.reload();
            }}
            icon={<RefreshCw className="w-4 h-4" />}
          >
            Reload page
          </Button>
          {!isChunkError && (
            <Button variant="secondary" onClick={reset}>
              Try again
            </Button>
          )}
        </div>
        {error?.digest && <p className="text-xs text-gray-400 mt-4">Digest: {error.digest}</p>}
      </div>
    </div>
  );
}
