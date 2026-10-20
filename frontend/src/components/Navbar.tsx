
import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { Newspaper, LogOut, User, Settings, Home, Rss, Shield, Menu, X, Sparkles } from "lucide-react";
import { cn } from "@/shared/cn";

export default function Navbar() {
  const { user, isAuthenticated, isLoading, isAdmin, logout } = useAuth();
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleLogout = () => {
    setMobileOpen(false);
    logout();
    navigate("/login");
  };

  const links = [
    { href: "/", label: "Home", icon: <Home className="h-4 w-4" />, show: true },
    { href: "/news", label: "My News", icon: <Rss className="h-4 w-4" />, show: isAuthenticated },
    { href: "/settings", label: "Settings", icon: <Settings className="h-4 w-4" />, show: isAuthenticated },
    { href: "/admin", label: "Admin", icon: <Shield className="h-4 w-4" />, show: isAuthenticated && isAdmin },
  ].filter((link) => link.show);

  const isActive = (href: string) => (href === "/" ? pathname === "/" : pathname.startsWith(href));

  return (
    <nav className="sticky top-0 z-50 border-b border-slate-200/70 bg-white/80 backdrop-blur-xl">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center gap-8">
            <Link
              to="/"
              className="group flex items-center gap-2"
              onClick={() => setMobileOpen(false)}
            >
              <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500 to-accent-500 text-white shadow-glow transition-transform duration-300 group-hover:scale-105 group-hover:rotate-3">
                <Newspaper className="h-5 w-5" />
              </span>
              <span className="text-lg font-bold tracking-tight text-slate-900">
                AI Pulse
              </span>
            </Link>

            <div className="hidden items-center gap-1 md:flex">
              {links.map((link) => (
                <Link
                  key={link.href}
                  to={link.href}
                  className={cn(
                    "relative flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors duration-200",
                    isActive(link.href)
                      ? "text-brand-700"
                      : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                  )}
                >
                  {link.icon}
                  {link.label}
                  {isActive(link.href) && (
                    <span className="absolute inset-x-3 -bottom-[13px] h-0.5 rounded-full bg-gradient-to-r from-brand-500 to-accent-500 animate-fade-in" />
                  )}
                </Link>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-3">
            {isLoading ? (
              <>
                <div className="hidden items-center gap-2 sm:flex" aria-hidden="true">
                  <span className="skeleton h-9 w-16 rounded-lg" />
                  <span className="skeleton h-9 w-20 rounded-lg" />
                </div>
                <span className="skeleton h-9 w-9 rounded-lg sm:hidden" aria-hidden="true" />
              </>
            ) : isAuthenticated ? (
              <>
                <div className="hidden items-center gap-3 sm:flex">
                  <span className="flex items-center gap-2 text-sm text-slate-600">
                    <span className="flex h-7 w-7 items-center justify-center rounded-full bg-gradient-to-br from-brand-500 to-accent-500 text-xs font-semibold text-white">
                      {(user?.name || user?.email || "U").charAt(0).toUpperCase()}
                    </span>
                    {user?.name || user?.email}
                    {isAdmin && (
                      <span className="badge-brand">{user?.role}</span>
                    )}
                  </span>
                  <button
                    onClick={handleLogout}
                    className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-slate-600 transition-colors hover:bg-red-50 hover:text-red-600"
                  >
                    <LogOut className="h-4 w-4" />
                    <span className="hidden sm:block">Logout</span>
                  </button>
                </div>
                <button
                  className="rounded-lg p-2 text-slate-600 transition-colors hover:bg-slate-100 md:hidden"
                  onClick={() => setMobileOpen((open) => !open)}
                  aria-label={mobileOpen ? "Close menu" : "Open menu"}
                  aria-expanded={mobileOpen}
                >
                  {mobileOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
                </button>
              </>
            ) : (
              <>
                <div className="hidden items-center gap-2 sm:flex">
                  <Link to="/login" className="btn-secondary text-sm">
                    Sign in
                  </Link>
                  <Link to="/register" className="btn-primary text-sm">
                    <Sparkles className="h-4 w-4" /> Start free
                  </Link>
                </div>
                <button
                  className="rounded-lg p-2 text-slate-600 transition-colors hover:bg-slate-100 sm:hidden"
                  onClick={() => setMobileOpen((open) => !open)}
                  aria-label={mobileOpen ? "Close menu" : "Open menu"}
                  aria-expanded={mobileOpen}
                >
                  {mobileOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
                </button>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="animate-fade-in border-t border-slate-200 bg-white/95 backdrop-blur-xl md:hidden">
          <div className="space-y-1 px-4 py-3">
            {links.map((link) => (
              <Link
                key={link.href}
                to={link.href}
                onClick={() => setMobileOpen(false)}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                  isActive(link.href)
                    ? "bg-brand-50 text-brand-700"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                )}
              >
                {link.icon}
                {link.label}
              </Link>
            ))}
            <div className="mt-2 space-y-1 border-t border-slate-200 pt-2">
              {isLoading ? (
                <div className="flex gap-2 pt-1" aria-hidden="true">
                  <span className="skeleton h-9 flex-1 rounded-lg" />
                  <span className="skeleton h-9 flex-1 rounded-lg" />
                </div>
              ) : isAuthenticated ? (
                <>
                  <div className="flex items-center gap-2 px-3 py-2 text-sm text-slate-600">
                    <User className="h-4 w-4" />
                    {user?.name || user?.email}
                  </div>
                  <button
                    onClick={handleLogout}
                    className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-slate-600 transition-colors hover:bg-red-50 hover:text-red-600"
                  >
                    <LogOut className="h-4 w-4" />
                    Logout
                  </button>
                </>
              ) : (
                <div className="flex gap-2 pt-1">
                  <Link
                    to="/login"
                    onClick={() => setMobileOpen(false)}
                    className="btn-secondary flex-1 text-center text-sm"
                  >
                    Sign in
                  </Link>
                  <Link
                    to="/register"
                    onClick={() => setMobileOpen(false)}
                    className="btn-primary flex-1 text-center text-sm"
                  >
                    Start free
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
