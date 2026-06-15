"use client";

import React from "react";
import Link from "next/link";

export default function Footer() {
  return (
    <>
      {/* FINAL CALL TO ACTION BOX */}
      <section className="max-w-5xl mx-auto px-6 pt-32 pb-20 relative z-10 text-center">
        <div className="rounded-[40px] border border-slate-800 bg-gradient-to-b from-slate-950 via-slate-950 to-slate-900 p-8 md:p-16 backdrop-blur-2xl relative overflow-hidden shadow-[0_0_60px_rgba(147,51,234,0.1)]">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_bottom_left,rgba(34,211,238,0.05),transparent_40%)]" />

          <h2 className="text-3xl md:text-5xl font-black text-white tracking-tight leading-tight">
            Treat AI Agents Like <br />
            <span className="bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
              Production Infrastructure
            </span>
          </h2>

          <p className="mt-6 text-slate-400 text-base md:text-xl max-w-2xl mx-auto leading-relaxed">
            Stop managing autonomous execution flows as black-box prompt
            strings. <br className="hidden md:inline" />
            <span className="text-slate-200">
              Gain absolute execution trace telemetry, stability runtime
              governance, and real-time step failure orchestration controls
              right now.
            </span>
          </p>

          <div className="mt-10 flex flex-wrap justify-center gap-4 relative z-10">
            <button className="px-8 py-4 bg-cyan-400 text-black font-black text-base rounded-xl hover:shadow-[0_0_30px_rgba(34,211,238,0.4)] transition-all">
              Start Free Trial
            </button>

            <button className="px-8 py-4 border border-slate-800 bg-black text-white font-bold text-base rounded-xl hover:bg-slate-900 transition-colors">
              Book Architecture Demo
            </button>
          </div>
        </div>
      </section>

      {/* FOOTER NAVIGATION */}
      <footer className="border-t border-slate-900 bg-black relative z-10">
        <div className="max-w-7xl mx-auto px-6 py-12 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex flex-col items-center md:items-start gap-2">
            <span className="text-xl font-black">
              <span className="text-white">Agent</span>
              <span className="from-cyan-400 to-purple-500 bg-gradient-to-r bg-clip-text text-transparent">
                Pulse
              </span>
            </span>

            <span className="text-xs text-slate-500 font-mono">
              © 2026 AgentPulse Inc. All rights reserved.
            </span>
          </div>

          <div className="flex flex-wrap justify-center gap-x-8 gap-y-2 text-sm font-medium text-slate-400">
            <Link href="/#features" className="hover:text-white transition-colors">
              Product
            </Link>

            <Link href="/#features" className="hover:text-white transition-colors">
              Features
            </Link>

            <Link href="/pricing" className="hover:text-white transition-colors">
              Pricing
            </Link>

            <Link href="/#docs" className="hover:text-white transition-colors">
              Documentation
            </Link>

            <a href="#github" className="hover:text-white transition-colors">
              GitHub
            </a>

            <a href="#linkedin" className="hover:text-white transition-colors">
              LinkedIn
            </a>
          </div>

          <div className="flex flex-wrap justify-center gap-6 text-xs font-mono text-slate-600">
            <Link href="/privacy" className="hover:text-slate-400 transition-colors">
              Privacy Policy
            </Link>

            <Link href="/terms" className="hover:text-slate-400 transition-colors">
              Terms of Service
            </Link>

            <Link href="/refund" className="hover:text-slate-400 transition-colors">
              Refund Policy
            </Link>
          </div>
        </div>
      </footer>
    </>
  );
}