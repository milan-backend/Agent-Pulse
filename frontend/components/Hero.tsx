"use client";

import React from "react";
import { ArrowRight, Terminal, Cpu, ShieldAlert, Layers } from "lucide-react";
import Link from "next/link";

export default function Hero() {
  const frameworks = [
    "LangGraph", "CrewAI", "AutoGen", "OpenAI Agents", "Semantic Kernel", "Custom Agent Systems"
  ];

  const metrics = [
    { label: "100% Trace Visibility", icon: <Terminal size={14} className="text-cyan-400" /> },
    { label: "Budget Guardrails", icon: <Cpu size={14} className="text-purple-400" /> },
    { label: "Mission-Level Monitoring", icon: <Layers size={14} className="text-amber-400" /> },
    { label: "Production-Ready Governance", icon: <ShieldAlert size={14} className="text-emerald-400" /> }
  ];

  return (
    <section className="relative z-10 max-w-7xl mx-auto px-6 pt-28 md:pt-36 text-center">
      {/* Eyebrow Label Badge Layout */}
      <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-cyan-500/20 bg-cyan-500/5 text-cyan-300 text-xs font-black tracking-widest uppercase mb-6 backdrop-blur-md">
        AI Agent Observability & Governance Platform
      </div>

      {/* Headline Content Block */}
      <h1 className="text-4xl md:text-7xl font-black tracking-tight text-white max-w-5xl mx-auto leading-[1.05]">
        AI Agents Don&apos;t Fail in Demos. <br />
        <span className="bg-gradient-to-r from-red-400 via-orange-500 to-amber-400 bg-clip-text text-transparent drop-shadow-[0_0_30px_rgba(239,68,68,0.2)]">
          They Fail in Production.
        </span>
      </h1>

      {/* Supporting Narrative Layout Copy */}
      <p className="mt-8 text-slate-400 text-base md:text-xl max-w-3xl mx-auto leading-relaxed">
        Monitor, control, and debug AI agents in production with execution tracing, budget controls, runtime observability, and safe execution controls.{" "}
        <span className="text-slate-200 block mt-2 font-medium">
          See every mission, understand every decision, prevent runaway costs, and confidently operate AI agents at scale.
        </span>
      </p>

      {/* Dual CTA Button Weight Mapping Strategy */}
      <div className="mt-10 flex flex-wrap justify-center gap-4 relative z-10">
        <Link
          href="/signup"
          className="px-8 py-4 bg-cyan-400 text-black font-black text-base rounded-xl hover:scale-[1.02] hover:shadow-[0_0_35px_rgba(34,211,238,0.4)] transition-all flex items-center gap-2"
        >
          Start Free <ArrowRight size={18} />
        </Link>

        <button className="px-8 py-4 border border-slate-800 bg-black text-slate-300 font-bold text-base rounded-xl hover:bg-slate-900 hover:text-white transition-all">
          View Demo
        </button>
      </div>

      {/* Framework Compatibility Strip Container */}
      <div className="mt-20 border-t border-b border-slate-900/60 py-4 max-w-4xl mx-auto">
        <p className="text-[10px] font-mono tracking-widest text-slate-500 uppercase mb-2 font-bold">
          Built for modern AI agent frameworks
        </p>
        <div className="flex flex-wrap justify-center gap-x-6 gap-y-2 text-xs font-medium text-slate-400">
          {frameworks.map((fw, idx) => (
            <span key={idx} className="flex items-center gap-2">
              {idx > 0 && <span className="text-slate-700">•</span>}
              {fw}
            </span>
          ))}
        </div>
      </div>

      {/* Core Platform Metric Badges Strips Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-5xl mx-auto mt-12">
        {metrics.map((m, idx) => (
          <div
            key={idx}
            className="p-4 rounded-xl border border-slate-900 bg-slate-950/40 backdrop-blur-md flex items-center justify-center gap-2.5 font-mono text-xs text-slate-300"
          >
            {m.icon}
            <span>{m.label}</span>
          </div>
        ))}
      </div>
    </section>
  );
}