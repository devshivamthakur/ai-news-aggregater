
import { createContext, useCallback, useContext, useMemo, useRef, useState } from "react";
import { CheckCircle2, Info, X, XCircle } from "lucide-react";
import { cn } from "@/shared/cn";

type ToastType = "success" | "error" | "info";

interface ToastItem {
  id: number;
  type: ToastType;
  message: string;
}

interface ToastContextValue {
  success: (message: string) => void;
  error: (message: string) => void;
  info: (message: string) => void;
}

const ToastContext = createContext<ToastContextValue | undefined>(undefined);

const TOAST_STYLES: Record<ToastType, string> = {
  success: "bg-emerald-50/95 border-emerald-200 text-emerald-800",
  error: "bg-red-50/95 border-red-200 text-red-800",
  info: "bg-white/95 border-slate-200 text-slate-800",
};

const TOAST_ICONS: Record<ToastType, React.ReactNode> = {
  success: <CheckCircle2 className="h-5 w-5 flex-shrink-0 text-emerald-600" />,
  error: <XCircle className="h-5 w-5 flex-shrink-0 text-red-600" />,
  info: <Info className="h-5 w-5 flex-shrink-0 text-brand-600" />,
};

const DURATION_MS = 4000;
let nextToastId = 1;

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([]);
  const timers = useRef<Map<number, ReturnType<typeof setTimeout>>>(new Map());

  const dismiss = useCallback((id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
    const timer = timers.current.get(id);
    if (timer) {
      clearTimeout(timer);
      timers.current.delete(id);
    }
  }, []);

  const push = useCallback(
    (type: ToastType, message: string) => {
      const id = nextToastId++;
      setToasts((prev) => [...prev.slice(-3), { id, type, message }]);
      const timer = setTimeout(() => dismiss(id), DURATION_MS);
      timers.current.set(id, timer);
    },
    [dismiss]
  );

  const value = useMemo<ToastContextValue>(
    () => ({
      success: (m) => push("success", m),
      error: (m) => push("error", m),
      info: (m) => push("info", m),
    }),
    [push]
  );

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div
        aria-live="polite"
        className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 w-[min(24rem,calc(100vw-2rem))]"
      >
        {toasts.map((toast) => (
          <div
            key={toast.id}
            role="status"
            className={cn(
              "toast-in flex items-start gap-3 rounded-2xl border p-4 shadow-lg backdrop-blur-xl",
              TOAST_STYLES[toast.type]
            )}
          >
            {TOAST_ICONS[toast.type]}
            <p className="flex-1 pt-0.5 text-sm font-medium leading-snug">{toast.message}</p>
            <button
              onClick={() => dismiss(toast.id)}
              className="rounded-md p-1 transition-colors hover:bg-black/5 flex-shrink-0"
              aria-label="Dismiss notification"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within a ToastProvider");
  }
  return context;
}
