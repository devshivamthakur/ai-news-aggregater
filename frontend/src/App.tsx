import { Suspense, useEffect, type ReactNode } from "react";
import { BrowserRouter, Routes, Route, Navigate, useLocation } from "react-router-dom";
import { AuthProvider } from "@/context/AuthContext";
import { ToastProvider } from "@/components/ui/Toast";
import Navbar from "@/components/Navbar";
import ErrorBoundary from "@/components/ErrorBoundary";
import SessionExpiryWatcher from "@/components/SessionExpiryWatcher";
import PageLoader from "@/components/ui/PageLoader";
import {
  NewsPageSkeleton,
  SettingsPageSkeleton,
  AdminPageSkeleton,
} from "@/components/PageSkeletons";
import lazyWithRetry from "@/shared/lazyWithRetry";

// Every route is code-split so the initial download stays small.
const Home = lazyWithRetry(() => import("@/pages/Home"));
const Login = lazyWithRetry(() => import("@/pages/Login"));
const Register = lazyWithRetry(() => import("@/pages/Register"));
const News = lazyWithRetry(() => import("@/pages/News"));
const Settings = lazyWithRetry(() => import("@/pages/Settings"));
const Admin = lazyWithRetry(() => import("@/pages/Admin"));

/** Scrolls to the top whenever the route changes (SPA equivalent of a page load). */
function ScrollToTop() {
  const { pathname } = useLocation();
  useEffect(() => {
    window.scrollTo({ top: 0 });
  }, [pathname]);
  return null;
}

/** Wraps a lazy route so a slow chunk shows a relevant skeleton, not a spinner. */
function RouteView({ children, fallback }: { children: ReactNode; fallback: ReactNode }) {
  return (
    <ErrorBoundary>
      <Suspense fallback={fallback}>{children}</Suspense>
    </ErrorBoundary>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ToastProvider>
          <ScrollToTop />
          <SessionExpiryWatcher />
          <div className="flex min-h-screen flex-col">
            <Navbar />
            <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-8 sm:px-6 lg:px-8">
              <Routes>
                <Route
                  path="/"
                  element={
                    <RouteView fallback={<PageLoader label="Loading" />}>
                      <Home />
                    </RouteView>
                  }
                />
                <Route
                  path="/login"
                  element={
                    <RouteView fallback={<PageLoader label="Opening sign in" />}>
                      <Login />
                    </RouteView>
                  }
                />
                <Route
                  path="/register"
                  element={
                    <RouteView fallback={<PageLoader label="Opening sign up" />}>
                      <Register />
                    </RouteView>
                  }
                />
                <Route
                  path="/news"
                  element={
                    <RouteView fallback={<NewsPageSkeleton />}>
                      <News />
                    </RouteView>
                  }
                />
                <Route
                  path="/settings"
                  element={
                    <RouteView fallback={<SettingsPageSkeleton />}>
                      <Settings />
                    </RouteView>
                  }
                />
                <Route
                  path="/admin"
                  element={
                    <RouteView fallback={<AdminPageSkeleton />}>
                      <Admin />
                    </RouteView>
                  }
                />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </main>
          </div>
        </ToastProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}
