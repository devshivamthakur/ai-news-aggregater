import { lazy, type ComponentType } from "react";

/**
 * Detects webpack/Vite chunk-load failures. These are transient in dev (the
 * dev server recompiled and the old chunk URL is stale) and after deployments
 * (the browser holds an old chunk manifest).
 */
export function isChunkLoadError(err: unknown): boolean {
  if (!err) return false;
  const name = err instanceof Error ? err.name : "";
  const message = err instanceof Error ? err.message : String(err);
  return (
    name === "ChunkLoadError" ||
    /loading chunk [\w-]+ failed/i.test(message) ||
    /loading css chunk/i.test(message) ||
    /failed to fetch dynamically imported module/i.test(message) ||
    /importing a module script failed/i.test(message) ||
    /\/assets\//.test(message)
  );
}

/**
 * `React.lazy` with automatic retry on transient chunk-load failures. In dev,
 * the first import often happens while the server is still recompiling; a
 * short delay + retry resolves it without a jarring full-page reload.
 *
 *   const News = lazyWithRetry(() => import("@/pages/News"));
 */
export default function lazyWithRetry<P extends object>(
  factory: () => Promise<{ default: ComponentType<P> }>,
  retries = 2
): ComponentType<P> {
  return lazy(() =>
    factory().catch(async (err) => {
      if (isChunkLoadError(err) && retries > 0) {
        await new Promise((resolve) => setTimeout(resolve, 800));
        return factory();
      }
      throw err;
    })
  ) as unknown as ComponentType<P>;
}
