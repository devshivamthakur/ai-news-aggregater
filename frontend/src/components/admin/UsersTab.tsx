"use client";

import { AdminUser } from "@/lib/api";
import { Users } from "lucide-react";
import { Skeleton } from "@/components/ui/Skeleton";
import EmptyState from "@/components/ui/EmptyState";

interface UsersTabProps {
  users: AdminUser[];
  isLoading: boolean;
}

function TableRowSkeleton() {
  return (
    <tr className="border-b border-gray-100">
      {Array.from({ length: 8 }).map((_, i) => (
        <td key={i} className="py-3 px-4">
          <Skeleton className="h-4 w-16" />
        </td>
      ))}
    </tr>
  );
}

export default function UsersTab({ users, isLoading }: UsersTabProps) {
  return (
    <div className="card">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Registered Users</h2>
      {isLoading ? (
        <div className="overflow-x-auto" aria-busy="true" aria-label="Loading users">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                {["ID", "Email", "Name", "Role", "Status", "Digest", "Last Login", "Joined"].map((h) => (
                  <th key={h} className="text-left py-3 px-4 font-medium text-gray-600">
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
        <EmptyState
          icon={<Users className="w-7 h-7" />}
          title="No users registered yet"
          description="Users will appear here once they sign up."
        />
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 font-medium text-gray-600">ID</th>
                <th className="text-left py-3 px-4 font-medium text-gray-600">Email</th>
                <th className="text-left py-3 px-4 font-medium text-gray-600">Name</th>
                <th className="text-left py-3 px-4 font-medium text-gray-600">Role</th>
                <th className="text-left py-3 px-4 font-medium text-gray-600">Status</th>
                <th className="text-left py-3 px-4 font-medium text-gray-600">Digest</th>
                <th className="text-left py-3 px-4 font-medium text-gray-600">Last Login</th>
                <th className="text-left py-3 px-4 font-medium text-gray-600">Joined</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                  <td className="py-3 px-4 text-gray-900">{u.id}</td>
                  <td className="py-3 px-4 text-gray-900">{u.email}</td>
                  <td className="py-3 px-4 text-gray-600">{u.name || "-"}</td>
                  <td className="py-3 px-4">
                    <span className={`badge ${
                      u.role === "super_admin" ? "badge-brand" :
                      u.role === "admin" ? "badge-green" : "badge-gray"
                    }`}>
                      {u.role}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <span className={`badge ${
                      u.status === "active" ? "badge-green" :
                      u.status === "suspended" ? "badge-gray" : "badge-gray"
                    }`}>
                      {u.status}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <span className={`badge ${u.digest_subscribed ? "badge-brand" : "badge-gray"}`}>
                      {u.digest_subscribed ? "Subscribed" : "Unsubscribed"}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-gray-500 text-xs">
                    {u.last_login_at ? new Date(u.last_login_at).toLocaleDateString() : "-"}
                  </td>
                  <td className="py-3 px-4 text-gray-500 text-xs">
                    {u.created_at ? new Date(u.created_at).toLocaleDateString() : "-"}
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
