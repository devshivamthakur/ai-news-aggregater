interface EmptyStateProps {
  icon: React.ReactNode;
  title: string;
  description?: string;
  action?: React.ReactNode;
}

/** Consistent empty-state placeholder used across pages. */
export default function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="card animate-fade-in py-14 text-center">
      <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-brand-50 to-accent-50 text-brand-500 ring-1 ring-brand-100">
        {icon}
      </div>
      <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
      {description && <p className="mx-auto mt-1.5 max-w-sm text-sm text-slate-500">{description}</p>}
      {action && <div className="mt-5 flex justify-center">{action}</div>}
    </div>
  );
}
