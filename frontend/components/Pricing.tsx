"use client";

import React from "react";
import { CheckCircle2, Cpu } from "lucide-react";

export default function Pricing() {
  return (
    <section id="pricing" className="max-w-7xl mx-auto px-6 pt-32 relative z-10">
      <h2 className="text-3xl md:text-5xl font-black text-center text-white mb-4">
        Predictable Runtime Pricing
      </h2>
      <p className="text-center text-slate-400 text-base md:text-lg mb-16 max-w-xl mx-auto">
        Scale effortlessly from standalone system testing to enterprise agent clusters.
      </p>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-stretch max-w-6xl mx-auto">

        {/* FREE PLAN */}
        <div className="rounded-3xl border border-slate-800 bg-slate-950/60 p-8 flex flex-col justify-between backdrop-blur-md">
          <div>
            <h3 className="text-xl font-black text-white">Free Plan</h3>
            <p className="text-sm text-slate-400 mt-2">
              Perfect for local workflow experimentation and individual sandbox testing.
            </p>

            <div className="mt-6 flex items-baseline gap-1">
              <span className="text-5xl font-black text-white">$0</span>
              <span className="text-xs font-mono text-slate-500">/ month</span>
            </div>

            <div className="mt-8 space-y-4 border-t border-slate-900 pt-6">
              {[
                "1 Agent",
                "10 Runtime Hours",
                "Live WebSocket Updates",
                "Analytics",
                "Missions",
                "Usage Logs",
                "Single Agent Pause",
                "Single Agent Resume",
                "Single Agent Kill",
              ].map((feat, i) => (
                <div
                  key={i}
                  className="flex items-center gap-3 text-sm text-slate-300"
                >
                  <CheckCircle2
                    size={16}
                    className="text-cyan-500 shrink-0"
                  />
                  <span>{feat}</span>
                </div>
              ))}
            </div>
          </div>

          <button className="w-full mt-8 py-4 bg-slate-900 border border-slate-800 text-slate-300 font-bold font-mono text-xs uppercase tracking-wider rounded-xl cursor-default">
            Current Plan
          </button>
        </div>

        {/* PRO PLAN — HIGHLIGHTED */}
        <div className="rounded-3xl border-2 border-cyan-400 bg-gradient-to-b from-slate-950 to-slate-900 p-8 flex flex-col justify-between relative shadow-[0_0_50px_rgba(34,211,238,0.15)] transform lg:scale-[1.03]">
          <div className="absolute top-4 right-4 px-3 py-1 bg-cyan-400 text-black font-mono font-black text-[10px] uppercase rounded-full tracking-wider">
            Most Popular
          </div>

          <div>
            <h3 className="text-xl font-black text-white flex items-center gap-2">
              Pro Stack <Cpu size={16} className="text-cyan-400" />
            </h3>

            <p className="text-sm text-slate-400 mt-2">
              Advanced orchestration plane engineered explicitly for growing AI
              developer teams.
            </p>

            <div className="mt-6 flex items-baseline gap-1">
              <span className="text-5xl font-black text-white">$29</span>
              <span className="text-xs font-mono text-slate-400">/ month</span>
            </div>

            <div className="mt-8 space-y-4 border-t border-cyan-950 pt-6">
              {[
                "10 Agents",
                "10 Team Members",
                "100 Runtime Hours",
                "Multi Workspace",
                "Team Collaboration",
                "MCP Access",
                "Priority Execution",
                "Retry Controls",
                "Loop Detection",
                "Budget Controls",
                "Analytics",
                "Audit Logs",
              ].map((feat, i) => (
                <div
                  key={i}
                  className="flex items-center gap-3 text-sm text-slate-200"
                >
                  <CheckCircle2
                    size={16}
                    className="text-cyan-400 shrink-0"
                  />
                  <span className="font-medium">{feat}</span>
                </div>
              ))}
            </div>
          </div>

          <button className="w-full mt-8 py-4 bg-cyan-400 text-black font-black font-mono text-xs uppercase tracking-wider rounded-xl hover:shadow-[0_0_20px_rgba(34,211,238,0.4)] hover:scale-[1.01] transition-all">
            Upgrade to Pro
          </button>
        </div>

        {/* ENTERPRISE PLAN */}
        <div className="rounded-3xl border border-slate-800 bg-slate-950/60 p-8 flex flex-col justify-between backdrop-blur-md">
          <div>
            <h3 className="text-xl font-black text-white">
              Enterprise Plane
            </h3>

            <p className="text-sm text-slate-400 mt-2">
              Robust, distributed architecture engineered for large-scale
              enterprise AI infrastructure.
            </p>

            <div className="mt-6 flex items-baseline gap-1">
              <span className="text-5xl font-black text-white">$199</span>
              <span className="text-xs font-mono text-slate-500">/ month</span>
            </div>

            <div className="mt-8 space-y-4 border-t border-slate-900 pt-6">
              {[
                "100 Agents",
                "100 Team Members",
                "10000 Runtime Hours",
                "Dedicated Runtime",
                "Maintenance Mode",
                "Unlimited Missions",
                "Priority Runtime Queue",
                "Advanced Audit Logs",
                "Advanced Budget Control",
                "Enterprise Analytics",
                "MCP Integrations",
                "Full Platform Access",
              ].map((feat, i) => (
                <div
                  key={i}
                  className="flex items-center gap-3 text-sm text-slate-300"
                >
                  <CheckCircle2
                    size={16}
                    className="text-emerald-400 shrink-0"
                  />
                  <span>{feat}</span>
                </div>
              ))}
            </div>
          </div>

          <button className="w-full mt-8 py-4 bg-emerald-500 text-black font-black font-mono text-xs uppercase tracking-wider rounded-xl hover:bg-emerald-400 transition-colors">
            Contact Sales
          </button>
        </div>

      </div>
    </section>
  );
}