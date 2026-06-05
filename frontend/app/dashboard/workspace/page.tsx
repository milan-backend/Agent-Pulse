"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { 
  Users, 
  Layers, 
  ShieldCheck, 
  KeyRound, 
  ArrowRight, 
  Activity,
  Loader2,
  Settings
} from "lucide-react";
import { getWorkspaceMembers, apiKeyApi } from "@/components/api";

export default function WorkspaceOverviewPage() {
  const [loading, setLoading] = useState(true);
  const [membersCount, setMembersCount] = useState(0);
  const [adminCount, setAdminCount] = useState(0);
  const [keyStatus, setKeyStatus] = useState({ connected: false });
  const [workspaceUID, setWorkspaceUID] = useState("");

  useEffect(() => {
    async function loadOverviewStats() {
      try {
        setLoading(true);
        const roster = await getWorkspaceMembers();
        if (roster) {
          setMembersCount(roster.length);
          setAdminCount(roster.filter((m: any) => m.role?.toLowerCase() === "admin").length);
        }

        if (typeof window !== "undefined") {
          const storedWorkspaceId = localStorage.getItem("workspace_id");
          if (storedWorkspaceId) {
            setWorkspaceUID(storedWorkspaceId.toUpperCase());
            const kData = await apiKeyApi.getKeyStatus(storedWorkspaceId);
            setKeyStatus(kData);
          }
        }
      } catch (err) {
        console.error(err);
      } relative: 
      setLoading(false);
    }
    loadOverviewStats();
  }, []);

  if (loading) {
    return (
      <div className="h-[50vh] w-full flex flex-col items-center justify-center gap-3 font-mono text-xs text-cyan-400 tracking-widest">
        <Loader2 className="animate-spin" size={24} />
        <span>COMPILING OVERVIEW METRICS...</span>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6 px-2 animate-fadeIn">
      
      {/* HEADER SECTION ROW */}
      <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 bg-[#090f1c]/60 border border-slate-800/80 p-6 rounded-2xl">
        <div className="space-y-1">
          <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <Activity size={18} className="text-cyan-400" /> Workspace Overview
          </h2>
          <p className="text-xs text-zinc-400">
            Node Registry: <span className="font-mono text-cyan-300 bg-slate-950 px-2 py-0.5 rounded border border-slate-900 text-[11px] font-bold">{workspaceUID?.substring(0, 12) || "AP-CORE"}</span>
          </p>
        </div>

        {/* COMPACT DASHBOARD INLINE STAT COUNTERS */}
        <div className="flex items-center gap-3 font-mono text-[11px]">
          <div className="bg-slate-950 border border-slate-800 rounded-xl px-4 py-2 flex items-center gap-2">
            <Users size={14} className="text-zinc-500" />
            <span className="text-zinc-500">Roster:</span>
            <span className="text-white font-bold">{membersCount}</span>
          </div>
          <div className="bg-slate-950 border border-slate-800 rounded-xl px-4 py-2 flex items-center gap-2">
            <KeyRound size={14} className={keyStatus.connected ? "text-green-400" : "text-zinc-600"} />
            <span className="text-zinc-500">Vault status:</span>
            <span className={keyStatus.connected ? "text-green-400 font-bold" : "text-zinc-500 font-bold"}>
              {keyStatus.connected ? "CONNECTED" : "OFFLINE"}
            </span>
          </div>
        </div>
      </div>

      {/* GRID HUB QUICK ROUTE CONTROLLERS */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* LINK SECTION 1: TEAM MATRIX LINK */}
        <Link 
          href="/dashboard/workspace/members"
          className="p-6 rounded-2xl border border-slate-800 bg-[#090f1c]/20 hover:bg-[#090f1c]/50 transition-all group flex items-center justify-between gap-6"
        >
          <div className="space-y-1">
            <h3 className="text-sm font-bold text-white group-hover:text-cyan-400 transition-colors flex items-center gap-2">
              <Users size={16} /> Team Members & Roster Clearances
            </h3>
            <p className="text-xs text-zinc-400 font-sans max-w-md">Invite developers, evict accounts, and manage inline operational parameters.</p>
          </div>
          <ArrowRight size={16} className="text-zinc-600 group-hover:text-cyan-400 group-hover:translate-x-1 transition-all shrink-0" />
        </Link>

        {/* LINK SECTION 2: API PROVIDERS LINK */}
        <Link 
          href="/dashboard/workspace/providers"
          className="p-6 rounded-2xl border border-slate-800 bg-[#090f1c]/20 hover:bg-[#090f1c]/50 transition-all group flex items-center justify-between gap-6"
        >
          <div className="space-y-1">
            <h3 className="text-sm font-bold text-white group-hover:text-purple-400 transition-colors flex items-center gap-2">
              <KeyRound size={16} /> Secure Provider Vault (BYOK)
            </h3>
            <p className="text-xs text-zinc-400 font-sans max-w-md">Connect encryption key hashes to supply cross-workspace shared backup billing pipelines.</p>
          </div>
          <ArrowRight size={16} className="text-zinc-600 group-hover:text-purple-400 group-hover:translate-x-1 transition-all shrink-0" />
        </Link>

      </div>

    </div>
  );
}