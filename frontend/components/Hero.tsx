"use client";

import React, { useState } from "react";
import {
  ArrowRight,
  Radio,
  Activity,
  Gauge,
  Repeat,
  Terminal,
  Pause,
  Play,
  RefreshCw,
  RotateCcw,
} from "lucide-react";
import Link from "next/link";

export default function Hero() {
  const [simulatedStatus, setSimulatedStatus] = useState("Running");
  const [simulatedRetries, setSimulatedRetries] = useState(2);
  const [simulatedCost, setSimulatedCost] = useState(4.12);

  return (
    <section className="relative z-10 max-w-7xl mx-auto px-6 pt-20 md:pt-32 text-center">
      <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-cyan-500/20 bg-cyan-500/5 text-cyan-300 text-xs font-black tracking-widest uppercase mb-6 backdrop-blur-md">
        <Radio size={12} className="animate-pulse" /> Production Engine Live
        v2.5
      </div>

      <h1 className="text-5xl md:text-7xl font-black tracking-tight text-white max-w-5xl mx-auto leading-[1.05]">
        AI Agents Don't Fail in Demos. <br />
        <span className="bg-gradient-to-r from-red-400 via-orange-500 to-amber-400 bg-clip-text text-transparent drop-shadow-[0_0_30px_rgba(239,68,68,0.2)]">
          They Fail in Production.
        </span>
      </h1>

      <p className="mt-8 text-slate-400 text-lg md:text-2xl max-w-3xl mx-auto font-medium leading-relaxed">
        Observe every mission. Control every execution. Govern every agent.{" "}
        <br className="hidden md:inline" />
        <span className="text-slate-200">
          Pause, resume, retry, kill, audit, and monitor AI workloads
        </span>{" "}
        from a single runtime control plane.
      </p>

      {/* Main Central CTA Links */}
      <div className="mt-10 flex flex-wrap justify-center gap-4">
        <Link
          href="/signup"
          className="px-8 py-4 bg-cyan-400 text-black font-black text-lg rounded-2xl hover:scale-[1.02] hover:shadow-[0_0_40px_rgba(34,211,238,0.4)] transition-all flex items-center gap-2"
        >
          Start Free <ArrowRight size={20} />
        </Link>

        <button className="px-8 py-4 border border-slate-800 bg-slate-900/40 text-white font-black text-lg rounded-2xl hover:bg-slate-900/80 backdrop-blur-md transition-all">
          View Demo
        </button>
      </div>

      {/* PLATFORM PREVIEW INTERACTIVE PLANE */}
      <div className="mt-20 max-w-5xl mx-auto border border-cyan-500/30 rounded-[32px] bg-gradient-to-b from-slate-950/90 to-slate-900/90 p-6 md:p-8 backdrop-blur-2xl shadow-[0_0_80px_rgba(34,211,238,0.15)] text-left relative overflow-hidden group">
        <div className="absolute top-0 right-0 h-96 w-96 rounded-full bg-cyan-500/5 blur-3xl" />

        <div className="flex flex-wrap items-center justify-between pb-6 border-b border-slate-800 gap-4">
          <div className="flex items-center gap-3">
            <div className="h-4 w-4 rounded-full bg-cyan-400 animate-pulse shadow-[0_0_10px_rgba(34,211,238,1)]" />

            <div>
              <h3 className="font-mono text-xs text-slate-500 uppercase tracking-widest font-black">
                Runtime Control Plane
              </h3>

              <h2 className="text-xl font-black text-white flex items-center gap-2 mt-0.5">
                Customer Support Agent{" "}
                <span className="font-mono text-xs text-slate-400 font-normal">
                  #cl_mission_9831
                </span>
              </h2>
            </div>
          </div>

          <div className="flex items-center gap-3 bg-slate-900 px-4 py-2 rounded-xl border border-slate-800">
            <span className="text-xs font-mono text-slate-400">STATUS:</span>

            <span
              className={`text-xs font-black px-2.5 py-0.5 rounded-md ${
                simulatedStatus === "Running"
                  ? "bg-cyan-500/10 text-cyan-300"
                  : simulatedStatus === "Paused"
                  ? "bg-amber-500/10 text-amber-300"
                  : "bg-red-500/10 text-red-400"
              }`}
            >
              {simulatedStatus.toUpperCase()}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 py-8">
          <div className="space-y-4 border-r border-slate-800/50 pr-4">
            <div className="flex items-center gap-2 text-slate-400 text-sm font-bold">
              <Activity size={16} className="text-cyan-400" />
              Mission Telemetry
            </div>

            <div className="bg-black/50 p-4 rounded-xl border border-slate-800 font-mono text-xs space-y-2">
              <div className="flex justify-between">
                <span className="text-slate-500">Execution Mode:</span>
                <span className="text-slate-300">Asynchronous</span>
              </div>

              <div className="flex justify-between">
                <span className="text-slate-500">WebSocket Link:</span>
                <span className="text-emerald-400">CONNECTED</span>
              </div>

              <div className="flex justify-between">
                <span className="text-slate-500">Current Task:</span>
                <span className="text-purple-300">
                  Refund Eligibility API
                </span>
              </div>
            </div>
          </div>

          <div className="space-y-4 border-r border-slate-800/50 pr-4">
            <div className="flex items-center gap-2 text-slate-400 text-sm font-bold">
              <Gauge size={16} className="text-purple-400" />
              Token & Budget Controls
            </div>

            <div className="bg-black/50 p-4 rounded-xl border border-slate-800 font-mono text-xs space-y-2">
              <div className="flex justify-between">
                <span className="text-slate-500">Token Tracking:</span>
                <span className="text-slate-300">42,819 tokens</span>
              </div>

              <div className="flex justify-between">
                <span className="text-slate-500">Cost Monitoring:</span>
                <span className="text-cyan-300">
                  ${simulatedCost.toFixed(2)}
                </span>
              </div>

              <div className="flex justify-between">
                <span className="text-slate-500">Budget Limit:</span>
                <span className="text-slate-400">$10.00 max</span>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex items-center gap-2 text-slate-400 text-sm font-bold">
              <Repeat size={16} className="text-amber-400" />
              Production Reliability
            </div>

            <div className="bg-black/50 p-4 rounded-xl border border-slate-800 font-mono text-xs space-y-2">
              <div className="flex justify-between">
                <span className="text-slate-500">Loop Detection:</span>
                <span className="text-emerald-400">0 loops flag</span>
              </div>

              <div className="flex justify-between">
                <span className="text-slate-300">
                  {simulatedRetries} / 5 retries
                </span>
              </div>

              <div className="flex justify-between">
                <span className="text-slate-500">Abnormal Spike:</span>
                <span className="text-emerald-400">Negative</span>
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-3 pt-4 border-t border-slate-800">
          <div className="flex items-center gap-2 text-slate-400 text-sm font-bold">
            <Terminal size={16} className="text-slate-400" />
            Live Execution History & Audit Logs
          </div>

          <div className="bg-black/80 rounded-xl p-4 font-mono text-xs text-slate-300 space-y-2 border border-slate-800/80 h-32 overflow-y-auto">
            <div>
              <span className="text-slate-500">[13:42:01]</span>{" "}
              <span className="text-cyan-400">INFO</span> Initiating Workspace
              Context for user request payload.
            </div>

            <div>
              <span className="text-slate-500">[13:42:03]</span>{" "}
              <span className="text-purple-400">DB</span> Fetching execution
              histories - schema verification successful.
            </div>

            <div>
              <span className="text-slate-500">[13:42:05]</span>{" "}
              <span className="text-amber-400">WARN</span> API Call timeout
              detected. Triggering structural retry mechanism...
            </div>

            <div>
              <span className="text-slate-500">[13:42:06]</span>{" "}
              <span className="text-cyan-400">INFO</span> Event received over
              live WebSockets. Continuing task propagation loop.
            </div>
          </div>
        </div>

        <div className="mt-8 flex flex-wrap gap-4 border-t border-slate-800/60 pt-6">
          <button
            onClick={() => setSimulatedStatus("Paused")}
            className="px-5 py-3 bg-amber-500/10 border border-amber-500/30 text-amber-300 font-mono font-bold text-xs rounded-xl flex items-center gap-2 hover:bg-amber-500/20 transition-all"
          >
            <Pause size={14} />
            Pause Mission
          </button>

          <button
            onClick={() => setSimulatedStatus("Running")}
            className="px-5 py-3 bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 font-mono font-bold text-xs rounded-xl flex items-center gap-2 hover:bg-cyan-500/20 transition-all"
          >
            <Play size={14} />
            Resume Mission
          </button>

          <button
            onClick={() => {
              setSimulatedRetries((p) => p + 1);
              setSimulatedCost((c) => c + 0.45);
            }}
            className="px-5 py-3 bg-purple-500/10 border border-purple-500/30 text-purple-300 font-mono font-bold text-xs rounded-xl flex items-center gap-2 hover:bg-purple-500/20 transition-all"
          >
            <RefreshCw size={14} />
            Retry Mission
          </button>

          <button
            onClick={() => setSimulatedStatus("Killed")}
            className="px-5 py-3 bg-red-500/10 border border-red-500/30 text-red-400 font-mono font-bold text-xs rounded-xl flex items-center gap-2 hover:bg-red-500/20 transition-all"
          >
            <RotateCcw size={14} />
            Kill Mission
          </button>
        </div>
      </div>
    </section>
  );
}