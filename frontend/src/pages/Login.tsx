
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { ApiError } from "@/shared/api";
import { LogIn, Eye, EyeOff, ArrowRight } from "lucide-react";
import Button from "@/components/ui/Button";
import AuthLayout, { AuthCardHeader, AuthError } from "@/components/AuthLayout";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      await login(email, password);
      navigate("/news");
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.detail || "Login failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthLayout title="Sign in">
      <AuthCardHeader
        icon={<LogIn className="h-7 w-7" />}
        title="Welcome back"
        subtitle="Sign in to pick up where you left off."
      />

      <AuthError message={error} />

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="email" className="mb-1.5 block text-sm font-medium text-slate-700">
            Email
          </label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="input"
            placeholder="you@example.com"
            autoComplete="email"
            required
          />
        </div>

        <div>
          <label htmlFor="password" className="mb-1.5 block text-sm font-medium text-slate-700">
            Password
          </label>
          <div className="relative">
            <input
              id="password"
              type={showPassword ? "text" : "password"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input pr-11"
              placeholder="Enter your password"
              autoComplete="current-password"
              required
            />
            <button
              type="button"
              onClick={() => setShowPassword((show) => !show)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 transition-colors hover:text-slate-600"
              aria-label={showPassword ? "Hide password" : "Show password"}
            >
              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
        </div>

        <Button type="submit" className="w-full" loading={isLoading}>
          {isLoading ? "Signing in…" : "Sign in"}
          {!isLoading && <ArrowRight className="h-4 w-4" />}
        </Button>
      </form>

      <p className="mt-6 text-center text-sm text-slate-500">
        New to AI Pulse?{" "}
        <Link to="/register" className="font-semibold text-brand-600 transition-colors hover:text-brand-700">
          Create an account
        </Link>
      </p>
    </AuthLayout>
  );
}
