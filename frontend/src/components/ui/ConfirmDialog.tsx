
import { AlertTriangle, Sparkles } from "lucide-react";
import Button from "./Button";

interface ConfirmDialogProps {
  open: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  danger?: boolean;
  loading?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

/** Accessible confirmation modal that replaces the native `confirm()`. */
export default function ConfirmDialog({
  open,
  title,
  message,
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  danger = false,
  loading = false,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-[90] flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-label={title}
    >
      <div className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm animate-fade-in" onClick={onCancel} />
      <div className="card animate-pop-in relative w-full max-w-md border-0 p-6 shadow-2xl">
        <div className="flex items-start gap-4">
          <div
            className={`flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-2xl ${
              danger ? "bg-red-100 text-red-600" : "bg-brand-100 text-brand-600"
            }`}
          >
            {danger ? <AlertTriangle className="h-5 w-5" /> : <Sparkles className="h-5 w-5" />}
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
            <p className="mt-1 text-sm leading-relaxed text-slate-600">{message}</p>
          </div>
        </div>
        <div className="mt-6 flex justify-end gap-2">
          <Button variant="secondary" onClick={onCancel} disabled={loading}>
            {cancelLabel}
          </Button>
          <Button variant={danger ? "danger" : "primary"} onClick={onConfirm} loading={loading}>
            {confirmLabel}
          </Button>
        </div>
      </div>
    </div>
  );
}
