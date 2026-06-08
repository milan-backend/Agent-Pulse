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
  Cpu,
  FileCode2 // Imported for the RAG Knowledge Base card icon styling
} from "lucide-react";
import { getWorkspaceMembers, apiKeyApi } from "@/components/api";

export default function WorkspaceOverviewPage() {
  const [loading, setLoading] = useState(true);
  const [membersCount, setMembersCount] = useState(0);
  const [adminCount, setAdminCount] = useState(0);
  
  // Dynamic states tracking connected keys & defaults
  const [geminiActive, setGeminiActive] = useState(false);
  const [openaiActive, setOpenaiActive] = useState(false);
  const [geminiDefault, setGeminiDefault] = useState(false);
  const [openaiDefault, setOpenaiDefault] = useState(false);

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
            // Check both provider states and pull their specific default boolean tags
            const gRes = await apiKeyApi.getKeyStatus(storedWorkspaceId, "GEMINI_API_KEY");
            const oRes = await apiKeyApi.getKeyStatus(storedWorkspaceId, "OPENAI_API_KEY");
            
            setGeminiActive(!!gRes?.connected);
            setGeminiDefault(!!gRes?.is_default);

            setOpenaiActive(!!oRes?.connected);
            setOpenaiDefault(!!oRes?.is_default);
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

  const isAnyConnected = geminiActive || openaiActive;

  return (
    <div className="w-full space-y-6 animate-fadeIn">
      
      {/* METRICS GRID */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full">
        
        {/* MEMBERS CARD */}
        <div className="p-8 rounded-2xl bg-[#090f1c]/40 border border-slate-800/80 flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest block font-bold">Active Workspace Roster</span>
            <div className="text-4xl font-black text-white font-sans">{membersCount}</div>
            <div className="text-xs text-zinc-400">Teammates Invited</div>
          </div>
          <div className="h-12 w-12 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
            <Users size={22} />
          </div>
        </div>

        {/* GOVERNANCE CARD */}
        <div className="p-8 rounded-2xl bg-[#090f1c]/40 border border-slate-800/80 flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest block font-bold">Governance Administrators</span>
            <div className="text-4xl font-black text-white font-sans">{adminCount}</div>
            <div className="text-xs text-zinc-400">Root Account Managers</div>
          </div>
          <div className="h-12 w-12 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
            <ShieldCheck size={22} />
          </div>
        </div>

        {/* PROVIDER CONNECTIVITY CARD */}
        <div className="p-8 rounded-2xl bg-[#090f1c]/40 border border-slate-800/80 flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest block font-bold">Provider Connectivity</span>
            <div className="pt-1.5 pb-1">
              {isAnyConnected ? (
                <span className="text-green-400 font-mono font-bold bg-green-500/10 border border-green-500/20 px-3 py-1 rounded text-xs tracking-wider uppercase">CONNECTED</span>
              ) : (
                <span className="text-zinc-500 font-mono font-bold bg-zinc-900 border border-zinc-800 px-3 py-1 rounded text-xs tracking-wider uppercase">OFFLINE</span>
              )}
            </div>
            
            {/* DYNAMIC DEFAULT ROUTING STATUS TEXT */}
            <div className="text-xs text-zinc-400 pt-0.5 font-sans">
              {geminiActive && openaiActive ? (
                openaiDefault ? (
                  <span className="text-purple-400 font-semibold">OpenAI (Primary Default Active)</span>
                ) : geminiDefault ? (
                  <span className="text-cyan-400 font-semibold">Gemini (Primary Default Active)</span>
                ) : (
                  <span className="text-purple-400 font-semibold">OpenAI Core (System Fallback)</span>
                )
              ) : openaiActive ? (
                <span className="text-purple-400 font-semibold">OpenAI Infrastructure Core</span>
              ) : geminiActive ? (
                <span className="text-cyan-400 font-semibold">Google Gemini Fallback Core</span>
              ) : (
                "No Active Providers Connected"
              )}
            </div>
          </div>
          <div className={`h-12 w-12 rounded-xl flex items-center justify-center border ${
            isAnyConnected ? "bg-green-500/10 border-green-500/20 text-green-400" : "bg-zinc-900 border-zinc-800 text-zinc-500"
          }`}>
            <KeyRound size={22} />
          </div>
        </div>

      </div>

      {/* FOOTER ACTIONS ROW - GRID CHANGED TO grid-cols-1 md:grid-cols-3 FOR THE NEW CARD */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full">
        
        {/* TEAM CLEARANCE CONFIGURATOR */}
        <Link href="/dashboard/workspace/members" className="p-8 rounded-2xl border border-slate-800/80 bg-[#090f1c]/20 hover:bg-[#090f1c]/50 transition-all hover:border-cyan-500/20 group flex flex-col justify-between h-48 relative">
          <div className="space-y-1.5">
            <h3 className="text-lg font-bold text-white group-hover:text-cyan-400 transition-colors flex items-center gap-2">
              <Boxes size={18} className="text-cyan-400" /> 
              Control Team Clearances
            </h3>
            <p className="text-xs text-zinc-400 font-sans leading-relaxed">
              Dispatch encrypted invitations, evict operational accounts dynamically, and evaluate inline permissions matrix tags natively.
            </p>
          </div>
          <div className="flex justify-end w-full">
            <ArrowRight size={18} className="text-zinc-600 group-hover:text-cyan-400 group-hover:translate-x-1.5 transition-all" />
          </div>
        </Link>

        {/* PROVIDER KEY STORAGE VAULT */}
        <Link href="/dashboard/workspace/providers" className="p-8 rounded-2xl border border-slate-800/80 bg-[#090f1c]/20 hover:bg-[#090f1c]/50 transition-all hover:border-purple-500/20 group flex flex-col justify-between h-48 relative">
          <div className="space-y-1.5">
            <h3 className="text-lg font-bold text-white group-hover:text-purple-400 transition-colors flex items-center gap-2">
              <Cpu size={18} className="text-purple-400" /> 
              Configure Provider Vault
            </h3>
            <p className="text-xs text-zinc-400 font-sans leading-relaxed">
              Inject multi-tenant infrastructure key tokens (BYOK) safely into background server parameters without data cross-leak hazards.
            </p>
          </div>
          <div className="flex justify-end w-full">
            <ArrowRight size={18} className="text-zinc-600 group-hover:text-purple-400 group-hover:translate-x-1.5 transition-all" />
          </div>
        </Link>

        {/* NEW: RAG DATA KNOWLEDGE BASE ACCELERATOR PANEL CARD */}
        <Link href="/dashboard/workspace/knowledge" className="p-8 rounded-2xl border border-slate-800/80 bg-[#090f1c]/20 hover:bg-[#090f1c]/50 transition-all hover:border-emerald-500/20 group flex flex-col justify-between h-48 relative">
          <div className="space-y-1.5">
            <h3 className="text-lg font-bold text-white group-hover:text-emerald-400 transition-colors flex items-center gap-2">
              <FileCode2 size={18} className="text-emerald-400" /> 
              RAG Knowledge Base
            </h3>
            <p className="text-xs text-zinc-400 font-sans leading-relaxed">
              Ingest plain text or raw multi-page PDF documents securely into our decoupled, two-tier isolated vector storage boundaries.
            </p>
          </div>
          <div className="flex justify-end w-full">
            <ArrowRight size={18} className="text-zinc-600 group-hover:text-emerald-400 group-hover:translate-x-1.5 transition-all" />
          </div>
        </Link>

      </div>

    </div>
  );
}