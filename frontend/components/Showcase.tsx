"use client";

import React, { useState } from "react";
import {
  Terminal,
  LayoutDashboard,
  UserSquare2,
  CheckSquare,
  Rocket,
  Info,
  BarChart3,
  FileText,
  ChevronRight,
} from "lucide-react";

export default function Showcase() {
  const screens = [
    {
      id: "dashboard",
      label: "Main Dashboard",
      icon: <LayoutDashboard size={16} />,
      src: "/agentpulseai.dev_dashboard.png",
      isScrollable: true,
      path: "workspaces/default/overview",
    },
    {
      id: "agent_dashboard",
      label: "Agent Hub",
      icon: <UserSquare2 size={16} />,
      src: "/agentpulseai.dev_agent_dashboard.png",
      isScrollable: false,
      path: "workspaces/default/agents",
    },
    {
      id: "agent_tasks",
      label: "Agent Tasks",
      icon: <CheckSquare size={16} />,
      src: "/agentpulseai.dev_agent_tasks.png",
      isScrollable: false,
      path: "workspaces/default/tasks",
    },
    {
      id: "missions",
      label: "Missions Engine",
      icon: <Rocket size={16} />,
      src: "/agentpulseai.dev_missions_page.png",
      isScrollable: true,
      path: "workspaces/default/missions",
    },
    {
      id: "mission_info",
      label: "Mission Logs",
      icon: <Info size={16} />,
      src: "/agentpulseai.dev_mission_information.png",
      isScrollable: false,
      path: "workspaces/default/missions/logs",
    },
    {
      id: "analytics",
      label: "Token Analytics",
      icon: <BarChart3 size={16} />,
      src: "/agentpulseai.dev_analytics.png",
      isScrollable: false,
      path: "workspaces/default/analytics",
    },
    {
      id: "usage_logs",
      label: "Audit Trails",
      icon: <FileText size={16} />,
      src: "/agentpulseai.dev_usage_logs.png",
      isScrollable: true,
      path: "workspaces/default/audit-history",
    },
  ];

  const [activeTab, setActiveTab] = useState(screens[0]);

  return (
    <section className="max-w-7xl mx-auto px-6 pt-32 relative z-10">
      <div className="text-center mb-16">
        <h2 className="text-3xl md:text-5xl font-black text-white mb-4 font-sans">
          Engineered for Complex AI Architectures
        </h2>

        <p className="text-slate-400 text-base md:text-lg max-w-2xl mx-auto">
          Click through the control panels below to see exactly how AgentPulse
          tracks and manages live agent missions.
        </p>
      </div>

      {/* FIXED CONTAINER: STABLE WIDTH DISPATCHER */}
      <div className="flex flex-col md:flex-row gap-6 items-start max-w-6xl mx-auto">
        {/* LEFT COMPONENT: ROCK-SOLID SIDEBAR WIDTH */}
        <div className="w-full md:w-64 flex flex-row md:flex-col overflow-x-auto md:overflow-x-visible gap-2 bg-slate-950/60 p-3 rounded-2xl border border-slate-800/80 backdrop-blur-md shrink-0">
          <div className="hidden md:block px-3 py-2 text-[10px] font-mono uppercase font-bold tracking-widest text-slate-500 mb-2">
            Select Live View
          </div>

          {screens.map((screen) => {
            const isActive = activeTab.id === screen.id;

            return (
              <button
                key={screen.id}
                onClick={() => setActiveTab(screen)}
                className={`flex items-center justify-between gap-3 px-4 py-3 rounded-xl font-medium text-xs font-mono tracking-wide transition-all whitespace-nowrap text-left w-full ${
                  isActive
                    ? "bg-cyan-500/10 border border-cyan-400/30 text-cyan-300 shadow-[0_0_20px_rgba(34,211,238,0.05)]"
                    : "border border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/40"
                }`}
              >
                <div className="flex items-center gap-2.5 min-w-0">
                  <span
                    className={`shrink-0 ${
                      isActive ? "text-cyan-400" : "text-slate-500"
                    }`}
                  >
                    {screen.icon}
                  </span>

                  <span className="truncate">{screen.label}</span>
                </div>

                <ChevronRight
                  size={14}
                  className={`hidden md:block shrink-0 transition-transform ${
                    isActive
                      ? "translate-x-0.5 text-cyan-400"
                      : "text-transparent"
                  }`}
                />
              </button>
            );
          })}
        </div>

        {/* RIGHT COMPONENT: EXPANDABLE SIMULATOR HUB */}
        <div className="flex-1 w-full border border-slate-800 rounded-2xl bg-slate-950 overflow-hidden shadow-[0_0_60px_rgba(34,211,238,0.05)] flex flex-col">
          {/* Header Bar with Fixes for Text Clipping */}
          <div className="bg-slate-900/60 px-5 py-3.5 flex items-center justify-between border-b border-slate-800/80 backdrop-blur-md gap-4">
            <div className="flex items-center gap-2 min-w-0">
              <div className="flex gap-1.5 shrink-0">
                <div className="w-2.5 h-2.5 rounded-full bg-red-500/40" />
                <div className="w-2.5 h-2.5 rounded-full bg-amber-500/40" />
                <div className="w-2.5 h-2.5 rounded-full bg-emerald-500/40" />
              </div>

              <span className="text-[11px] font-mono text-slate-500 ml-4 tracking-wider flex items-center gap-1.5 truncate">
                <Terminal size={12} className="shrink-0" />{" "}
                app.agentpulse.com/{activeTab.path}
              </span>
            </div>

            <div className="shrink-0 font-mono text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/20 whitespace-nowrap">
              {activeTab.isScrollable
                ? "Scrollable Page"
                : "Cropped Panel"}
            </div>
          </div>

          {/* Screenshot Display Frame Area */}
          <div className="bg-slate-950 flex-1 flex flex-col items-center justify-start relative overflow-hidden h-[520px]">
            <div
              className={`w-full h-full ${
                activeTab.isScrollable
                  ? "overflow-y-scroll scrollbar-thin scrollbar-thumb-slate-800 scrollbar-track-transparent"
                  : "overflow-hidden flex items-center justify-center p-4 bg-slate-900/20"
              }`}
            >
              <img
                key={activeTab.id}
                src={activeTab.src}
                alt={`AgentPulse ${activeTab.label}`}
                className={`w-full ${
                  activeTab.isScrollable
                    ? "h-auto object-top"
                    : "h-full object-contain object-center rounded-lg"
                }`}
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}