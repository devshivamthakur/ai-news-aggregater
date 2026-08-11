"use client";

import { useAuth } from "@/context/AuthContext";
import Link from "next/link";
import { ArrowRight, Mail, Rss, Sparkles, Zap, Settings, Download, Bell, Brain, Globe, Shield, Clock, TrendingUp, Users, Star, ChevronRight, Github } from "lucide-react";

export default function HomePage() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="space-y-20">
      {/* Hero Section */}
      <section className="text-center py-20 animate-fade-up">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-brand-50 rounded-full text-brand-700 text-sm font-medium mb-6">
          <Sparkles className="w-4 h-4" />
          AI-Powered News Aggregation
        </div>
        <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
          Stay Ahead with
          <span className="bg-gradient-to-r from-brand-600 to-brand-800 bg-clip-text text-transparent"> AI News</span>
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-8">
          Get personalized AI news digests delivered to your inbox. We fetch, analyze, and summarize the latest from top sources.
        </p>
        <div className="flex items-center justify-center gap-4">
          {isAuthenticated ? (
            <Link href="/news" className="btn-primary flex items-center gap-2 text-lg px-6 py-3">
              View News <ArrowRight className="w-5 h-5" />
            </Link>
          ) : (
            <>
              <Link href="/register" className="btn-primary flex items-center gap-2 text-lg px-6 py-3">
                Get Started <ArrowRight className="w-5 h-5" />
              </Link>
              <Link href="/login" className="btn-secondary text-lg px-6 py-3">
                Sign In
              </Link>
            </>
          )}
        </div>
        <div className="mt-8 flex items-center justify-center gap-6 text-sm text-gray-500">
          <span className="flex items-center gap-1"><Shield className="w-4 h-4" /> Secure</span>
          <span className="flex items-center gap-1"><Zap className="w-4 h-4" /> Fast</span>
          <span className="flex items-center gap-1"><Globe className="w-4 h-4" /> Global Sources</span>
        </div>
      </section>

      {/* Stats Section */}
      <section className="grid grid-cols-2 md:grid-cols-4 gap-6 stagger">
        {[
          { label: "News Sources", value: "50+", icon: Rss },
          { label: "Articles Analyzed", value: "10K+", icon: Brain },
          { label: "Active Users", value: "500+", icon: Users },
          { label: "Daily Digests", value: "1K+", icon: Mail },
        ].map((stat) => (
          <div key={stat.label} className="card text-center hover:shadow-md transition-shadow">
            <stat.icon className="w-8 h-8 text-brand-600 mx-auto mb-3" />
            <div className="text-3xl font-bold text-gray-900 mb-1">{stat.value}</div>
            <div className="text-sm text-gray-500">{stat.label}</div>
          </div>
        ))}
      </section>

      {/* How it works - Dashboard Style */}
      <section className="card animate-fade-up">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">How It Works</h2>
        <div className="grid md:grid-cols-3 gap-8 stagger">
          {/* Step 1: Set Interests */}
          <div className="text-center p-6 rounded-xl bg-gradient-to-br from-brand-50 to-white border border-brand-100">
            <div className="w-16 h-16 bg-brand-600 text-white rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
              <Settings className="w-8 h-8" />
            </div>
            <div className="inline-flex items-center justify-center w-8 h-8 bg-brand-100 text-brand-700 rounded-full text-sm font-bold mb-3">
              1
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Set Interests</h3>
            <p className="text-gray-600">Choose topics you care about</p>
            <div className="mt-4 flex flex-wrap justify-center gap-2">
              {["AI", "Technology", "Science", "Programming"].map((tag) => (
                <span key={tag} className="px-3 py-1 bg-brand-100 text-brand-700 rounded-full text-xs font-medium">
                  {tag}
                </span>
              ))}
            </div>
          </div>

          {/* Step 2: We Fetch */}
          <div className="text-center p-6 rounded-xl bg-gradient-to-br from-purple-50 to-white border border-purple-100">
            <div className="w-16 h-16 bg-purple-600 text-white rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
              <Download className="w-8 h-8" />
            </div>
            <div className="inline-flex items-center justify-center w-8 h-8 bg-purple-100 text-purple-700 rounded-full text-sm font-bold mb-3">
              2
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">We Fetch</h3>
            <p className="text-gray-600">AI gathers and analyzes news</p>
            <div className="mt-4 flex flex-wrap justify-center gap-2">
              {["RSS", "YouTube", "Medium", "Web"].map((tag) => (
                <span key={tag} className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-medium">
                  {tag}
                </span>
              ))}
            </div>
          </div>

          {/* Step 3: Get Digest */}
          <div className="text-center p-6 rounded-xl bg-gradient-to-br from-green-50 to-white border border-green-100">
            <div className="w-16 h-16 bg-green-600 text-white rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
              <Bell className="w-8 h-8" />
            </div>
            <div className="inline-flex items-center justify-center w-8 h-8 bg-green-100 text-green-700 rounded-full text-sm font-bold mb-3">
              3
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Get Digest</h3>
            <p className="text-gray-600">Receive personalized emails</p>
            <div className="mt-4 flex flex-wrap justify-center gap-2">
              {["Daily", "Weekly", "Instant"].map((tag) => (
                <span key={tag} className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section>
        <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">Powerful Features</h2>
        <div className="grid md:grid-cols-3 gap-8 stagger">
          <div className="card text-center hover:shadow-md hover:border-brand-100 transition-all duration-300">
            <div className="w-12 h-12 bg-brand-100 rounded-xl flex items-center justify-center mx-auto mb-4">
              <Rss className="w-6 h-6 text-brand-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Multi-Source Fetching</h3>
            <p className="text-gray-600">Aggregates from RSS feeds, YouTube channels, Medium publications, and web sources automatically.</p>
          </div>
          <div className="card text-center hover:shadow-md hover:border-brand-100 transition-all duration-300">
            <div className="w-12 h-12 bg-brand-100 rounded-xl flex items-center justify-center mx-auto mb-4">
              <Sparkles className="w-6 h-6 text-brand-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">AI Analysis</h3>
            <p className="text-gray-600">Every article is summarized, categorized, and scored by AI for quick consumption.</p>
          </div>
          <div className="card text-center hover:shadow-md hover:border-brand-100 transition-all duration-300">
            <div className="w-12 h-12 bg-brand-100 rounded-xl flex items-center justify-center mx-auto mb-4">
              <Mail className="w-6 h-6 text-brand-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Email Digests</h3>
            <p className="text-gray-600">Receive personalized digests based on your interests, delivered on your schedule.</p>
          </div>
          <div className="card text-center hover:shadow-md hover:border-brand-100 transition-all duration-300">
            <div className="w-12 h-12 bg-brand-100 rounded-xl flex items-center justify-center mx-auto mb-4">
              <Brain className="w-6 h-6 text-brand-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Smart Categorization</h3>
            <p className="text-gray-600">LLM-powered topic classification keeps your feed organized and relevant.</p>
          </div>
          <div className="card text-center hover:shadow-md hover:border-brand-100 transition-all duration-300">
            <div className="w-12 h-12 bg-brand-100 rounded-xl flex items-center justify-center mx-auto mb-4">
              <Clock className="w-6 h-6 text-brand-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Scheduled Delivery</h3>
            <p className="text-gray-600">Choose daily, weekly, or instant delivery — works around your schedule.</p>
          </div>
          <div className="card text-center hover:shadow-md hover:border-brand-100 transition-all duration-300">
            <div className="w-12 h-12 bg-brand-100 rounded-xl flex items-center justify-center mx-auto mb-4">
              <Shield className="w-6 h-6 text-brand-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Secure & Private</h3>
            <p className="text-gray-600">JWT authentication with bcrypt hashing keeps your account safe.</p>
          </div>
        </div>
      </section>

      {/* Why Choose Us */}
      <section className="card bg-gradient-to-br from-brand-50 to-purple-50 border-brand-100">
        <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">Why Choose AI News Aggregator?</h2>
        <div className="grid md:grid-cols-2 gap-8">
          <div className="space-y-4">
            {[
              { title: "Save Hours Weekly", desc: "No more manually checking dozens of sources. We do the heavy lifting." },
              { title: "AI-Curated Relevance", desc: "Our LLM filters noise and surfaces what matters to you." },
              { title: "Multi-Platform Sources", desc: "RSS, YouTube, Medium, and web — all in one place." },
            ].map((item) => (
              <div key={item.title} className="flex gap-3">
                <div className="flex-shrink-0 w-6 h-6 bg-brand-600 rounded-full flex items-center justify-center">
                  <ChevronRight className="w-4 h-4 text-white" />
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">{item.title}</h4>
                  <p className="text-sm text-gray-600">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
          <div className="space-y-4">
            {[
              { title: "Personalized Digests", desc: "Tailored content based on your unique interests and reading habits." },
              { title: "Admin Dashboard", desc: "Full control over users, sources, and aggregation jobs." },
              { title: "Open Source", desc: "Transparent, auditable code. Self-host or deploy to the cloud." },
            ].map((item) => (
              <div key={item.title} className="flex gap-3">
                <div className="flex-shrink-0 w-6 h-6 bg-brand-600 rounded-full flex items-center justify-center">
                  <ChevronRight className="w-4 h-4 text-white" />
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">{item.title}</h4>
                  <p className="text-sm text-gray-600">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section>
        <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">What Users Say</h2>
        <div className="grid md:grid-cols-3 gap-6 stagger">
          {[
            { name: "Sarah K.", role: "AI Researcher", quote: "This tool saves me hours every week. The AI summaries are incredibly accurate." },
            { name: "Mike R.", role: "Software Engineer", quote: "Finally, a news aggregator that understands what I actually care about." },
            { name: "Emily T.", role: "Product Manager", quote: "The daily digest keeps me informed without overwhelming my inbox." },
          ].map((testimonial) => (
            <div key={testimonial.name} className="card hover:shadow-md transition-shadow">
              <div className="flex items-center gap-1 mb-3">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                ))}
              </div>
              <p className="text-gray-600 mb-4 italic">"{testimonial.quote}"</p>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-brand-100 rounded-full flex items-center justify-center">
                  <span className="text-brand-700 font-semibold text-sm">{testimonial.name[0]}</span>
                </div>
                <div>
                  <div className="font-semibold text-gray-900 text-sm">{testimonial.name}</div>
                  <div className="text-xs text-gray-500">{testimonial.role}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* FAQ */}
      <section className="max-w-3xl mx-auto">
        <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">Frequently Asked Questions</h2>
        <div className="space-y-4">
          {[
            { q: "How does the AI analysis work?", a: "Every article is processed by OpenAI's GPT-4o-mini model, which generates a summary, assigns categories, and scores relevance." },
            { q: "Can I customize my digest frequency?", a: "Yes! Choose from daily, weekly, or instant delivery in your settings." },
            { q: "What sources do you support?", a: "We support RSS feeds, YouTube channels, Medium publications, and custom web sources." },
            { q: "Is my data secure?", a: "Absolutely. We use JWT authentication with bcrypt hashing and never share your data with third parties." },
          ].map((faq) => (
            <div key={faq.q} className="card">
              <h4 className="font-semibold text-gray-900 mb-2">{faq.q}</h4>
              <p className="text-gray-600 text-sm">{faq.a}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="text-center py-16 px-8 bg-gradient-to-r from-brand-600 to-purple-700 rounded-2xl">
        <h2 className="text-3xl font-bold text-white mb-4">Ready to Stay Informed?</h2>
        <p className="text-brand-100 max-w-xl mx-auto mb-8">
          Join hundreds of professionals who get their AI news curated and delivered. Set up takes less than 2 minutes.
        </p>
        <div className="flex items-center justify-center gap-4">
          {isAuthenticated ? (
            <Link href="/news" className="bg-white text-brand-700 hover:bg-brand-50 font-medium px-6 py-3 rounded-lg transition-all flex items-center gap-2">
              View News <ArrowRight className="w-5 h-5" />
            </Link>
          ) : (
            <>
              <Link href="/register" className="bg-white text-brand-700 hover:bg-brand-50 font-medium px-6 py-3 rounded-lg transition-all flex items-center gap-2">
                Get Started Free <ArrowRight className="w-5 h-5" />
              </Link>
              <Link href="/login" className="bg-brand-500/30 text-white hover:bg-brand-500/40 font-medium px-6 py-3 rounded-lg transition-all">
                Sign In
              </Link>
            </>
          )}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-200 pt-12 pb-8">
        <div className="grid md:grid-cols-4 gap-8 mb-8">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 bg-brand-600 rounded-lg flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <span className="font-bold text-gray-900">AI News</span>
            </div>
            <p className="text-sm text-gray-600">AI-powered news aggregation for professionals who stay ahead.</p>
          </div>
          <div>
            <h4 className="font-semibold text-gray-900 mb-3">Product</h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li><Link href="/news" className="hover:text-brand-600 transition-colors">News Feed</Link></li>
              <li><Link href="/settings" className="hover:text-brand-600 transition-colors">Settings</Link></li>
              <li><Link href="/admin" className="hover:text-brand-600 transition-colors">Admin</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-gray-900 mb-3">Company</h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li><a href="#" className="hover:text-brand-600 transition-colors">About</a></li>
              <li><a href="#" className="hover:text-brand-600 transition-colors">Blog</a></li>
              <li><a href="#" className="hover:text-brand-600 transition-colors">Contact</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-gray-900 mb-3">Legal</h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li><a href="#" className="hover:text-brand-600 transition-colors">Privacy</a></li>
              <li><a href="#" className="hover:text-brand-600 transition-colors">Terms</a></li>
            </ul>
          </div>
        </div>
        <div className="flex items-center justify-between pt-8 border-t border-gray-100">
          <p className="text-sm text-gray-500">© 2026 AI News Aggregator. All rights reserved.</p>
          <a href="#" className="text-gray-400 hover:text-brand-600 transition-colors">
            <Github className="w-5 h-5" />
          </a>
        </div>
      </footer>
    </div>
  );
}
