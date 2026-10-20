import { Link } from "react-router-dom";
import { ArrowLeft, AlertCircle, CheckCircle2 } from "lucide-react";

interface AuthLayoutProps {
  children: React.ReactNode;
  /** Short context label shown above the headline (e.g. "Sign in"). */
  title: string;
}

const PROMISES = [
  { text: "A short, friendly brief — never a wall of links" },
  { text: "Catch up in about five minutes" },
  { text: "Private by default, no ads, no spam" },
];

/**
 * Split-screen wrapper shared by the sign-in and sign-up pages.
 *
 * The page shell (Navbar + <main>) already renders the brand, so this layout
 * deliberately avoids repeating the logo and instead leads with a benefit.
 */
export default function AuthLayout({ children, title }: AuthLayoutProps) {
  return (
    <div className="relative isolate overflow-hidden" aria-label={title}>
      {/* Soft ambient wash — faded to transparent on every edge so the
          clipped blur reads as a vignette, never a hard-edged box. */}
      <div className="mask-fade-x pointer-events-none absolute inset-0 -z-10 overflow-hidden">
        <div className="mask-fade-y relative h-full w-full">
          <div className="animate-blob absolute -left-64 -top-56 h-[44rem] w-[44rem] rounded-full bg-brand-300/30 blur-[120px]" />
          <div className="animate-blob absolute -bottom-72 -right-56 h-[40rem] w-[40rem] rounded-full bg-accent-300/25 blur-[120px] [animation-delay:4s]" />
          <div className="dot-grid absolute inset-0 opacity-40 [mask-image:radial-gradient(ellipse_at_center,black,transparent_72%)]" />
        </div>
      </div>

      <div className="grid items-center gap-12 py-12 lg:grid-cols-[1.05fr_1fr] lg:gap-16 lg:py-20">
        {/* Desktop pitch panel */}
        <div className="hidden max-w-xl lg:block">
          <Link
            to="/"
            className="inline-flex items-center gap-2 text-sm font-medium text-slate-500 transition-colors hover:text-brand-600"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to home
          </Link>

          <h1 className="mt-6 text-4xl font-extrabold leading-[1.1] tracking-tight text-slate-900 sm:text-5xl">
            Your news,
            <br />
            <span className="gradient-text-animated">minus the noise.</span>
          </h1>

          <p className="mt-5 max-w-md text-lg leading-relaxed text-slate-600">
            Tell us what you care about and we&apos;ll send a calm, skimmable brief straight to your
            inbox.
          </p>

          <ul className="mt-8 space-y-3.5">
            {PROMISES.map((item) => (
              <li key={item.text} className="flex items-center gap-3">
                <span className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-emerald-100 text-emerald-600">
                  <CheckCircle2 className="h-3.5 w-3.5" />
                </span>
                <span className="text-slate-700">{item.text}</span>
              </li>
            ))}
          </ul>

          <div className="mt-10 flex items-center gap-3 rounded-2xl border border-white/60 bg-white/70 p-4 shadow-soft backdrop-blur-xl">
            <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-brand-500 to-accent-500 text-xs font-bold text-white">
              SR
            </div>
            <div>
              <p className="text-sm text-slate-600">
                &ldquo;I finally unsubscribed from four newsletters. This does all of it.&rdquo;
              </p>
              <p className="text-xs text-slate-400">Sofia R., Designer</p>
            </div>
          </div>
        </div>

        {/* Form card — centred alone on small screens */}
        <div className="card card-hover w-full max-w-md justify-self-center p-7 sm:p-8 lg:justify-self-end">
          {children}
        </div>
      </div>
    </div>
  );
}

export function AuthCardHeader({
  icon,
  title,
  subtitle,
}: {
  icon: React.ReactNode;
  title: string;
  subtitle: string;
}) {
  return (
    <div className="mb-7 text-center">
      <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-brand-500 to-accent-500 text-white shadow-glow">
        {icon}
      </div>
      <h2 className="text-2xl font-bold tracking-tight text-slate-900">{title}</h2>
      <p className="mt-1.5 text-sm text-slate-500">{subtitle}</p>
    </div>
  );
}

export function AuthError({ message }: { message: string }) {
  if (!message) return null;
  return (
    <div
      role="alert"
      className="animate-fade-in mb-4 flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 px-3 py-2.5 text-sm text-red-700"
    >
      <AlertCircle className="h-4 w-4 flex-shrink-0" />
      {message}
    </div>
  );
}
