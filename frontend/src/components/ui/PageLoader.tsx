import { Newspaper } from "lucide-react";
import Spinner from "./Spinner";

interface PageLoaderProps {
  label?: string;
}

/** Full-page branded loader used for route transitions and auth gates. */
export default function PageLoader({ label = "Loading" }: PageLoaderProps) {
  return (
    <div className="flex min-h-[60vh] items-center justify-center" role="status" aria-label={label}>
      <div className="flex animate-fade-in flex-col items-center gap-5">
        <div className="relative flex h-16 w-16 items-center justify-center rounded-3xl bg-gradient-to-br from-brand-500 to-accent-500 shadow-glow">
          <Newspaper className="h-8 w-8 text-white" />
          <span className="absolute inset-0 rounded-3xl bg-brand-400/40 animate-ping-soft" />
        </div>
        <div className="flex items-center gap-3">
          <Spinner size="md" />
          <span className="text-sm font-medium text-slate-500">{label}…</span>
        </div>
      </div>
    </div>
  );
}
