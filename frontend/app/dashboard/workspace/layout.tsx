"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { 
  Users, 
  KeyRound, 
  ArrowLeft, 
  Layers, 
  ShieldAlert,
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
  const router = useRouter();
  
  const [loading, setLoading] = useState(true);
  const [userRole, setUserRole] = useState<"admin" | "operator" | "viewer">("viewer");
  const [workspaceName, setWorkspaceName] = useState("Loading Workspace...");

  useEffect(() => {
    async function verifyAccessRole() {
      try {
        setLoading(true);
        
        // 1. Fetch current logged-in identity
        const user = await getCurrentUser();
        const userEmail = user?.email;

        // 2. Fetch the active workspace roster profiles
        const roster = await getWorkspaceMembers();
        
        // 3. Find match to compute precise RBAC clearance tier
        if (userEmail && roster) {
          const match = roster.find(
            (m: any) => m.user_email === userEmail || m.email === userEmail
          );
          if (match?.role) {
            setUserRole(match.role.toLowerCase() as "admin" | "operator" | "viewer");
          }
        }

        // Extract raw active workspace text context from browser environment storage
        if (typeof window !== "undefined") {
          const storedWorkspaceId = localStorage.getItem("workspace_id");
          if (storedWorkspaceId) {
            setWorkspaceName(`AP-${storedWorkspaceId.substring(0, 6).toUpperCase()}`);
          } else {
            setWorkspaceName("Agent-Pulse Core");
          }
        }

      } catch (err) {
        console.error("Failed to authenticate workspace layout context metrics:", err);
      } finally {
        setLoading(false);
      }
    }

    verifyAccessRole();
  }, [pathname]);

  if (loading) {
    return (
      <div className="min-h-[70vh] w-full flex flex-col items-center justify-center gap-3 font-mono text-xs text-cyan-400">
        <Loader2 className="animate-spin text-cyan-400" size={32} />
        <span>DECRYPTING SECURE WORKSPACE HUB...</span>
      </div>
    );
  }

  return (
    <div className="w-full min-h-screen bg-[#020817] text-white flex flex-col xl:flex-row gap-8 p-1 sm:p-4">
      
      {/* INTERNAL CONTEXT SUB-SIDEBAR */}
      <div className="w-full xl:w-72 shrink-0 rounded-[24px] border border-cyan-500/10 bg-[#071120]/60 backdrop-blur-md p-6 flex flex-col justify-between relative overflow-hidden h-fit xl:sticky xl:top-24">
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-cyan-500/30 to-transparent" />
        
        <div className="space-y-6">
          {/* BACK ACTION CONTROL */}
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 text-xs font-mono text-zinc-500 hover:text-cyan-400 transition-colors group"
          >
            <ArrowLeft size={14} className="group-hover:-translate-x-1 transition-transform" />
            <span>RETURN TO RUNTIME</span>
          </Link>

          {/* WORKSPACE METRICS IDENTITY TAG */}
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-xs font-mono text-cyan-400/70 uppercase tracking-widest">
              <Layers size={12} />
              <span>Active Multi-Tenant Context</span>
            </div>
            <h2 className="text-2xl font-black tracking-tight text-white truncate">
              {workspaceName}
            </h2>
          </div>

          <hr className="border-slate-800/60" />

          {/* SUB-NAVIGATION MATRIX LINKS */}
          <nav className="flex flex-col gap-2">
            
            {/* LINK 1: UNIFIED TEAM CONTROLLER */}
            <Link
              href="/dashboard/workspace/members"
              className={`w-full flex items-center justify-between px-4 py-3.5 rounded-xl font-sans text-sm font-bold transition-all border ${
                pathname === "/dashboard/workspace/members"
                  ? "bg-cyan-500/10 border-cyan-500/30 text-cyan-300 shadow-[0_0_15px_rgba(6,182,212,0.05)]"
                  : "bg-transparent border-transparent text-zinc-400 hover:text-zinc-200 hover:bg-slate-900/40"
              }`}
            >
              <div className="flex items-center gap-3">
                <Users size={18} className={pathname === "/dashboard/workspace/members" ? "text-cyan-300" : "text-zinc-500"} />
                <span>Team Members</span>
              </div>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-950 text-zinc-500 border border-slate-800/40">OPEN</span>
            </Link>

            {/* LINK 2: VAULT API MODEL PARAMETERS (CRITICAL ENFORCEMENT: HIDDEN FROM OPERATORS/VIEWERS) */}
            {userRole === "admin" ? (
              <Link
                href="/dashboard/workspace/providers"
                className={`w-full flex items-center justify-between px-4 py-3.5 rounded-xl font-sans text-sm font-bold transition-all border ${
                  pathname === "/dashboard/workspace/providers"
                    ? "bg-cyan-500/10 border-cyan-500/30 text-cyan-300 shadow-[0_0_15px_rgba(6,182,212,0.05)]"
                    : "bg-transparent border-transparent text-zinc-400 hover:text-zinc-200 hover:bg-slate-900/40"
                }`}
              >
                <div className="flex items-center gap-3">
                  <KeyRound size={18} className={pathname === "/dashboard/workspace/providers" ? "text-cyan-300" : "text-zinc-500"} />
                  <span>API Providers</span>
                </div>
                <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-cyan-950 border border-cyan-500/20 text-cyan-400 font-extrabold tracking-wider">VAULT</span>
              </Link>
            ) : (
              /* Using LockIcon alias safely right here to completely clear the TS check error */
              <div className="w-full flex items-center justify-between px-4 py-3.5 rounded-xl text-zinc-600 font-sans text-sm font-bold select-none border border-transparent opacity-40">
                <div className="flex items-center gap-3">
                  <LockIcon size={18} className="text-zinc-600" />
                  <span className="line-through">API Providers</span>
                </div>
                <ShieldAlert size={14} className="text-zinc-600" />
              </div>
            )}

          </nav>
        </div>

        {/* BOTTOM METADATA BADGE */}
        <div className="mt-8 pt-4 border-t border-slate-900 flex items-center justify-between font-mono text-[10px] text-zinc-500">
          <span>CLEARANCE TIER:</span>
          <span className="text-cyan-400 uppercase font-bold tracking-wider">{userRole}</span>
        </div>
      </div>

      {/* CORE DISPLAY PORT DISPLAY INTERFACE ELEMENT */}
      <div className="flex-1 min-w-0">
        {children}
      </div>

    </div>
  );
}