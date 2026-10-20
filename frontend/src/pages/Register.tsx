
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { ApiError } from "@/shared/api";
import { UserPlus, Eye, EyeOff, CheckCircle2, XCircle, ArrowRight } from "lucide-react";
import Button from "@/components/ui/Button";
import AuthLayout, { AuthCardHeader, AuthError } from "@/components/AuthLayout";
import { cn } from "@/shared/cn";

export default function RegisterPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const passwordsMatch = password === confirmPassword;
  const passwordValid = password.length >= 8;
  const canSubmit = passwordValid && passwordsMatch;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!passwordsMatch) {
      setError("Passwords do not match");
      return;
    }

    if (!passwordValid) {
      setError("Password must be at least 8 characters");
      return;
    }

    setIsLoading(true);

    try {
      await register(email, password, name);
      navigate("/news");
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.detail || "Registration failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthLayout title="Create account">
      <AuthCardHeader
        icon={<UserPlus className="h-7 w-7" />}
        title="Create your account"
        subtitle="Free forever — set up in under two minutes."
      />

      <AuthError message={error} />

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="name" className="mb-1.5 block text-sm font-medium text-slate-700">
            Full name
          </label>
          <input
            id="name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="input"
            placeholder="Jane Doe"
            autoComplete="name"
            required
          />
        </div>

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
              className={cn(
                "input pr-11",
                password.length > 0 && !passwordValid && "border-red-300 focus:ring-red-400"
              )}
              placeholder="At least 8 characters"
              autoComplete="new-password"
              required
              minLength={8}
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
          {password.length > 0 && (
            <p
              className={cn(
                "mt-1.5 flex items-center gap-1 text-xs",
                passwordValid ? "text-emerald-600" : "text-amber-600"
              )}
            >
              {passwordValid ? <CheckCircle2 className="h-3 w-3" /> : <XCircle className="h-3 w-3" />}
              {passwordValid ? "Looks good" : "Use at least 8 characters"}
            </p>
          )}
        </div>

        <div>
          <label htmlFor="confirmPassword" className="mb-1.5 block text-sm font-medium text-slate-700">
            Confirm password
          </label>
          <input
            id="confirmPassword"
            type={showPassword ? "text" : "password"}
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className={cn(
              "input",
              confirmPassword.length > 0 && !passwordsMatch && "border-red-300 focus:ring-red-400"
            )}
            placeholder="Repeat your password"
            autoComplete="new-password"
            required
          />
          {confirmPassword.length > 0 && !passwordsMatch && (
            <p className="mt-1.5 flex items-center gap-1 text-xs text-red-600">
              <XCircle className="h-3 w-3" />
              Passwords don&apos;t match
            </p>
          )}
        </div>

        <Button type="submit" className="w-full" loading={isLoading} disabled={!canSubmit}>
          {isLoading ? "Creating account…" : "Create account"}
          {!isLoading && <ArrowRight className="h-4 w-4" />}
        </Button>
      </form>

      <p className="mt-6 text-center text-sm text-slate-500">
        Already have an account?{" "}
        <Link to="/login" className="font-semibold text-brand-600 transition-colors hover:text-brand-700">
          Sign in
        </Link>
      </p>
    </AuthLayout>
  );
}
