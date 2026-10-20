
import { BarChart3, Users, Rss, Tag, Zap, Trash2 } from "lucide-react";
import { cn } from "@/shared/cn";

export type AdminTab = "overview" | "users" | "sources" | "categories" | "jobs" | "maintenance";

interface AdminTabsProps {
  activeTab: AdminTab;
  onChange: (tab: AdminTab) => void;
  isAdmin: boolean;
}

const TABS: { id: AdminTab; label: string; icon: React.ReactNode; adminOnly?: boolean }[] = [
  { id: "overview", label: "Overview", icon: <BarChart3 className="h-4 w-4" /> },
  { id: "users", label: "Readers", icon: <Users className="h-4 w-4" /> },
  { id: "sources", label: "Sources", icon: <Rss className="h-4 w-4" />, adminOnly: true },
  { id: "categories", label: "Topics", icon: <Tag className="h-4 w-4" /> },
  { id: "jobs", label: "Jobs", icon: <Zap className="h-4 w-4" /> },
  { id: "maintenance", label: "Maintenance", icon: <Trash2 className="h-4 w-4" />, adminOnly: true },
];

export default function AdminTabs({ activeTab, onChange, isAdmin }: AdminTabsProps) {
  return (
    <div className="flex gap-1 overflow-x-auto rounded-2xl border border-slate-200 bg-white p-1.5 shadow-sm">
      {TABS.filter((tab) => !tab.adminOnly || isAdmin).map((tab) => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          className={cn(
            "flex flex-1 items-center justify-center gap-2 whitespace-nowrap rounded-xl px-4 py-2.5 text-sm font-medium transition-all duration-200",
            activeTab === tab.id
              ? "bg-gradient-to-r from-brand-600 to-brand-700 text-white shadow-soft"
              : "text-slate-600 hover:bg-slate-100"
          )}
        >
          {tab.icon}
          {tab.label}
        </button>
      ))}
    </div>
  );
}
