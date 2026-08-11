"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { Newspaper, LogOut, User, Settings, Home, Rss, Shield, Menu, X } from "lucide-react";
import { cn } from "@/lib/cn";

export default function Navbar() {
  const { user, isAuthenticated, isLoading, isAdmin, logout } = useAuth();
  const pathname = usePathname();
  const router = useRouter();
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleLogout = () => {
    setMobileOpen(false);
    logout();
    router.push("/login");
  };

  const links = [
    { href: "/", label: "Home", icon: <Home className="w-4 h-4" />, show: true },
    { href: "/news", label: "News", icon: <Rss className="w-4 h-4" />, show: isAuthenticated },
    { href: "/settings", label: "Settings", icon: <Settings className="w-4 h-4" />, show: isAuthenticated },
    { href: "/admin", label: "Admin", icon: <Shield className="w-4 h-4" />, show: isAuthenticated && isAdmin },
  ].filter((link) => link.show);

  const isActive = (href: string) => (href === "/" ? pathname === "/" : pathname.startsWith(href));

  return (
    <nav className="bg-white/80 backdrop-blur-md border-b border-gray-100 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-8">
            <Link href="/" className="flex items-center gap-2 group" onClick={() => setMobileOpen(false)}>
              <div className="w-8 h-8 bg-gradient-to-br from-brand-500 to-brand-700 rounded-lg flex items-center justify-center shadow-md shadow-brand-600/20 transition-transform group-hover:scale-105">
                <Newspaper className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-brand-600 to-brand-800 bg-clip-text text-transparent">
                AI News
              </span>
            </Link>
            <div className="hidden md:flex items-center gap-1">
              {links.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className={cn(
                    "relative flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors duration-200",
                    isActive(link.href)
                      ? "text-brand-700"
                      : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
                  )}
                >
                  {link.icon}
                  {link.label}
                  {isActive(link.href) && (
                    <span className="absolute inset-x-3 -bottom-[13px] h-0.5 bg-gradient-to-r from-brand-500 to-brand-700 rounded-full animate-fade-in" />
                  )}
                </Link>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-3">
            {isLoading ? (
              // Session is being checked — show a neutral placeholder instead of
              // flashing Login/Sign Up (or user info) before auth resolves.
              <>
                <div className="hidden sm:flex items-center gap-2" aria-hidden="true">
                  <span className="skeleton h-9 w-16 rounded-lg" />
                  <span className="skeleton h-9 w-20 rounded-lg" />
                </div>
                <span className="skeleton h-9 w-9 rounded-lg sm:hidden" aria-hidden="true" />
              </>
            ) : isAuthenticated ? (
              <>
                <div className="hidden sm:flex items-center gap-3">
                  <span className="flex items-center gap-2 text-sm text-gray-600">
                    <span className="w-7 h-7 rounded-full bg-gradient-to-br from-brand-500 to-brand-700 text-white text-xs font-semibold flex items-center justify-center">
                      {(user?.name || user?.email || "U").charAt(0).toUpperCase()}
                    </span>
                    {user?.name || user?.email}
                    {isAdmin && (
                      <span className="px-2 py-0.5 bg-brand-100 text-brand-700 rounded-full text-xs font-medium">
                        {user?.role}
                      </span>
                    )}
                  </span>
                  <button
                    onClick={handleLogout}
                    className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <LogOut className="w-4 h-4" />
                    <span className="hidden sm:block">Logout</span>
                  </button>
                </div>
                <button
                  className="md:hidden p-2 rounded-lg text-gray-600 hover:bg-gray-100 transition-colors"
                  onClick={() => setMobileOpen((open) => !open)}
                  aria-label={mobileOpen ? "Close menu" : "Open menu"}
                  aria-expanded={mobileOpen}
                >
                  {mobileOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
                </button>
              </>
            ) : (
              <>
                <div className="hidden sm:flex items-center gap-2">
                  <Link href="/login" className="btn-secondary text-sm">
                    Login
                  </Link>
                  <Link href="/register" className="btn-primary text-sm">
                    Sign Up
                  </Link>
                </div>
                <button
                  className="sm:hidden p-2 rounded-lg text-gray-600 hover:bg-gray-100 transition-colors"
                  onClick={() => setMobileOpen((open) => !open)}
                  aria-label={mobileOpen ? "Close menu" : "Open menu"}
                  aria-expanded={mobileOpen}
                >
                  {mobileOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
                </button>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="md:hidden border-t border-gray-100 bg-white/95 backdrop-blur-md animate-fade-in">
          <div className="px-4 py-3 space-y-1">
            {links.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setMobileOpen(false)}
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                  isActive(link.href)
                    ? "bg-brand-100 text-brand-700"
                    : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
                )}
              >
                {link.icon}
                {link.label}
              </Link>
            ))}
            <div className="pt-2 mt-2 border-t border-gray-100 space-y-1">
              {isLoading ? (
                <div className="flex gap-2 pt-1" aria-hidden="true">
                  <span className="skeleton h-9 flex-1 rounded-lg" />
                  <span className="skeleton h-9 flex-1 rounded-lg" />
                </div>
              ) : isAuthenticated ? (
                <>
                  <div className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600">
                    <User className="w-4 h-4" />
                    {user?.name || user?.email}
                  </div>
                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-600 hover:bg-red-50 hover:text-red-600 transition-colors"
                  >
                    <LogOut className="w-4 h-4" />
                    Logout
                  </button>
                </>
              ) : (
                <div className="flex gap-2 pt-1">
                  <Link href="/login" onClick={() => setMobileOpen(false)} className="btn-secondary flex-1 text-center text-sm">
                    Login
                  </Link>
                  <Link href="/register" onClick={() => setMobileOpen(false)} className="btn-primary flex-1 text-center text-sm">
                    Sign Up
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </nav>
  );
}
