
import { Users, Newspaper, Rss, Activity, TrendingUp, Clock, Database, Shield } from "lucide-react";
import { AdminStatsOut } from "@/shared/api";
import StatCard from "./StatCard";

interface OverviewTabProps {
  stats: AdminStatsOut;
}

/** Health meters shown in the "How things are going" panel. */
function Meter({
  value,
  label,
  tone,
}: {
  value: number | string;
  label: string;
  tone: "good" | "warn" | "bad" | "neutral";
}) {
  const toneText = {
    good: "text-emerald-600",
    warn: "text-amber-600",
    bad: "text-red-600",
    neutral: "text-slate-700",
  }[tone];

  const toneBg = {
    good: "from-emerald-400 to-emerald-500",
    warn: "from-amber-400 to-amber-500",
    bad: "from-red-400 to-red-500",
    neutral: "from-brand-400 to-brand-500",
  }[tone];

  return (
    <div className="rounded-xl border border-slate-100 bg-slate-50/70 p-4 text-center transition-colors hover:bg-slate-50">
      <div
        className={`mx-auto mb-2 h-1.5 w-10 rounded-full bg-gradient-to-r ${toneBg}`}
        aria-hidden="true"
      />
      <p className={`text-3xl font-extrabold ${toneText}`}>{value}</p>
      <p className="mt-1 text-sm text-slate-500">{label}</p>
    </div>
  );
}

export default function OverviewTab({ stats }: OverviewTabProps) {
  return (
    <div className="space-y-6">
      {/* Primary Stats */}
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard
          icon={<Users className="h-5 w-5 text-brand-600" />}
          iconBg="bg-brand-100"
          value={stats.total_users}
          label="Readers"
        />
        <StatCard
          icon={<Activity className="h-5 w-5 text-emerald-600" />}
          iconBg="bg-emerald-100"
          value={stats.active_users}
          label="Active this week"
        />
        <StatCard
          icon={<Newspaper className="h-5 w-5 text-sky-600" />}
          iconBg="bg-sky-100"
          value={stats.total_news_items}
          label="Stories collected"
        />
        <StatCard
          icon={<Rss className="h-5 w-5 text-accent-600" />}
          iconBg="bg-accent-100"
          value={stats.active_sources}
          label="Live sources"
        />
      </div>

      {/* Secondary Stats */}
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard
          icon={<TrendingUp className="h-5 w-5 text-brand-600" />}
          iconBg="bg-brand-100"
          value={stats.news_today}
          label="Added today"
        />
        <StatCard
          icon={<Clock className="h-5 w-5 text-teal-600" />}
          iconBg="bg-teal-100"
          value={stats.news_this_week}
          label="Added this week"
        />
        <StatCard
          icon={<Database className="h-5 w-5 text-amber-600" />}
          iconBg="bg-amber-100"
          value={stats.total_fetches}
          label="Fetches"
        />
        <StatCard
          icon={<Shield className="h-5 w-5 text-rose-600" />}
          iconBg="bg-rose-100"
          value={stats.total_admins}
          label="Admins"
        />
      </div>

      {/* System Health */}
      <div className="card">
        <div className="mb-5 flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-slate-900">How things are going</h3>
            <p className="text-sm text-slate-500">A quick pulse on your pipeline right now.</p>
          </div>
          <span className="badge-green">Live</span>
        </div>
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          <Meter value={stats.analyzed_news_items} label="Analyzed" tone="good" />
          <Meter value={stats.pending_news_items} label="Waiting" tone="warn" />
          <Meter value={stats.error_sources} label="Sources having trouble" tone="bad" />
          <Meter value={stats.suspended_users} label="Suspended" tone="neutral" />
        </div>
      </div>
    </div>
  );
}
