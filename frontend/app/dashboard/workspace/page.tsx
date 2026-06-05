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
  Cpu,
  Boxes,
  Loader2
} from "lucide-react";
import { getWorkspaceMembers, getCurrentUser, apiKeyApi } from "@/components/api";

export default function WorkspaceOverviewPage() {
  const [loading, setLoading] = useState(true);
  const [membersCount, setMembersCount] = useState(0);
  const [adminCount, setAdminCount] = useState(0);
  const [operatorCount, setOperatorCount] = useState(0);
  const [keyStatus, setKeyStatus] = useState({ connected: false });
  const [workspaceUID, setWorkspaceUID] = useState("");

  useEffect(() => {
    async function loadOverviewStats() {
      try {
        setLoading(true);
        
        // 1. Fetch organizational roster metrics
        const roster = await getWorkspaceMembers();
        if (roster) {
          setMembersCount(roster.length);
          setAdminCount(roster.filter((m: any) => m.role?.toLowerCase() === "admin").length);
          setOperatorCount(roster.filter((m: any) => m.role?.toLowerCase() === "operator").length);
        }

        // 2. Fetch active cluster token connectivity data
        if (typeof window !== "undefined") {
          const storedWorkspaceId = localStorage.getItem("workspace_id");
          if (storedWorkspaceId) {
            setWorkspaceUID(storedWorkspaceId.toUpperCase());
            const kData = await apiKeyApi.getKeyStatus(storedWorkspaceId);
            setKeyStatus(kData);
          }
        }
      } catch (err) {
        console.error("Failed to compile dashboard workspace summary view:", err);
      } finally {
        setLoading(false);
      }
    }

    loadOverviewStats();
  }, []);

  if (loading) {
    return (
      <div className="h-[60vh] w-full flex items-center justify-center gap-2 font-mono text-xs text-cyan-400">
        <Loader2 className="animate-spin" size={20} />
        <span>COMPILING PERIMETER TELEMETRY...</span>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fadeIn">
      
      {/* SECTION 1: WELCOME CONTROL METRIC BANNER */}
      <div className="p-8 rounded-[32px] border border-cyan-500/10 bg-gradient-to-b from-[#071120]/50 to-transparent relative overflow-hidden">
        <div className="absolute top-0 right-0 h-64 w-64 rounded-full bg-cyan-500/5 blur-3xl pointer-events-none" />
        
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-cyan-500/20 bg-cyan-500/5 text-[10px] font-mono text-cyan-400 tracking-wider">
            <Activity size={12} className="animate-pulse" /> SYSTEM RUNTIME CONTROL CENTER
          </div>
          <h1 className="text-4xl font-black tracking-tight text-white font-sans">
            Workspace Hub
          </h1>
          <p className="text-zinc-400 text-sm font-sans max-w-2xl leading-relaxed">
            Perimeter ID: <span className="font-mono text-cyan-300 text-xs bg-slate-950 px-2 py-0.5 rounded border border-slate-900">{workspaceUID || "AP-CORE-NODE"}</span>. Monitor cluster variables, team allocations, and structural API configurations.
          </p>
        </div>
      </div>

      {/* SECTION 2: METRIC TELEMETRY COUNTERS */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        
        {/* CARD 1: OVERALL TEAM STRENGTH */}
        <div className="p-6 rounded-2xl bg-black/40 border border-slate-900 flex items-center justify-between transition-all hover:border-slate-800">
          <div className="space-y-1">
            <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-wider">Allocated Profiles</span>
            <div className="text-3xl font-black text-white">{membersCount}</div>
            <div className="text-[11px] font-sans text-zinc-400">Total Active Users</div>
          </div>
          <div className="h-12 w-12 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
            <Users size={22} />
          </div>
        </div>

        {/* CARD 2: TOTAL ACTIVE ADMINISTRATORS */}
        <div className="p-6 rounded-2xl bg-black/40 border border-slate-900 flex items-center justify-between transition-all hover:border-slate-800">
          <div className="space-y-1">
            <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-wider">Governance Nodes</span>
            <div className="text-3xl font-black text-white">{adminCount}</div>
            <div className="text-[11px] font-sans text-zinc-400">Workspace Admins</div>
          </div>
          <div className="h-12 w-12 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
            <ShieldCheck size={22} />
          </div>
        </div>

        {/* CARD 3: SHARED GATEWAY KEY CONNECTIVITY BADGE */}
        <div className="p-6 rounded-2xl bg-black/40 border border-slate-900 flex items-center justify-between transition-all hover:border-slate-800">
          <div className="space-y-1">
            <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-wider">Infrastructure Backup</span>
            <div className="pt-1">
              {keyStatus.connected ? (
                <span className="text-green-400 font-mono font-bold bg-green-500/10 border border-green-500/20 px-2.5 py-1 rounded text-xs tracking-wide uppercase">ACTIVE</span>
              ) : (
                <span className="text-zinc-500 font-mono font-bold bg-zinc-900 border border-zinc-800 px-2.5 py-1 rounded text-xs tracking-wide uppercase">OFFLINE</span>
              )}
            </div>
            <div className="text-[11px] font-sans text-zinc-400 pt-1">Google Gemini Fallback</div>
          </div>
          <div className={`h-12 w-12 rounded-xl flex items-center justify-center border ${
            keyStatus.connected 
              ? "bg-green-500/10 border-green-500/20 text-green-400" 
              : "bg-zinc-900 border-zinc-800 text-zinc-500"
          }`}>
            <KeyRound size={22} />
          </div>
        </div>

      </div>

      {/* SECTION 3: NAVIGATION HUB QUICK-LINKS GRID */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* LINK CARD 1: TEAM PERIMETER CONTROL */}
        <Link 
          href="/dashboard/workspace/members"
          className="p-6 rounded-[24px] border border-slate-900 bg-[#071120]/20 hover:bg-[#071120]/40 transition-all hover:border-cyan-500/20 group flex flex-col justify-between h-48"
        >
          <div className="space-y-2">
            <div className="h-10 w-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
              <Boxes size={18} />
            </div>
            <h3 className="text-lg font-bold text-white group-hover:text-cyan-300 transition-colors">Manage Team & Roles</h3>
            <p className="text-xs text-zinc-400 font-sans leading-relaxed">
              Invite development engineers, allocate engine permissions, and modify structural clearance matrices.
            </p>
          </div>
          <div className="flex items-center gap-1.5 text-xs font-mono text-cyan-400 font-bold self-end group-hover:gap-2.5 transition-all">
            <span>ACCESS TEAM PANEL</span>
            <ArrowRight size={14} />
          </div>
        </Link>

        {/* LINK CARD 2: SECURE VAULT ENVIRONMENT VARIABLES */}
        <Link 
          href="/dashboard/workspace/providers"
          className="p-6 rounded-[24px] border border-slate-900 bg-[#071120]/20 hover:bg-[#071120]/40 transition-all hover:border-cyan-500/20 group flex flex-col justify-between h-48"
        >
          <div className="space-y-2">
            <div className="h-10 w-10 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
              <Cpu size={18} />
            </div>
            <h3 className="text-lg font-bold text-white group-hover:text-purple-300 transition-colors">API Vault Infrastructure</h3>
            <p className="text-xs text-zinc-400 font-sans leading-relaxed">
              Securely inject cryptographically locked provider keys to fuel background agent pipelines.
            </p>
          </div>
          <div className="flex items-center gap-1.5 text-xs font-mono text-purple-400 font-bold self-end group-hover:gap-2.5 transition-all">
            <span>ACCESS API VAULT</span>
            <ArrowRight size={14} />
          </div>
        </Link>

      </div>

    </div>
  );
}