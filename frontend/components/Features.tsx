"use client";

import React from "react";
import {
  CheckCircle2,
  Eye,
  Sliders,
  Gauge,
  Shield,
  Scale,
  Zap,
} from "lucide-react";

export default function Features() {
  const capabilities = [
    "Agent Management",
    "Mission Orchestration",
    "Runtime Analytics",
    "Mission Telemetry",
    "Token Tracking",
    "Cost Monitoring",
    "Usage Logs",
    "Audit Trails",
    "Loop Detection",
    "Retry Controls",
    "Budget Controls",
    "WebSocket Monitoring",
    "Workspace Management",
    "RBAC Security",
    "Execution Timelines",
    "Live Agent Monitoring",
  ];

  const features = [
    {
      title: "Runtime Observability",
      icon: <Eye size={28} className="text-cyan-400" />,
      desc: "Track every single mission, granular sub-task, LLM raw token count, execution cost metric, and backend event telemetry in absolute real-time.",
    },
    {
      title: "Mission Control Plane",
      icon: <Sliders size={28} className="text-purple-400" />,
      desc: "Take control of processing workflows. Pause running executions, resume states, inject structural parameters, or kill rogue agents instantly.",
    },
    {
      title: "Agent Monitoring",
      icon: <Gauge size={28} className="text-blue-400" />,
      desc: "Dedicated, telemetry-rich operational dashboards tracking performance metrics, model failure flags, and latency for your entire agent cluster.",
    },
    {
      title: "Governance & Security",
      icon: <Shield size={28} className="text-emerald-400" />,
      desc: "Enterprise-grade Role-Based Access Control (RBAC), secure workspace partitioning, token permissions, and immutable audit logs for compliance.",
    },
    {
      title: "Cost Intelligence",
      icon: <Scale size={28} className="text-pink-400" />,
      desc: "Deep analytical graphs monitoring dollar expenditures across multiple workspace instances, coupled with automated ceiling hard-stops.",
    },
    {
      title: "Production Reliability",
      icon: <Zap size={28} className="text-amber-400" />,
      desc: "State-machine loop guards, idempotency filters, failure tolerance thresholds, and retry queue configuration protocols built for scale.",
    },
  ];

  return (
    <>
      {/* CAPABILITY GRID */}
      <section
        id="product"
        className="max-w-7xl mx-auto px-6 pt-32 relative z-10"
      >
        <h2 className="text-3xl md:text-5xl font-black text-center text-white mb-16 font-sans">
          One Platform for AI Runtime Operations
        </h2>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {capabilities.map((cap, idx) => (
            <div
              key={idx}
              className="p-4 rounded-xl border border-cyan-500/10 bg-slate-950/40 backdrop-blur-md flex items-center gap-3 font-mono text-xs text-slate-300"
            >
              <CheckCircle2
                size={14}
                className="text-cyan-400 shrink-0"
              />
              <span>{cap}</span>
            </div>
          ))}
        </div>
      </section>

      {/* DETAILED FEATURE CARDS */}
      <section
        id="features"
        className="max-w-7xl mx-auto px-6 pt-32 relative z-10"
      >
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {features.map((feat, idx) => (
            <div
              key={idx}
              className="p-8 rounded-3xl border border-slate-800 bg-gradient-to-br from-slate-950 to-slate-900/60 backdrop-blur-xl relative overflow-hidden group hover:border-slate-700 transition-all"
            >
              <div className="absolute top-0 right-0 h-24 w-24 bg-cyan-500/5 rounded-bl-full blur-xl group-hover:bg-cyan-500/10 transition-all" />

              <div className="h-14 w-14 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center mb-6">
                {feat.icon}
              </div>

              <h3 className="text-xl font-black text-white mb-3 font-sans">
                {feat.title}
              </h3>

              <p className="text-slate-400 text-sm leading-relaxed">
                {feat.desc}
              </p>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}