"use client";

import React from "react";
import { Eye, Shield, Scale, Target, History, Key, Users, Layers } from "lucide-react";

export default function ValueProp() {
  const cards = [
    { title: "Runtime Observability", desc: "Track executions, tool calls, latency, token usage, and failures in real time.", icon: <Eye className="text-cyan-400" /> },
    { title: "Safe Execution Controls", desc: "Prevent infinite loops, runaway agents, and unsafe actions before they become incidents.", icon: <Shield className="text-purple-400" /> },
    { title: "Budget Guardrails", desc: "Set spend limits, alerts, and automated controls across agents and teams.", icon: <Scale className="text-pink-400" /> },
    { title: "Agent Mission Tracking", desc: "Follow every mission from start to completion with full execution history.", icon: <Target className="text-amber-400" /> },
    { title: "Audit Logs", desc: "Maintain accountability with searchable logs and governance records.", icon: <History className="text-blue-400" /> },
    { title: "BYOK Support", desc: "Use your own OpenAI, Anthropic, Gemini, Groq, or custom provider credentials.", icon: <Key className="text-emerald-400" /> },
    { title: "Multi-Agent Monitoring", desc: "Monitor workflows involving multiple agents, tools, and orchestration systems.", icon: <Users className="text-indigo-400" /> },
    { title: "RAG Attribution Tracing", desc: "See exactly which sources influenced every response and decision.", icon: <Layers className="text-orange-400" /> }
  ];

  return (
    <section id="features" className="max-w-7xl mx-auto px-6 pt-32 relative z-10">
      <div className="text-center mb-16">
        <h2 className="text-3xl md:text-5xl font-black text-white mb-4">
          Everything You Need To Run AI Agents In Production
        </h2>
        <p className="text-slate-400 text-sm md:text-base max-w-xl mx-auto">
          Deep structural diagnostic tools engineered to remove operational uncertainty from live LLM workflow pipelines.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
        {cards.map((card, idx) => (
          <div
            key={idx}
            className="p-6 rounded-2xl border border-slate-800 bg-gradient-to-b from-slate-950 to-slate-900/40 backdrop-blur-md hover:border-slate-700/80 transition-all group relative overflow-hidden"
          >
            <div className="h-10 w-10 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center mb-4 group-hover:scale-[1.03] transition-transform">
              {card.icon}
            </div>
            <h3 className="text-base font-black text-white mb-2 font-sans">{card.title}</h3>
            <p className="text-slate-400 text-xs leading-relaxed font-sans">{card.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
}