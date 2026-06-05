"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  Users, 
  KeyRound, 
  ArrowLeft, 
  Layers, 
  Loader2,
  Lock as LockIcon
} from "lucide-react";
import { getCurrentUser, getWorkspaceMembers } from "@/components/api";

export default function WorkspaceLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  
  const [loading, setLoading] = useState(true);
  const [userRole, setUserRole] = useState<"admin" | "operator" | "viewer">("viewer");
  const [workspaceName, setWorkspaceName] = useState("Loading Workspace...");

  // Compute dynamic page title based on the active tab route string
  const getPageTitle = () => {
    if (pathname.includes("/members")) return "Workspace Members";
    if (pathname.includes("/providers")) return "API Providers Infrastructure";
    return "Workspace Overview";
  };

  const getPageDescription = () => {
    if (pathname.includes("/members")) return "Manage active user credentials, allocate team clearances, and inspect role parameters.";
    if (pathname.includes("/providers")) return "Configure secure workspace-level model keys for autonomous pipeline workloads.";
    return "Central telemetry command center for your operational workspace node cluster.";
  };

  useEffect(() => {
    async function verifyAccessRole() {
      try {
        setLoading(true);
        const user = await getCurrentUser();
        const userEmail = user?.email;
        const roster = await getWorkspaceMembers();
        
        if (userEmail && roster) {
          const match = roster.find(
            (m: any) => m.user_email === userEmail || m.email === userEmail
          );
          if (match?.role) {
            setUserRole(match.role.toLowerCase() as "admin" | "operator" | "viewer");
          }
        }

        if (typeof window !== "undefined") {
          const storedWorkspaceId = localStorage.getItem("workspace_id");
          if (storedWorkspaceId) {
            setWorkspaceName(`AP-${storedWorkspaceId.substring(0, 6).toUpperCase()}`);
          } else {
            setWorkspaceName("Agent-Pulse Core");
          }
        }
      } catch (err) {
        console.error("Layout initialization tracking failure:", err);
      } finally {
        setLoading(false);
      }
    }
    verifyAccessRole();
  }, [pathname]);

  if (loading) {
    return (
      <div className="min-h-[60vh] w-full flex flex-col items-center justify-center gap-3 font-mono text-xs text-cyan-400">
        <Loader2 className="animate-spin text-cyan-400" size={28} />
        <span>AUTHENTICATING CORE WORKSPACE ACCESS MAPS...</span>
      </div>
    );
  }

  return (
    <div className="w-full min-h-screen bg-[#020817] text-white p-4 sm:p-8 space-y-8 max-w-7xl mx-auto">
      
      {/* MASSIVE HORIZONTAL TOP HEADER ROW */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-800 pb-6 relative">
        <div className="space-y-2">
          <div className="flex items-center gap-2 font-mono text-[10px] tracking-widest text-zinc-500 uppercase">
            <Layers size={12} className="text-cyan-400" />
            <span>Multi-Tenant Node: {workspaceName}</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-black tracking-tight text-white font-sans">
            {getPageTitle()}
          </h1>
          <p className="text-sm text-zinc-400 max-w-3xl font-sans">
            {getPageDescription()}
          </p>
        </div>

        {/* BACK TO RUNTIME ACTION LINK */}
        <Link
          href="/dashboard"
          className="inline-flex items-center gap-2 text-xs font-mono text-zinc-500 hover:text-cyan-400 transition-colors group sm:self-start mt-2"
        >
          <ArrowLeft size={14} className="group-hover:-translate-x-1 transition-transform" />
          <span>RETURN TO DASHBOARD</span>
        </Link>
      </div>

      {/* HORIZONTAL CONTROLS TAB NAVIGATION ROW */}
      <div className="flex items-center justify-between border-b border-slate-900/60 pb-1 flex-wrap gap-4 font-sans">
        <div className="flex items-center gap-2">
          
          {/* TAB 1: OVERVIEW HUB LINK */}
          <Link
            href="/dashboard/workspace"
            className={`px-5 py-3 rounded-xl text-xs font-bold uppercase tracking-wider transition-all border ${
              pathname === "/dashboard/workspace"
                ? "bg-cyan-500/10 border-cyan-500/20 text-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.03)]"
                : "bg-transparent border-transparent text-zinc-500 hover:text-zinc-300"
            }`}
          >
            Overview
          </Link>

          {/* TAB 2: TEAM ROSTER CONTROLLER */}
          <Link
            href="/dashboard/workspace/members"
            className={`px-5 py-3 rounded-xl text-xs font-bold uppercase tracking-wider transition-all border flex items-center gap-2 ${
              pathname === "/dashboard/workspace/members"
                ? "bg-cyan-500/10 border-cyan-500/20 text-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.03)]"
                : "bg-transparent border-transparent text-zinc-500 hover:text-zinc-300"
            }`}
          >
            <Users size={14} />
            <span>Members</span>
          </Link>

          {/* TAB 3: API PROVIDERS CONFIGURATION (CONDITIONAL HIDING FROM NON-ADMINS) */}
          {userRole === "admin" ? (
            <Link
              href="/dashboard/workspace/providers"
              className={`px-5 py-3 rounded-xl text-xs font-bold uppercase tracking-wider transition-all border flex items-center gap-2 ${
                pathname === "/dashboard/workspace/providers"
                  ? "bg-cyan-500/10 border-cyan-500/20 text-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.03)]"
                  : "bg-transparent border-transparent text-zinc-500 hover:text-zinc-300"
              }`}
            >
              <KeyRound size={14} />
              <span>API Providers</span>
            </Link>
          ) : (
            <div className="px-5 py-3 text-xs font-bold uppercase tracking-wider text-zinc-700 select-none flex items-center gap-2 opacity-40 cursor-not-allowed">
              <LockIcon size={14} className="text-zinc-700" />
              <span className="line-through">API Providers</span>
            </div>
          )}
        </div>

        {/* COMPACT METADATA FOOTNOTE */}
        <div className="font-mono text-[11px] text-zinc-500 bg-slate-950 px-3 py-1.5 rounded-lg border border-slate-900">
          CLEARANCE CREDENTIALS: <span className="text-cyan-400 uppercase font-black">{userRole}</span>
        </div>
      </div>

      {/* FULL WIDTH DYNAMIC CANVAS SLOT */}
      <div className="w-full pt-2 animate-fadeIn">
        {children}
      </div>

    </div>
  );
}