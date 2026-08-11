"use client";

import { Users, Newspaper, Rss, Activity, TrendingUp, Clock, Database, Shield } from "lucide-react";
import { AdminStatsOut } from "@/lib/api";
import StatCard from "./StatCard";

interface OverviewTabProps {
  stats: AdminStatsOut;
}

export default function OverviewTab({ stats }: OverviewTabProps) {
  return (
    <div className="space-y-6">
      {/* Primary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          icon={<Users className="w-5 h-5 text-brand-600" />}
          iconBg="bg-brand-100"
          value={stats.total_users}
          label="Total Users"
        />
        <StatCard
          icon={<Activity className="w-5 h-5 text-green-600" />}
          iconBg="bg-green-100"
          value={stats.active_users}
          label="Active Users"
        />
        <StatCard
          icon={<Newspaper className="w-5 h-5 text-blue-600" />}
          iconBg="bg-blue-100"
          value={stats.total_news_items}
          label="News Items"
        />
        <StatCard
          icon={<Rss className="w-5 h-5 text-purple-600" />}
          iconBg="bg-purple-100"
          value={stats.active_sources}
          label="Active Sources"
        />
      </div>

      {/* Secondary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          icon={<TrendingUp className="w-5 h-5 text-indigo-600" />}
          iconBg="bg-indigo-100"
          value={stats.news_today}
          label="News Today"
        />
        <StatCard
          icon={<Clock className="w-5 h-5 text-teal-600" />}
          iconBg="bg-teal-100"
          value={stats.news_this_week}
          label="News This Week"
        />
        <StatCard
          icon={<Database className="w-5 h-5 text-amber-600" />}
          iconBg="bg-amber-100"
          value={stats.total_fetches}
          label="Total Fetches"
        />
        <StatCard
          icon={<Shield className="w-5 h-5 text-rose-600" />}
          iconBg="bg-rose-100"
          value={stats.total_admins}
          label="Admins"
        />
      </div>

      {/* System Health */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">System Health</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <p className="text-3xl font-bold text-green-600">{stats.analyzed_news_items}</p>
            <p className="text-sm text-gray-600">Analyzed</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-yellow-600">{stats.pending_news_items}</p>
            <p className="text-sm text-gray-600">Pending</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-red-600">{stats.error_sources}</p>
            <p className="text-sm text-gray-600">Error Sources</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-gray-600">{stats.suspended_users}</p>
            <p className="text-sm text-gray-600">Suspended</p>
          </div>
        </div>
      </div>
    </div>
  );
}
