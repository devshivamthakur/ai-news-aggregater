
import { AdminUser } from "@/shared/api";
import { Users, Mail } from "lucide-react";
import { Skeleton } from "@/components/ui/Skeleton";
import EmptyState from "@/components/ui/EmptyState";
import { cn } from "@/shared/cn";

interface UsersTabProps {
  users: AdminUser[];
  isLoading: boolean;
}

function TableRowSkeleton() {
  return (
    <tr className="border-b border-slate-100">
      {Array.from({ length: 8 }).map((_, i) => (
        <td key={i} className="px-4 py-3.5">
          <Skeleton className="h-4 w-16" />
        </td>
      ))}
    </tr>
  );
}

function roleBadge(role: string) {
  if (role === "super_admin") return "bg-brand-50 text-brand-700 ring-brand-100";
  if (role === "admin") return "bg-emerald-50 text-emerald-700 ring-emerald-100";
  return "bg-slate-100 text-slate-600 ring-slate-200";
}

const HEADERS = ["ID", "Email", "Name", "Role", "Status", "Brief", "Last seen", "Joined"];

export default function UsersTab({ users, isLoading }: UsersTabProps) {
  return (
    <div className="card p-0">
      <div className="flex items-center gap-2.5 border-b border-slate-100 px-6 py-5">
        <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-50 text-brand-600">
          <Users className="h-4 w-4" />
        </span>
        <div>
          <h2 className="text-lg font-semibold text-slate-900">Readers</h2>
          <p className="text-xs text-slate-400">
            {users.length > 0 ? `${users.length} registered` : "No one here just yet"}
          </p>
        </div>
      </div>

      {isLoading ? (
        <div className="overflow-x-auto" aria-busy="true" aria-label="Loading readers">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200">
                {HEADERS.map((h) => (
                  <th key={h} className="px-4 py-3 text-left font-medium text-slate-500">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {Array.from({ length: 5 }).map((_, i) => (
                <TableRowSkeleton key={i} />
              ))}
            </tbody>
          </table>
        </div>
      ) : users.length === 0 ? (
        <div className="p-6">
          <EmptyState
            icon={<Mail className="h-7 w-7" />}
            title="No readers yet"
            description="People will show up here as soon as they create an account."
          />
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50/60">
                {HEADERS.map((h) => (
                  <th key={h} className="px-4 py-3 text-left font-medium text-slate-500">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr
                  key={u.id}
                  className="border-b border-slate-100 transition-colors last:border-0 hover:bg-slate-50"
                >
                  <td className="px-4 py-3.5 text-slate-500 tabular-nums">{u.id}</td>
                  <td className="px-4 py-3.5 font-medium text-slate-900">{u.email}</td>
                  <td className="px-4 py-3.5 text-slate-600">{u.name || "—"}</td>
                  <td className="px-4 py-3.5">
                    <span className={cn("badge ring-1 ring-inset", roleBadge(u.role))}>{u.role}</span>
                  </td>
                  <td className="px-4 py-3.5">
                    <span
                      className={cn(
                        "badge ring-1 ring-inset",
                        u.status === "active"
                          ? "bg-emerald-50 text-emerald-700 ring-emerald-100"
                          : "bg-slate-100 text-slate-600 ring-slate-200"
                      )}
                    >
                      {u.status}
                    </span>
                  </td>
                  <td className="px-4 py-3.5">
                    <span
                      className={cn(
                        "badge ring-1 ring-inset",
                        u.digest_subscribed
                          ? "bg-brand-50 text-brand-700 ring-brand-100"
                          : "bg-slate-100 text-slate-600 ring-slate-200"
                      )}
                    >
                      {u.digest_subscribed ? "On" : "Off"}
                    </span>
                  </td>
                  <td className="px-4 py-3.5 text-xs text-slate-400">
                    {u.last_login_at ? new Date(u.last_login_at).toLocaleDateString() : "—"}
                  </td>
                  <td className="px-4 py-3.5 text-xs text-slate-400">
                    {u.created_at ? new Date(u.created_at).toLocaleDateString() : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
