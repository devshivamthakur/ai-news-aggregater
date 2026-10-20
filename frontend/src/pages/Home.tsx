
import { useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import Reveal from "@/components/Reveal";
import CountUp from "@/components/CountUp";
import {
  ArrowRight,
  ArrowUpRight,
  Bell,
  Brain,
  CalendarClock,
  CheckCircle2,
  ChevronDown,
  Clock,
  Globe,
  Heart,
  Inbox,
  Layers,
  Mail,
  Newspaper,
  PlayCircle,
  Quote,
  Rss,
  Shield,
  Sparkles,
  Star,
  TrendingUp,
  Users,
  Zap,
} from "lucide-react";
import { cn } from "@/shared/cn";

/* ------------------------------------------------------------------ */
/* Content                                                             */
/* ------------------------------------------------------------------ */

const SOURCES = [
  "TechCrunch",
  "The Verge",
  "Reuters",
  "BBC News",
  "Ars Technica",
  "Wired",
  "MIT News",
  "NASA",
  "Bloomberg",
  "The Atlantic",
  "Hacker News",
  "Nature",
];

const STATS = [
  { value: 50, suffix: "+", label: "Sources we follow", note: "blogs, videos & more" },
  { value: 10, suffix: "K+", label: "Stories read daily", note: "so you don't have to" },
  { value: 500, suffix: "+", label: "Happy readers", note: "and counting" },
  { value: 5, suffix: " min", label: "To catch up", note: "most mornings" },
];

const STEPS = [
  {
    icon: Heart,
    step: "01",
    title: "Pick what you love",
    body: "Choose the topics you care about — from space to startups — and we'll tune your feed to match.",
    tags: ["AI", "Science", "Startups", "Design"],
    tint: "brand" as const,
  },
  {
    icon: Rss,
    step: "02",
    title: "We do the reading",
    body: "Every day we scan your sources and pull out the stories actually worth your time. No filler.",
    tags: ["Blogs", "Videos", "Newsletters"],
    tint: "accent" as const,
  },
  {
    icon: Mail,
    step: "03",
    title: "Get a short brief",
    body: "A friendly email lands in your inbox — ready to skim in minutes, on whatever schedule you like.",
    tags: ["Daily", "Weekly", "Instant"],
    tint: "green" as const,
  },
];

const FEATURES = [
  {
    icon: Layers,
    title: "Every source, one place",
    body: "Blogs, videos, newsletters and news sites — gathered into a single, calm feed.",
  },
  {
    icon: Sparkles,
    title: "Summaries you can skim",
    body: "Each story is boiled down to the few lines that matter. Plain language, no jargon.",
  },
  {
    icon: Inbox,
    title: "Briefs in your inbox",
    body: "Pick daily, weekly or instant — your news arrives when you actually want it.",
  },
  {
    icon: Brain,
    title: "Topics that match you",
    body: "The more you read, the better your feed gets at guessing what you'll care about.",
  },
  {
    icon: Clock,
    title: "Fits your day",
    body: "Reading time is shown up front, so you always know the commitment before you click.",
  },
  {
    icon: Shield,
    title: "Private by default",
    body: "Your interests stay yours. No tracking, no ads, and no selling your data — ever.",
  },
];

const WHY = [
  {
    title: "Save hours every week",
    body: "Stop opening ten tabs to catch up. We bring the day's news to one quiet place.",
  },
  {
    title: "No noise, just signal",
    body: "We skip the filler and keep only the stories that are actually worth your time.",
  },
  {
    title: "All your sources together",
    body: "Blogs, videos and newsletters sit side by side — finally, in one view.",
  },
  {
    title: "Made for your schedule",
    body: "Morning person or night owl, your brief arrives at the moment that suits you.",
  },
];

const TESTIMONIALS = [
  {
    quote:
      "I used to spend an hour every morning catching up. Now it takes five minutes — and I actually remember what I read.",
    name: "Priya S.",
    role: "Product Lead",
    initials: "PS",
  },
  {
    quote:
      "The summaries are spot on. It feels like a friend who reads everything and tells me the good parts.",
    name: "Daniel M.",
    role: "Founder",
    initials: "DM",
  },
  {
    quote:
      "I finally unsubscribed from four newsletters. This does all of it, in one calm email.",
    name: "Sofia R.",
    role: "Designer",
    initials: "SR",
  },
];

const FAQS = [
  {
    q: "How does the summary work?",
    a: "We read each story and turn it into a short, plain-language summary — just the key points. No jargon, no clickbait.",
  },
  {
    q: "Can I choose when I get emails?",
    a: "Yes. Pick daily, weekly or instant, and change it anytime from your settings. You're always in control.",
  },
  {
    q: "What kinds of sources do you follow?",
    a: "Blogs, news sites, video channels and newsletters. You can even add your own favorites so nothing important is missed.",
  },
  {
    q: "Is my information kept private?",
    a: "Always. We never sell or share your data, we don't run ads, and you can delete your account at any time.",
  },
];

/* ------------------------------------------------------------------ */
/* Small building blocks                                               */
/* ------------------------------------------------------------------ */

function TrustRow() {
  const items = [
    { icon: Shield, label: "Private by default" },
    { icon: Zap, label: "Ready in 2 minutes" },
    { icon: Heart, label: "No spam, ever" },
  ];
  return (
    <div className="flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-sm text-slate-500">
      {items.map((item) => (
        <span key={item.label} className="inline-flex items-center gap-1.5">
          <item.icon className="h-4 w-4 text-brand-500" />
          {item.label}
        </span>
      ))}
    </div>
  );
}

function DigestPreview() {
  const stories = [
    { tag: "AI", tagClass: "badge-brand", title: "A calmer way to build with smart tools", source: "The Verge" },
    { tag: "Space", tagClass: "badge-amber", title: "New images from the deep-space telescope", source: "NASA" },
    { tag: "Startups", tagClass: "badge-green", title: "Why small teams are winning right now", source: "TechCrunch" },
  ];

  return (
    <div className="relative mx-auto w-full max-w-md">
      {/* Ambient glow behind the card */}
      <div className="absolute -inset-6 -z-10 rounded-[2rem] bg-gradient-to-br from-brand-500/20 via-brand-400/10 to-accent-400/20 blur-2xl" />

      <div className="glass animate-float rounded-3xl p-5 shadow-card-hover">
        <div className="mb-4 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500 to-accent-500 text-white shadow-glow">
            <Mail className="h-5 w-5" />
          </div>
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold text-slate-900">Your morning brief</p>
            <p className="text-xs text-slate-500">Today · 3 min read</p>
          </div>
          <span className="ml-auto inline-flex items-center gap-1 rounded-full bg-accent-50 px-2.5 py-1 text-xs font-semibold text-accent-700 ring-1 ring-inset ring-accent-100">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping-soft rounded-full bg-accent-400" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-accent-500" />
            </span>
            New
          </span>
        </div>

        <div className="space-y-3">
          {stories.map((story) => (
            <div
              key={story.title}
              className="flex items-start gap-3 rounded-xl border border-slate-100 bg-white/70 p-3 transition-colors hover:border-brand-100"
            >
              <span className={cn("mt-0.5", story.tagClass)}>{story.tag}</span>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-slate-800">{story.title}</p>
                <p className="text-xs text-slate-400">{story.source}</p>
              </div>
              <ArrowUpRight className="h-4 w-4 flex-shrink-0 text-slate-300" />
            </div>
          ))}
        </div>

        <div className="mt-4 flex items-center justify-between border-t border-slate-100 pt-3">
          <span className="text-xs text-slate-500">Curated for you</span>
          <span className="inline-flex items-center gap-1 text-xs font-semibold text-brand-600">
            Read brief <ArrowRight className="h-3.5 w-3.5" />
          </span>
        </div>
      </div>

      {/* Floating chips */}
      <div className="animate-float-slow absolute -left-6 top-6 hidden rounded-full border border-white/60 bg-white/80 px-3 py-1.5 text-xs font-medium text-slate-700 shadow-card backdrop-blur sm:block">
        <span className="inline-flex items-center gap-1.5">
          <Sparkles className="h-3.5 w-3.5 text-brand-500" /> AI
        </span>
      </div>
      <div className="animate-float absolute -right-5 bottom-10 hidden rounded-full border border-white/60 bg-white/80 px-3 py-1.5 text-xs font-medium text-slate-700 shadow-card backdrop-blur [animation-delay:1.2s] sm:block">
        <span className="inline-flex items-center gap-1.5">
          <PlayCircle className="h-3.5 w-3.5 text-accent-500" /> Videos
        </span>
      </div>
    </div>
  );
}

function SourceTicker() {
  const row = [...SOURCES, ...SOURCES];
  return (
    <div className="relative overflow-hidden py-2">
      <div className="pointer-events-none absolute inset-y-0 left-0 z-10 w-20 bg-gradient-to-r from-slate-50 to-transparent" />
      <div className="pointer-events-none absolute inset-y-0 right-0 z-10 w-20 bg-gradient-to-l from-slate-50 to-transparent" />
      <div className="flex w-max animate-marquee gap-3 hover:[animation-play-state:paused]">
        {row.map((source, i) => (
          <span
            key={`${source}-${i}`}
            className="inline-flex items-center gap-2 whitespace-nowrap rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-600 shadow-sm"
          >
            <Newspaper className="h-3.5 w-3.5 text-brand-400" />
            {source}
          </span>
        ))}
      </div>
    </div>
  );
}

function FaqItem({
  q,
  a,
  open,
  onToggle,
}: {
  q: string;
  a: string;
  open: boolean;
  onToggle: () => void;
}) {
  return (
    <div
      className={cn(
        "card overflow-hidden p-0 transition-all duration-300",
        open ? "border-brand-200 shadow-card-hover" : "hover:border-slate-300"
      )}
    >
      <button
        type="button"
        onClick={onToggle}
        aria-expanded={open}
        className="flex w-full items-center justify-between gap-4 px-6 py-5 text-left"
      >
        <span className="text-base font-semibold text-slate-900">{q}</span>
        <span
          className={cn(
            "flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-slate-100 text-slate-500 transition-all duration-300",
            open && "rotate-180 bg-brand-100 text-brand-700"
          )}
        >
          <ChevronDown className="h-4 w-4" />
        </span>
      </button>
      <div
        className={cn(
          "grid transition-all duration-300 ease-out",
          open ? "grid-rows-[1fr] opacity-100" : "grid-rows-[0fr] opacity-0"
        )}
      >
        <div className="overflow-hidden">
          <p className="px-6 pb-5 text-sm leading-relaxed text-slate-600">{a}</p>
        </div>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Page                                                                */
/* ------------------------------------------------------------------ */

export default function HomePage() {
  const { isAuthenticated } = useAuth();
  const [openFaq, setOpenFaq] = useState<number | null>(0);

  return (
    <div className="space-y-24">
      {/* ============ HERO ============ */}
      <section className="relative overflow-hidden pt-10">
        {/* Animated gradient blooms — clipped by their own layer and faded to
            transparent on all four sides, so the container's `overflow-hidden`
            never shows up as a hard-edged rectangle. */}
        <div className="mask-fade-x pointer-events-none absolute inset-0 -z-10 overflow-hidden">
          <div className="mask-fade-y relative h-full w-full">
            <div className="animate-blob absolute -left-72 -top-80 h-[46rem] w-[46rem] rounded-full bg-brand-300/40 blur-[120px]" />
            <div className="animate-blob absolute -right-80 -top-20 h-[42rem] w-[42rem] rounded-full bg-accent-300/35 blur-[120px] [animation-delay:3s]" />
            <div className="animate-blob absolute -bottom-96 left-1/4 h-[38rem] w-[38rem] rounded-full bg-fuchsia-300/30 blur-[120px] [animation-delay:6s]" />
            <div className="dot-grid absolute inset-0 opacity-50 [mask-image:radial-gradient(ellipse_at_center,black,transparent_70%)]" />
          </div>
        </div>

        <div className="mx-auto grid max-w-7xl items-center gap-14 py-14 lg:grid-cols-2 lg:py-20">
          <div className="text-center lg:text-left">
            <Reveal>
              <span className="section-eyebrow">
                <Sparkles className="h-3.5 w-3.5" />
                Your personal news assistant
              </span>
            </Reveal>

            <Reveal delay={80}>
              <h1 className="mt-6 text-4xl font-extrabold leading-[1.1] tracking-tight text-slate-900 sm:text-5xl lg:text-6xl">
                Never miss the news
                <br />
                that <span className="gradient-text-animated">matters to&nbsp;you</span>
              </h1>
            </Reveal>

            <Reveal delay={160}>
              <p className="mx-auto mt-6 max-w-xl text-lg leading-relaxed text-slate-600 lg:mx-0">
                AI Pulse reads hundreds of stories every day and sends you a short, friendly brief on
                the topics you love. Set up takes less than two minutes — and it&apos;s free.
              </p>
            </Reveal>

            <Reveal delay={240}>
              <div className="mt-8 flex flex-col items-center gap-3 sm:flex-row lg:justify-start sm:justify-center">
                {isAuthenticated ? (
                  <>
                    <Link to="/news" className="btn-primary px-6 py-3 text-base">
                      Open my news <ArrowRight className="h-5 w-5" />
                    </Link>
                    <Link to="/settings" className="btn-secondary px-6 py-3 text-base">
                      My settings
                    </Link>
                  </>
                ) : (
                  <>
                    <Link to="/register" className="btn-primary px-6 py-3 text-base">
                      Start for free <ArrowRight className="h-5 w-5" />
                    </Link>
                    <Link to="/login" className="btn-secondary px-6 py-3 text-base">
                      I have an account
                    </Link>
                  </>
                )}
              </div>
            </Reveal>

            <Reveal delay={320}>
              <div className="mt-8">
                <TrustRow />
              </div>
            </Reveal>
          </div>

          <Reveal delay={200} className="relative">
            <DigestPreview />
          </Reveal>
        </div>
      </section>

      {/* ============ SOURCE TICKER ============ */}
      <section className="border-y border-slate-200/70 bg-slate-50/60">
        <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
          <p className="mb-5 text-center text-xs font-semibold uppercase tracking-widest text-slate-400">
            Following stories from sources you trust
          </p>
          <SourceTicker />
        </div>
      </section>

      {/* ============ STATS ============ */}
      <section className="mx-auto max-w-7xl">
        <div className="grid grid-cols-2 gap-5 lg:grid-cols-4">
          {STATS.map((stat, i) => (
            <Reveal key={stat.label} delay={i * 90}>
              <div className="card card-hover h-full text-center">
                <div className="text-3xl font-extrabold text-slate-900 sm:text-4xl">
                  <CountUp end={stat.value} suffix={stat.suffix} />
                </div>
                <p className="mt-1 text-sm font-semibold text-slate-700">{stat.label}</p>
                <p className="text-xs text-slate-400">{stat.note}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </section>

      {/* ============ HOW IT WORKS ============ */}
      <section id="how-it-works" className="mx-auto max-w-7xl scroll-mt-24">
        <Reveal className="mx-auto max-w-2xl text-center">
          <span className="section-eyebrow">How it works</span>
          <h2 className="mt-5 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
            Three easy steps to a calmer inbox
          </h2>
          <p className="mt-3 text-slate-600">
            No feeds to configure, no settings to drown in. Just tell us what you like and we handle the rest.
          </p>
        </Reveal>

        <div className="relative mt-14 grid gap-8 md:grid-cols-3">
          {/* Connector line */}
          <div className="absolute left-0 right-0 top-10 hidden h-px bg-gradient-to-r from-brand-200 via-accent-200 to-brand-200 md:block" />

          {STEPS.map((step, i) => {
            const tintStyles =
              step.tint === "brand"
                ? "from-brand-500 to-brand-700"
                : step.tint === "accent"
                  ? "from-accent-400 to-accent-600"
                  : "from-emerald-500 to-emerald-600";
            const tagStyles =
              step.tint === "brand"
                ? "bg-brand-50 text-brand-700"
                : step.tint === "accent"
                  ? "bg-accent-50 text-accent-700"
                  : "bg-emerald-50 text-emerald-700";

            return (
              <Reveal key={step.step} delay={i * 120}>
                <div className="card card-hover relative h-full text-center">
                  <div
                    className={cn(
                      "mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br text-white shadow-glow",
                      tintStyles
                    )}
                  >
                    <step.icon className="h-7 w-7" />
                  </div>
                  <div className="mx-auto mt-4 inline-flex h-7 w-7 items-center justify-center rounded-full bg-slate-100 text-xs font-bold text-slate-500">
                    {i + 1}
                  </div>
                  <h3 className="mt-3 text-xl font-semibold text-slate-900">{step.title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-slate-600">{step.body}</p>
                  <div className="mt-4 flex flex-wrap justify-center gap-2">
                    {step.tags.map((tag) => (
                      <span key={tag} className={cn("rounded-full px-3 py-1 text-xs font-medium", tagStyles)}>
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              </Reveal>
            );
          })}
        </div>
      </section>

      {/* ============ FEATURES ============ */}
      <section className="mx-auto max-w-7xl">
        <Reveal className="mx-auto max-w-2xl text-center">
          <span className="section-eyebrow">Why you&apos;ll love it</span>
          <h2 className="mt-5 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
            Everything you need, nothing you don&apos;t
          </h2>
          <p className="mt-3 text-slate-600">
            A small set of thoughtful features, designed to save you time — not add to your to-do list.
          </p>
        </Reveal>

        <div className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((feature, i) => (
            <Reveal key={feature.title} delay={(i % 3) * 100}>
              <div className="card card-hover group h-full">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-brand-50 text-brand-600 transition-all duration-300 group-hover:bg-gradient-to-br group-hover:from-brand-500 group-hover:to-accent-500 group-hover:text-white group-hover:shadow-glow">
                  <feature.icon className="h-6 w-6" />
                </div>
                <h3 className="mt-5 text-lg font-semibold text-slate-900">{feature.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-600">{feature.body}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </section>

      {/* ============ WHY NEWSly ============ */}
      <section className="mx-auto max-w-7xl">
        <div className="card overflow-hidden border-0 bg-gradient-to-br from-brand-600 via-brand-700 to-brand-900 p-0">
          <div className="grid gap-10 p-8 sm:p-12 lg:grid-cols-2 lg:items-center">
            <Reveal>
              <span className="section-eyebrow border-white/20 bg-white/10 text-white">
                Why AI Pulse
              </span>
              <h2 className="mt-5 text-3xl font-bold tracking-tight text-white sm:text-4xl">
                News that respects your time
              </h2>
              <p className="mt-3 text-brand-100">
                Most of us don&apos;t need more information — we need the right information, at the
                right moment. That&apos;s all AI Pulse tries to do.
              </p>

              <ul className="mt-8 space-y-5">
                {WHY.map((item) => (
                  <li key={item.title} className="flex gap-4">
                    <span className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-white/15 text-white">
                      <CheckCircle2 className="h-4 w-4" />
                    </span>
                    <div>
                      <h4 className="font-semibold text-white">{item.title}</h4>
                      <p className="text-sm text-brand-100">{item.body}</p>
                    </div>
                  </li>
                ))}
              </ul>
            </Reveal>

            <Reveal delay={140}>
              <div className="relative">
                <div className="absolute -inset-6 rounded-[2rem] bg-white/10 blur-2xl" />
                <div className="glass relative rounded-3xl p-6 shadow-2xl">
                  <div className="flex items-center gap-3 border-b border-slate-100 pb-4">
                    <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500 to-accent-500 text-white">
                      <Bell className="h-5 w-5" />
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-slate-900">Your brief is ready</p>
                      <p className="text-xs text-slate-500">Delivered at 7:00 AM</p>
                    </div>
                  </div>
                  <div className="mt-4 space-y-3">
                    {[
                      { icon: CalendarClock, label: "Morning brief", meta: "Every day at 7:00" },
                      { icon: Globe, label: "12 sources", meta: "Updated hourly" },
                      { icon: TrendingUp, label: "5 min read", meta: "Skimmable summary" },
                    ].map((row) => (
                      <div
                        key={row.label}
                        className="flex items-center gap-3 rounded-xl border border-slate-100 bg-white/80 p-3"
                      >
                        <row.icon className="h-5 w-5 flex-shrink-0 text-brand-500" />
                        <div className="flex-1">
                          <p className="text-sm font-medium text-slate-800">{row.label}</p>
                          <p className="text-xs text-slate-400">{row.meta}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="mt-4 flex items-center justify-between rounded-xl bg-gradient-to-r from-brand-50 to-accent-50 px-4 py-3">
                    <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-brand-700">
                      <Clock className="h-3.5 w-3.5" /> Time saved today
                    </span>
                    <span className="text-sm font-bold text-slate-900">48 min</span>
                  </div>
                </div>
              </div>
            </Reveal>
          </div>
        </div>
      </section>

      {/* ============ TESTIMONIALS ============ */}
      <section className="mx-auto max-w-7xl">
        <Reveal className="mx-auto max-w-2xl text-center">
          <span className="section-eyebrow">Kind words</span>
          <h2 className="mt-5 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
            Loved by people who hate noise
          </h2>
        </Reveal>

        <div className="mt-14 grid gap-6 md:grid-cols-3">
          {TESTIMONIALS.map((t, i) => (
            <Reveal key={t.name} delay={i * 110}>
              <figure className="card card-hover relative h-full">
                <Quote className="absolute right-6 top-6 h-8 w-8 text-brand-100" />
                <div className="flex items-center gap-1">
                  {Array.from({ length: 5 }).map((_, s) => (
                    <Star key={s} className="h-4 w-4 fill-amber-400 text-amber-400" />
                  ))}
                </div>
                <blockquote className="mt-4 text-sm leading-relaxed text-slate-700">
                  &ldquo;{t.quote}&rdquo;
                </blockquote>
                <figcaption className="mt-6 flex items-center gap-3 border-t border-slate-100 pt-4">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-brand-500 to-accent-500 text-xs font-bold text-white">
                    {t.initials}
                  </div>
                  <div>
                    <div className="text-sm font-semibold text-slate-900">{t.name}</div>
                    <div className="text-xs text-slate-500">{t.role}</div>
                  </div>
                </figcaption>
              </figure>
            </Reveal>
          ))}
        </div>
      </section>

      {/* ============ FAQ ============ */}
      <section className="mx-auto max-w-3xl">
        <Reveal className="text-center">
          <span className="section-eyebrow">Good to know</span>
          <h2 className="mt-5 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
            Frequently asked questions
          </h2>
        </Reveal>

        <Reveal delay={120}>
          <div className="mt-10 space-y-4">
            {FAQS.map((faq, i) => (
              <FaqItem
                key={faq.q}
                q={faq.q}
                a={faq.a}
                open={openFaq === i}
                onToggle={() => setOpenFaq(openFaq === i ? null : i)}
              />
            ))}
          </div>
        </Reveal>
      </section>

      {/* ============ CTA ============ */}
      <section className="mx-auto max-w-7xl">
        <Reveal>
          <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-brand-600 via-brand-700 to-accent-600 px-8 py-16 text-center shadow-card-hover sm:px-16">
            <div className="pointer-events-none absolute inset-0">
              <div className="animate-blob absolute -left-40 -top-40 h-[26rem] w-[26rem] rounded-full bg-white/15 blur-[90px]" />
              <div className="animate-blob absolute -bottom-48 -right-40 h-[30rem] w-[30rem] rounded-full bg-white/15 blur-[90px] [animation-delay:3s]" />
            </div>

            <div className="relative">
              <span className="section-eyebrow border-white/20 bg-white/10 text-white">
                <Zap className="h-3.5 w-3.5" /> Get started today
              </span>
              <h2 className="mt-5 text-3xl font-bold tracking-tight text-white sm:text-4xl">
                Ready to catch up in minutes?
              </h2>
              <p className="mx-auto mt-3 max-w-xl text-brand-100">
                Join readers who get their news the easy way. Free to start — no card required.
              </p>
              <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
                {isAuthenticated ? (
                  <Link to="/news" className="btn-white px-6 py-3 text-base">
                    Open my news <ArrowRight className="h-5 w-5" />
                  </Link>
                ) : (
                  <>
                    <Link to="/register" className="btn-white px-6 py-3 text-base">
                      Start for free <ArrowRight className="h-5 w-5" />
                    </Link>
                    <Link
                      to="/login"
                      className="inline-flex items-center justify-center gap-2 rounded-xl border border-white/30 bg-white/10 px-6 py-3 font-medium text-white transition-all duration-200 hover:bg-white/20"
                    >
                      Sign in
                    </Link>
                  </>
                )}
              </div>
            </div>
          </div>
        </Reveal>
      </section>

      {/* ============ FOOTER ============ */}
      <footer className="border-t border-slate-200 bg-white/60">
        <div className="mx-auto max-w-7xl px-4 py-14 sm:px-6 lg:px-8">
          <div className="grid gap-10 md:grid-cols-4">
            <div className="md:col-span-1">
              <Link to="/" className="inline-flex items-center gap-2">
                <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500 to-accent-500 text-white shadow-glow">
                  <Newspaper className="h-5 w-5" />
                </span>
                <span className="text-lg font-bold text-slate-900">AI Pulse</span>
              </Link>
              <p className="mt-4 text-sm leading-relaxed text-slate-500">
                Your personal news brief — the stories you care about, without the noise.
              </p>
            </div>

            <div>
              <h4 className="text-sm font-semibold uppercase tracking-wide text-slate-900">Product</h4>
              <ul className="mt-4 space-y-2.5 text-sm text-slate-600">
                <li><Link to="/news" className="transition-colors hover:text-brand-600">My news</Link></li>
                <li><Link to="/settings" className="transition-colors hover:text-brand-600">Settings</Link></li>
                <li><Link to="/login" className="transition-colors hover:text-brand-600">Sign in</Link></li>
              </ul>
            </div>

            <div>
              <h4 className="text-sm font-semibold uppercase tracking-wide text-slate-900">Company</h4>
              <ul className="mt-4 space-y-2.5 text-sm text-slate-600">
                <li><a href="#" className="transition-colors hover:text-brand-600">About</a></li>
                <li><a href="#" className="transition-colors hover:text-brand-600">Blog</a></li>
                <li><a href="#" className="transition-colors hover:text-brand-600">Contact</a></li>
              </ul>
            </div>

            <div>
              <h4 className="text-sm font-semibold uppercase tracking-wide text-slate-900">Legal</h4>
              <ul className="mt-4 space-y-2.5 text-sm text-slate-600">
                <li><a href="#" className="transition-colors hover:text-brand-600">Privacy</a></li>
                <li><a href="#" className="transition-colors hover:text-brand-600">Terms</a></li>
                <li>
                  <a
                    href="https://github.com"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 transition-colors hover:text-brand-600"
                  >
                    <Users className="h-4 w-4" /> Open source
                  </a>
                </li>
              </ul>
            </div>
          </div>

          <div className="mt-12 flex flex-col items-center justify-between gap-4 border-t border-slate-200 pt-8 sm:flex-row">
            <p className="text-sm text-slate-500">© 2026 AI Pulse. All rights reserved.</p>
            <p className="inline-flex items-center gap-1.5 text-sm text-slate-400">
              Made with <Heart className="h-3.5 w-3.5 fill-accent-400 text-accent-400" /> for quiet mornings
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
