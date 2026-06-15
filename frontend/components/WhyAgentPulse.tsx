"use client";

import React from "react";
import { Check, X } from "lucide-react";

export default function WhyAgentPulse() {
  const leftSide = ["Prompt Engineering", "Agent Frameworks", "Workflow Builders", "Model Providers", "RAG Pipelines"];
  const rightSide = ["Execution Visibility", "Runtime Monitoring", "Cost Governance", "Failure Detection", "Mission Analytics", "Safety Controls", "Audit Trails", "Production Operations"];

  return (
    <section className="max-w-7xl mx-auto px-6 pt-32 relative z-10">
      <div className="text-center mb-16">
        <h2 className="text-3xl md:text-5xl font-black text-white mb-4 font-sans">Why AgentPulse?</h2>
        <p className="text-slate-400 text-base font-mono uppercase tracking-wider text-cyan-400 font-bold">
          Most AI tools help you build agents. AgentPulse helps you operate them.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto items-stretch">
        {/* LEFT CARD COLUMN: BUILDING */}
        <div className="rounded-2xl border border-slate-900 bg-slate-950/40 p-8 backdrop-blur-sm flex flex-col justify-between">
          <div>
            <h3 className="text-lg font-black text-slate-400 uppercase tracking-wider border-b border-slate-900 pb-3 mb-6 font-sans">
              Build Agents
            </h3>
            <div className="space-y-4">
              {leftSide.map((item, i) => (
                <div key={i} className="flex items-center gap-3 text-sm text-slate-500 font-medium">
                  <X size={14} className="text-slate-700 shrink-0" />
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* RIGHT CARD COLUMN: OPERATING (PREMIUM FOCUS HIGHLIGHT) */}
        <div className="rounded-2xl border-2 border-cyan-500/30 bg-gradient-to-b from-slate-950 to-slate-900 p-8 shadow-[0_0_40px_rgba(34,211,238,0.05)] flex flex-col justify-between">
          <div>
            <h3 className="text-lg font-black text-cyan-400 uppercase tracking-wider border-b border-slate-800/60 pb-3 mb-6 font-sans">
              Operate Agents
            </h3>
            <div className="space-y-4">
              {rightSide.map((item, i) => (
                <div key={i} className="flex items-center gap-3 text-sm text-slate-200 font-bold">
                  <Check size={14} className="text-cyan-400 shrink-0" />
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <p className="text-center text-slate-400 text-sm md:text-base max-w-2xl mx-auto mt-12 leading-relaxed font-sans border-t border-slate-950 pt-8">
        Building an AI agent is only the beginning. <br />
        <span className="text-white font-bold">Running it safely, reliably, and cost-effectively in production is where AgentPulse comes in.</span>
      </p>
    </section>
  );
}