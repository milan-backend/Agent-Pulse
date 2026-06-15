"use client";

import React from "react";
import { CheckCircle } from "lucide-react";

export default function EnterpriseTrust() {
  const trustFeatures = [
    "Role-Based Access Control (RBAC)", "Workspace Management", "Audit Trails", 
    "BYOK Security", "Mission History", "Cost Analytics", "Governance Policies", "Team Collaboration"
  ];

  return (
    <section className="max-w-7xl mx-auto px-6 pt-32 relative z-10">
      <div className="rounded-3xl border border-slate-900 bg-slate-950/20 p-8 md:p-12 backdrop-blur-md max-w-5xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-8 items-center">
          
          <div className="lg:col-span-2 space-y-4">
            <h2 className="text-2xl md:text-4xl font-black text-white tracking-tight">
              Built For Teams That Need Reliability
            </h2>
            <p className="text-xs md:text-sm text-slate-400 leading-relaxed font-sans">
              Whether you&apos;re an individual developer deploying your first agent or an enterprise operating thousands of missions, AgentPulse provides the visibility and controls needed to run AI systems in production.
            </p>
          </div>

          <div className="lg:col-span-3 grid grid-cols-1 sm:grid-cols-2 gap-4">
            {trustFeatures.map((feat, i) => (
              <div key={i} className="flex items-center gap-2.5 text-xs text-slate-300 font-mono">
                <CheckCircle size={12} className="text-emerald-400 shrink-0" />
                <span>{feat}</span>
              </div>
            ))}
          </div>

        </div>
      </div>
    </section>
  );
}