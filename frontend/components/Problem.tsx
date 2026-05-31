"use client";

import React from "react";
import {
  Repeat,
  AlertTriangle,
  Layers,
  Eye,
  History,
  Scale,
  Terminal,
  TrendingUp,
} from "lucide-react";

export default function Problem() {
  const problems = [
    {
      title: "Infinite Loops",
      icon: <Repeat size={24} className="text-red-400" />,
      desc: "Agents spinning recursively on the same step, exhausting rate limits and tokens in minutes.",
    },
    {
      title: "Retry Storms",
      icon: <AlertTriangle size={24} className="text-amber-400" />,
      desc: "Cascading step script exceptions causing uncontrolled re-execution bursts without thresholds.",
    },
    {
      title: "Duplicate Executions",
      icon: <Layers size={24} className="text-orange-400" />,
      desc: "Race conditions generating multiple agent instances attacking identical downstream tasks.",
    },
    {
      title: "Hidden Failures",
      icon: <Eye size={24} className="text-purple-400" />,
      desc: "Background processes failing silently while giving external clients a deceptive 200 OK stance.",
    },
    {
      title: "Missing Audit Trails",
      icon: <History size={24} className="text-blue-400" />,
      desc: "Zero operational records tracking agent tool actions, making historical debugging impossible.",
    },
    {
      title: "Budget Overruns",
      icon: <Scale size={24} className="text-emerald-400" />,
      desc: "A single rogue multi-agent run burning through thousands of dollars due to uncapped execution tiers.",
    },
    {
      title: "No Runtime Visibility",
      icon: <Terminal size={24} className="text-slate-400" />,
      desc: "Operating blind without live pipeline tracking or execution telemetry stream diagnostics.",
    },
    {
      title: "Token Cost Explosions",
      icon: <TrendingUp size={24} className="text-pink-400" />,
      desc: "Massive text prompt payloads expanding payload context arrays exponentially behind the scenes.",
    },
  ];

  return (
    <section className="max-w-7xl mx-auto px-6 pt-32 relative z-10">
      <h2 className="text-3xl md:text-5xl font-black text-center text-white mb-16">
        Running AI Agents in Production is Hard
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {problems.map((item, idx) => (
          <div
            key={idx}
            className="rounded-2xl border border-slate-800 bg-slate-950/60 p-6 backdrop-blur-md hover:border-slate-700/60 transition-all group"
          >
            <div className="h-12 w-12 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center mb-4 group-hover:scale-[1.05] transition-transform">
              {item.icon}
            </div>

            <h3 className="text-lg font-black text-white mb-2">
              {item.title}
            </h3>

            <p className="text-slate-400 text-sm leading-relaxed">
              {item.desc}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}