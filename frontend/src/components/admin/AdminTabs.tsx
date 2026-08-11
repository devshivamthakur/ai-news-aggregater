"use client";

import { BarChart3, Users, Rss, Tag, Zap } from "lucide-react";

export type AdminTab = "overview" | "users" | "sources" | "categories" | "jobs";

interface AdminTabsProps {
  activeTab: AdminTab;
  onChange: (tab: AdminTab) => void;
  isAdmin: boolean;
}

const TABS: { id: AdminTab; label: string; icon: React.ReactNode; adminOnly?: boolean }[] = [
  { id: "overview", label: "Overview", icon: <BarChart3 className="w-4 h-4" /> },
  { id: "users", label: "Users", icon: <Users className="w-4 h-4" /> },
  { id: "sources", label: "Sources", icon: <Rss className="w-4 h-4" />, adminOnly: true },
  { id: "categories", label: "Categories", icon: <Tag className="w-4 h-4" /> },
  { id: "jobs", label: "Jobs", icon: <Zap className="w-4 h-4" /> },
];

export default function AdminTabs({ activeTab, onChange, isAdmin }: AdminTabsProps) {
  return (
    <div className="flex gap-2 border-b border-gray-200 pb-2">
      {TABS.filter((tab) => !tab.adminOnly || isAdmin).map((tab) => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            activeTab === tab.id
              ? "bg-brand-100 text-brand-700"
              : "text-gray-600 hover:bg-gray-100"
          }`}
        >
          {tab.icon}
          {tab.label}
        </button>
      ))}
    </div>
  );
}
