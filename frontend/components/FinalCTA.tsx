"use client";

import React from "react";
import Link from "next/link";
import { ArrowRight } from "lucide-react";

export default function FinalCTA() {
  return (
    <section className="max-w-5xl mx-auto px-6 pt-32 pb-16 relative z-10 text-center">
      <div className="rounded-[40px] border border-slate-800 bg-gradient-to-b from-slate-950 to-slate-900 p-8 md:p-16 backdrop-blur-2xl relative overflow-hidden shadow-[0_0_60px_rgba(34,211,238,0.08)]">
        
        <h2 className="text-3xl md:text-5xl font-black text-white tracking-tight">
          Deploy Agents With Confidence
        </h2>

        <p className="mt-4 text-slate-400 text-sm md:text-base max-w-xl mx-auto leading-relaxed font-sans">
          Get complete visibility into agent behavior, costs, execution paths, and safety controls before production issues become expensive incidents.
        </p>

        <div className="mt-8 flex flex-wrap justify-center gap-4 relative z-10">
          <Link
            href="/signup"
            className="px-8 py-4 bg-cyan-400 text-black font-black text-sm rounded-xl hover:shadow-[0_0_25px_rgba(34,211,238,0.3)] transition-all flex items-center gap-2"
          >
            Start Free <ArrowRight size={16} />
          </Link>

          <button className="px-8 py-4 border border-slate-800 bg-black text-slate-300 font-bold text-sm rounded-xl hover:bg-slate-900 hover:text-white transition-colors">
            Book Architecture Demo
          </button>
        </div>

        {/* Small Trust Under-Line Copy String */}
        <p className="mt-6 text-[11px] font-mono text-slate-500 tracking-wide">
          No credit card required • Setup in minutes • BYOK supported
        </p>
      </div>
    </section>
  );
}