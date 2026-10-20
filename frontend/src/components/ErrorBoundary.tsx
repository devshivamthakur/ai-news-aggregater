import { Component, type ReactNode } from "react";
import { AlertTriangle, RefreshCw, Home as HomeIcon } from "lucide-react";
import { Link } from "react-router-dom";
import Button from "./ui/Button";

interface Props {
  children: ReactNode;
}

interface State {
  error: Error | null;
}

/** Matches the transient chunk failures the old Next error boundary handled. */
function isChunkLoadError(error: Error): boolean {
  const message = error?.message || "";
  return (
    error?.name === "ChunkLoadError" ||
    /loading chunk [\w-]+ failed/i.test(message) ||
    /loading css chunk/i.test(message) ||
    /failed to fetch dynamically imported module/i.test(message) ||
    /importing a module script failed/i.test(message) ||
    /\/assets\//.test(message)
  );
}

const RELOAD_GUARD_KEY = "chunk-error-reloaded";

/**
 * Top-level error boundary. A stale chunk reference (common in dev after a
 * recompile, or right after a deploy) is fixed by one fresh page load — we do
 * that automatically, guarded against infinite reload loops. Everything else
 * gets a friendly screen with retry / reload actions.
 */
export default class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error) {
    if (!isChunkLoadError(error) || typeof window === "undefined") return;
    try {
      if (!sessionStorage.getItem(RELOAD_GUARD_KEY)) {
        sessionStorage.setItem(RELOAD_GUARD_KEY, "1");
        window.location.reload();
      }
    } catch {
      // sessionStorage unavailable (privacy mode) — fall through to the UI.
    }
  }

  reset = () => {
    try {
      sessionStorage.removeItem(RELOAD_GUARD_KEY);
    } catch {
      /* ignore */
    }
    this.setState({ error: null });
  };

  reload = () => {
    try {
      sessionStorage.removeItem(RELOAD_GUARD_KEY);
    } catch {
      /* ignore */
    }
    window.location.reload();
  };

  render() {
    const { error } = this.state;
    if (!error) return this.props.children;

    const chunk = isChunkLoadError(error);

    return (
      <div className="flex min-h-[60vh] items-center justify-center px-4">
        <div className="card animate-pop-in w-full max-w-md border-0 text-center shadow-2xl">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-red-50 to-red-100">
            <AlertTriangle className="h-8 w-8 text-red-600" />
          </div>
          <h1 className="text-xl font-bold text-slate-900">
            {chunk ? "Just a hiccup" : "Something went wrong"}
          </h1>
          <p className="mt-2 text-sm leading-relaxed text-slate-600">
            {chunk
              ? "A part of the page didn't load — this usually happens during a quick reload. Reload once to carry on."
              : error?.message || "Something unexpected happened. Please try again."}
          </p>
          <div className="mt-6 flex flex-wrap items-center justify-center gap-2">
            <Button onClick={this.reload} icon={<RefreshCw className="h-4 w-4" />}>
              Reload page
            </Button>
            {!chunk && (
              <Button variant="secondary" onClick={this.reset}>
                Try again
              </Button>
            )}
            <Link to="/" className="btn-ghost text-sm">
              <HomeIcon className="h-4 w-4" />
              Go home
            </Link>
          </div>
        </div>
      </div>
    );
  }
}
