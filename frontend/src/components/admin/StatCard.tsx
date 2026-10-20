interface StatCardProps {
  icon: React.ReactNode;
  iconBg: string;
  value: number | string;
  label: string;
}

/** Compact KPI tile used across the admin overview grid. */
export default function StatCard({ icon, iconBg, value, label }: StatCardProps) {
  return (
    <div className="card card-hover group p-5">
      <div className="flex items-center gap-3.5">
        <div
          className={`flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-xl transition-transform duration-300 group-hover:scale-110 ${iconBg}`}
        >
          {icon}
        </div>
        <div className="min-w-0">
          <p className="truncate text-2xl font-extrabold leading-none text-slate-900">{value}</p>
          <p className="mt-1 truncate text-xs font-medium text-slate-500">{label}</p>
        </div>
      </div>
    </div>
  );
}
