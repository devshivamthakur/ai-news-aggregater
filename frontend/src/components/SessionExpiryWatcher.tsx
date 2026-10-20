import { useEffect, useRef } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { SESSION_EXPIRED_EVENT } from "@/shared/api";
import { useAuth } from "@/context/AuthContext";
import { useToast } from "@/components/ui/Toast";

const AUTH_PATHS = ["/login", "/register"];

/**
 * Reacts to the API client's `SESSION_EXPIRED_EVENT` (a refresh that failed
 * while you were using the app).
 *
 * It used to be handled with `window.location.href = "/login"`, which hard
 * reloaded the SPA — the user just saw the page flash and reload with no
 * explanation, and any error on screen was lost. This keeps everything
 * in-app: drop the dead session, move to sign-in, say why.
 */
export default function SessionExpiryWatcher() {
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const { refreshUser } = useAuth();
  const { error } = useToast();
  const lastNotice = useRef(0);

  useEffect(() => {
    const handleExpired = () => {
      // Syncs AuthContext with the cleared tokens (no token → user becomes null).
      void refreshUser();

      if (!AUTH_PATHS.includes(pathname)) {
        navigate("/login");
      }

      // Several parallel calls can fail at once — announce it only once.
      const now = Date.now();
      if (now - lastNotice.current > 3000) {
        lastNotice.current = now;
        error("Your session expired — please sign in again.");
      }
    };

    window.addEventListener(SESSION_EXPIRED_EVENT, handleExpired);
    return () => window.removeEventListener(SESSION_EXPIRED_EVENT, handleExpired);
  }, [pathname, navigate, refreshUser, error]);

  return null;
}
