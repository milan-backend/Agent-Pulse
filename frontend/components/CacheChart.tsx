"use client";

import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

import {
  Database,
  Zap,
  ShieldCheck,
  Activity,
} from "lucide-react";

interface Props {
  usage?: any;
}

export default function CacheChart({
  usage = {},
}: Props) {

  // =========================
  // CACHE DATA
  // =========================

  const cacheHit = Math.min(
    100,
    Math.max(
      0,
      Number(
        usage?.cache_hit_rate || 0
      )
    )
  )

  const cacheMiss = Math.max(
    0,
    100 - cacheHit
  )

  const totalMisses =
    Number(
      usage?.cache_misses || 0
    )

  // =========================
  // CHART DATA ARRAY
  // =========================
  const data = [
    {
      name: "Hit Rate",
      value: cacheHit,
      color: "#22d3ee", // Full Cyan success area
    },
    {
      name: "Miss Rate",
      value: cacheMiss,
      color: "#6366f1", // Premium Purple area from your screenshot!
    },
  ];

  return (

    <div
      className="
        rounded-[32px]
        border
        border-cyan-500/20
        bg-[linear-gradient(180deg,#071120_0%,#091525_100%)]
        p-8
        overflow-hidden
        relative
      "
    >

      {/* GLOW BACKGROUND EFFECT */}
      <div
        className="
          absolute
          top-0
          right-0
          h-56
          w-56
          rounded-full
          bg-cyan-500/10
          blur-3xl
        "
      />

      {/* HEADER */}
      <div
        className="
          relative
          z-10
          flex
          items-center
          justify-between
          mb-8
        "
      >
        <div>
          <h2 className="text-4xl font-black">Cache Analytics</h2>
          <p className="text-slate-400 mt-2">
            Runtime token cache efficiency telemetry.
          </p>
        </div>

        <div
          className="
            flex
            items-center
            gap-3
            rounded-full
            border
            border-cyan-500/20
            bg-cyan-500/10
            px-5
            py-2
          "
        >
          <Database size={18} className="text-cyan-300" />
          <span className="text-sm font-bold text-cyan-300">LIVE CACHE</span>
        </div>
      </div>

      {/* MAIN CONTENT ROW */}
      <div
        className="
          relative
          z-10
          grid
          grid-cols-1
          xl:grid-cols-2
          gap-10
          items-center
        "
      >

        {/* SOLID PIE CHART VIEW */}
        <div className="h-[320px] flex items-center justify-center">
          <ResponsiveContainer width="100%" height={350}>
            <PieChart>
              <Pie
                data={data}
                // FIX: Setting innerRadius to 0 transforms the hollow donut layout into a solid Pie circle chart!
                innerRadius={0}
                outerRadius={120}
                dataKey="value"
                stroke="#071120" // Adds a clean dark dividing stroke between sectors
                strokeWidth={2}
                startAngle={90}
                endAngle={-270}
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>

              <Tooltip
                contentStyle={{
                  backgroundColor: "#071120",
                  borderColor: "rgba(34, 211, 238, 0.2)",
                  borderRadius: "16px",
                  color: "#fff"
                }}
                formatter={(value) => [`${value}%`, "Rate"]}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* RIGHT STATS PANEL */}
        <div className="space-y-5">

          {/* CACHE HIT */}
          <div className="rounded-3xl border border-cyan-500/20 bg-cyan-500/10 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Cache Hit Rate</p>
                <h3 className="mt-3 text-5xl font-black text-cyan-300">{cacheHit}%</h3>
              </div>
              <div className="h-16 w-16 rounded-2xl bg-black/20 flex items-center justify-center">
                <Zap className="text-cyan-300" size={28} />
              </div>
            </div>
          </div>

          {/* CACHE MISS */}
          <div className="rounded-3xl border border-red-500/20 bg-red-500/10 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Cache Misses</p>
                <h3 className="mt-3 text-5xl font-black text-red-300">{totalMisses}</h3>
              </div>
              <div className="h-16 w-16 rounded-2xl bg-black/20 flex items-center justify-center">
                <ShieldCheck className="text-red-300" size={28} />
              </div>
            </div>
          </div>

          {/* TOTAL CACHE HITS */}
          <div className="rounded-3xl border border-green-500/20 bg-green-500/10 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Total Cache Hits</p>
                <h3 className="mt-3 text-5xl font-black text-green-300">{usage?.cache_hits || 0}</h3>
              </div>
              <div className="h-16 w-16 rounded-2xl bg-black/20 flex items-center justify-center">
                <Activity className="text-green-300" size={28} />
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
