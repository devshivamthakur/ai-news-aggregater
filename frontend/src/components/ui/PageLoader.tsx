import { Newspaper } from "lucide-react";
import Spinner from "./Spinner";

interface PageLoaderProps {
  label?: string;
}

/** Full-page branded loader used for route transitions and auth gates. */
export default function PageLoader({ label = "Loading" }: PageLoaderProps) {
  return (
    <div className="flex items-center justify-center min-h-[60vh]" role="status" aria-label={label}>
      <div className="flex flex-col items-center gap-5 animate-fade-in">
        <div className="w-14 h-14 bg-gradient-to-br from-brand-500 to-brand-700 rounded-2xl flex items-center justify-center shadow-lg shadow-brand-600/25 animate-pulse">
          <Newspaper className="w-7 h-7 text-white" />
        </div>
        <div className="flex items-center gap-3">
          <Spinner size="md" />
          <span className="text-sm text-gray-500 font-medium">{label}…</span>
        </div>
      </div>
    </div>
  );
}
