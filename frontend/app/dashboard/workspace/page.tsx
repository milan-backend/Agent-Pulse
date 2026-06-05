"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { 
  Users, 
  ShieldCheck, 
  KeyRound, 
  ArrowRight, 
  Loader2,
  Boxes,
  Cpu
} from "lucide-react";
import { getWorkspaceMembers, apiKeyApi } from "@/components/api";

export default function WorkspaceOverviewPage() {
  const [loading, setLoading] = useState(true);
  const [membersCount, setMembersCount] = useState(0);
  const [adminCount, setAdminCount] = useState(0);
  const [keyStatus, setKeyStatus] = useState({ connected: false });

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
            const kData = await apiKeyApi.getKeyStatus(storedWorkspaceId);
            setKeyStatus(kData);
          }
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadOverviewStats();
  }, []);

  if (loading) {
    return (
      <div className="h-[40vh] w-full flex items-center justify-center gap-2 font-mono text-xs text-cyan-400">
        <Loader2 className="animate-spin" size={20} />
        <span>COMPILING GRID METRICS...</span>
      </div>
    );
  }

  return (
    <div className="w-full space-y-6 animate-fadeIn">
      
      {/* 2X2 LUXURIOUS INTEGRATION & telemetry GRID */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full">
        
        {/* STAT 1 */}
        <div className="p-8 rounded-2xl bg-[#090f1c]/40 border border-slate-800/80 flex items-center justify-between transition-colors hover:border-slate-800">
          <div className="space-y-1">
            <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest block font-bold">Active Workspace Roster</span>
            <div className="text-4xl font-black text-white font-sans">{membersCount}</div>
            <div className="text-xs text-zinc-400">Teammates Invited</div>
          </div>
          <div className="h-12 w-12 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
            <Users size={22} />
          </div>
        </div>

        {/* STAT 2 */}
        <div className="p-8 rounded-2xl bg-[#090f1c]/40 border border-slate-800/80 flex items-center justify-between transition-colors hover:border-slate-800">
          <div className="space-y-1">
            <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest block font-bold">Governance Administrators</span>
            <div className="text-4xl font-black text-white font-sans">{adminCount}</div>
            <div className="text-xs text-zinc-400">Root Account Managers</div>
          </div>
          <div className="h-12 w-12 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
            <ShieldCheck size={22} />
          </div>
        </div>

        {/* STAT 3 */}
        <div className="p-8 rounded-2xl bg-[#090f1c]/40 border border-slate-800/80 flex items-center justify-between transition-colors hover:border-slate-800">
          <div className="space-y-1">
            <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest block font-bold">Provider Connectivity</span>
            <div className="pt-1.5 pb-1">
              {keyStatus.connected ? (
                <span className="text-green-400 font-mono font-bold bg-green-500/10 border border-green-500/20 px-3 py-1 rounded text-xs tracking-wider uppercase">CONNECTED</span>
              ) : (
                <span className="text-zinc-500 font-mono font-bold bg-zinc-900 border border-zinc-800 px-3 py-1 rounded text-xs tracking-wider uppercase">NOT CONNECTED</span>
              )}
            </div>
            <div className="text-xs text-zinc-400 pt-0.5">Google Gemini Fallback Core</div>
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

      {/* FULL WIDTH QUICK NAV TUNNEL LAYOUT CARDS */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full">
        
        {/* NAV 1 */}
        <Link 
          href="/dashboard/workspace/members"
          className="p-8 rounded-2xl border border-slate-800/80 bg-[#090f1c]/20 hover:bg-[#090f1c]/50 transition-all hover:border-cyan-500/20 group flex items-center justify-between gap-6"
        >
          <div className="space-y-1.5">
            <h3 className="text-lg font-bold text-white group-hover:text-cyan-400 transition-colors flex items-center gap-2">
              <Boxes size={18} className="text-cyan-400" /> Control Team Profiles & Clearances
            </h3>
            <p className="text-xs text-zinc-400 font-sans max-w-xl leading-relaxed">
              Dispatch encrypted invitations, evict operational accounts dynamically, and evaluate inline permissions matrix tags natively.
            </p>
          </div>
          <ArrowRight size={18} className="text-zinc-600 group-hover:text-cyan-400 group-hover:translate-x-1.5 transition-all shrink-0" />
        </Link>

        {/* NAV 2 */}
        <Link 
          href="/dashboard/workspace/providers"
          className="p-8 rounded-2xl border border-slate-800/80 bg-[#090f1c]/20 hover:bg-[#090f1c]/50 transition-all hover:border-purple-500/20 group flex items-center justify-between gap-6"
        >
          <div className="space-y-1.5">
            <h3 className="text-lg font-bold text-white group-hover:text-purple-400 transition-colors flex items-center gap-2">
              <Cpu size={18} className="text-purple-400" /> Configure API Provider Vault
            </h3>
            <p className="text-xs text-zinc-400 font-sans max-w-xl leading-relaxed">
              Inject multi-tenant infrastructure key tokens (BYOK) safely into background server parameters without data cross-leak hazards.
            </p>
          </div>
          <ArrowRight size={18} className="text-zinc-600 group-hover:text-purple-400 group-hover:translate-x-1.5 transition-all shrink-0" />
        </Link>

      </div>

    </div>
  );
}