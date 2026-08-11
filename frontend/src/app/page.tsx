"use client";

import { useAuth } from "@/context/AuthContext";
import Link from "next/link";
import { ArrowRight, Mail, Rss, Sparkles, Zap, Settings, Download, Bell } from "lucide-react";

export default function HomePage() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="space-y-16">
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

      {/* Features */}
      <section className="grid md:grid-cols-3 gap-8 stagger">
        <div className="card text-center hover:shadow-md hover:border-brand-100 transition-all duration-300">
          <div className="w-12 h-12 bg-brand-100 rounded-xl flex items-center justify-center mx-auto mb-4">
            <Rss className="w-6 h-6 text-brand-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Multi-Source Fetching</h3>
          <p className="text-gray-600">Aggregates from RSS feeds, YouTube channels, Medium publications, and web sources automatically.</p>
        </div>
        <div className="card text-center">
          <div className="w-12 h-12 bg-brand-100 rounded-xl flex items-center justify-center mx-auto mb-4">
            <Sparkles className="w-6 h-6 text-brand-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">AI Analysis</h3>
          <p className="text-gray-600">Every article is summarized, categorized, and scored by AI for quick consumption.</p>
        </div>
        <div className="card text-center">
          <div className="w-12 h-12 bg-brand-100 rounded-xl flex items-center justify-center mx-auto mb-4">
            <Mail className="w-6 h-6 text-brand-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Email Digests</h3>
          <p className="text-gray-600">Receive personalized digests based on your interests, delivered on your schedule.</p>
        </div>
      </section>
    </div>
  );
}
