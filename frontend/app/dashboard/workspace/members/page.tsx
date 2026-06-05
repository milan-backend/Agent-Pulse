"use client";

import { useState, useEffect } from "react";
import { 
  Users, 
  Mail, 
  ShieldCheck, 
  Trash2, 
  UserPlus, 
  Lock, 
  Shield, 
  Eye, 
  Crown, 
  Loader2,
  CheckCircle2,
  Sparkles
} from "lucide-react";
import { 
  getWorkspaceMembers, 
  createWorkspaceMember, 
  updateWorkspaceMemberRole, 
  deleteWorkspaceMember, 
  getCurrentUser 
} from "@/components/api";
import { toast } from "sonner";

interface WorkspaceMember {
  user_id: string;
  email: string;
  name: string;
  role: string;
}

export default function WorkspaceMembersPage() {
  const [members, setMembers] = useState<WorkspaceMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("viewer");
  const [adding, setAdding] = useState(false);
  const [updatingRole, setUpdatingRole] = useState<string | null>(null);
  const [removing, setRemoving] = useState<string | null>(null);

  const [currentUserEmail, setCurrentUserEmail] = useState("");
  const [currentUserRole, setCurrentUserRole] = useState<"admin" | "operator" | "viewer">("viewer");

  useEffect(() => {
    async function initializePageContext() {
      try {
        const me = await getCurrentUser();
        setCurrentUserEmail(me.email);
      } catch (err) {
        console.error(err);
      } finally {
        await loadMembers();
      }
    }
    initializePageContext();
  }, [currentUserEmail]);

  async function loadMembers() {
    try {
      setLoading(true);
      const data = await getWorkspaceMembers();
      setMembers(data || []);

      if (currentUserEmail && data) {
        const match = data.find((m: any) => m.user_email === currentUserEmail || m.email === currentUserEmail);
        if (match?.role) {
          setCurrentUserRole(match.role.toLowerCase() as any);
        }
      }
    } catch (error) {
      console.error(error);
      toast.error("Failed to sync workspace roster parameters");
    } finally {
      setLoading(false);
    }
  }

  async function addMember() {
    if (!email.trim()) {
      toast.error("Email string identifier required");
      return;
    }
    try {
      setAdding(true);
      const response = await createWorkspaceMember({ email: email.trim(), role });
      toast.success(response?.message || "Workspace member added successfully");
      setEmail("");
      setRole("viewer");
      await loadMembers();
    } catch (error: any) {
      toast.error(error?.message || "Failed to add user context");
    } finally {
      setAdding(false);
    }
  }

  async function handleRoleUpdate(memberEmail: string, newRole: string) {
    try {
      setUpdatingRole(memberEmail);
      const response = await updateWorkspaceMemberRole(memberEmail, newRole);
      toast.success(response?.message || "Clearance matrix updated");
      await loadMembers();
    } catch (error: any) {
      toast.error(error?.message || "Failed to modify role context");
    } finally {
      setUpdatingRole(null);
    }
  }

  async function removeMember(userId: string) {
    if (!window.confirm("Evict this membership reference from the secure workspace?")) return;
    try {
      setRemoving(userId);
      const response = await deleteWorkspaceMember(userId);
      toast.success(response?.message || "Workspace member evicted successfully");
      await loadMembers();
    } catch (error: any) {
      toast.error(error?.message || "Failed to clear member record");
    } finally {
      setRemoving(null);
    }
  }

  if (loading && members.length === 0) {
    return (
      <div className="h-[60vh] w-full flex flex-col items-center justify-center gap-4 font-mono text-xs text-cyan-400 tracking-widest">
        <Loader2 className="animate-spin text-cyan-400" size={32} />
        <span className="animate-pulse">DECRYPTING SECURE ROSTER METRICS...</span>
      </div>
    );
  }

  const isUserAdmin = currentUserRole === "admin";
  const isUserViewer = currentUserRole === "viewer";

  return (
    <div className="space-y-12 max-w-6xl mx-auto px-2 pb-16 animate-fadeIn">
      
      {/* ==================================================== */}
      {/* 1. ROLE PRIVILEGES SUMMARY CONSOLE                  */}
      {/* ==================================================== */}
      <div className="space-y-4">
        <div className="flex items-center gap-2 text-xs font-mono tracking-widest text-zinc-500 uppercase">
          <Sparkles size={14} className="text-cyan-400" />
          <span>Security & Governance Framework</span>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* ADMIN CARD */}
          <div className="p-6 rounded-[24px] border border-cyan-500/10 bg-gradient-to-b from-[#071120]/60 to-transparent backdrop-blur-md flex flex-col justify-between h-48 transition-all hover:border-cyan-500/20">
            <div className="flex items-center gap-3 text-cyan-400">
              <Crown size={20} />
              <h3 className="font-sans font-black tracking-wide text-base text-white">Workspace Admin</h3>
            </div>
            <p className="text-zinc-400 text-xs font-sans leading-relaxed mt-2 flex-1">
              Full governance authority over the environment. Managed API vault connections, billing variables, and explicit operational hierarchies.
            </p>
            <div className="mt-3 text-[10px] font-mono text-cyan-400 bg-cyan-500/5 border border-cyan-500/10 px-2.5 py-1 rounded-lg w-fit font-bold">
              ROOT PRIVILEGES
            </div>
          </div>

          {/* OPERATOR CARD */}
          <div className="p-6 rounded-[24px] border border-amber-500/10 bg-gradient-to-b from-[#141009]/40 to-transparent backdrop-blur-md flex flex-col justify-between h-48 transition-all hover:border-amber-500/20">
            <div className="flex items-center gap-3 text-amber-400">
              <ShieldCheck size={20} />
              <h3 className="font-sans font-black tracking-wide text-base text-white">Engine Operator</h3>
            </div>
            <p className="text-zinc-400 text-xs font-sans leading-relaxed mt-2 flex-1">
              Runtime controls execution path. Spawns pipeline clusters, invites additional staff profiles, and watches tracking feeds. API secrets remain write-only hidden.
            </p>
            <div className="mt-3 text-[10px] font-mono text-amber-400 bg-amber-500/5 border border-amber-500/10 px-2.5 py-1 rounded-lg w-fit font-bold">
              EXECUTION CLEARANCE
            </div>
          </div>

          {/* VIEWER CARD */}
          <div className="p-6 rounded-[24px] border border-slate-800 bg-gradient-to-b from-slate-950/40 to-transparent backdrop-blur-md flex flex-col justify-between h-48 transition-all hover:border-slate-700">
            <div className="flex items-center gap-3 text-zinc-400">
              <Eye size={20} />
              <h3 className="font-sans font-black tracking-wide text-base text-white">Roster Viewer</h3>
            </div>
            <p className="text-zinc-400 text-xs font-sans leading-relaxed mt-2 flex-1">
              Auditing rights over cluster status graphs. Monitors metric metrics and reviews runtime histories. System settings changes are completely frozen.
            </p>
            <div className="mt-3 text-[10px] font-mono text-zinc-400 bg-slate-900 border border-slate-800 px-2.5 py-1 rounded-lg w-fit font-bold">
              READ-ONLY PERMIT
            </div>
          </div>
        </div>
      </div>

      {/* ==================================================== */}
      {/* 2. EXPANSIVE COLLABORATOR INJECTION CONSOLE          */}
      {/* ==================================================== */}
      <div className="rounded-[32px] border border-cyan-500/10 bg-gradient-to-b from-[#040c18] to-[#020817] p-8 md:p-10 space-y-6 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none" />
        
        <div className="flex items-center gap-4 border-b border-slate-900 pb-5">
          <div className="h-12 w-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
            <UserPlus size={24} />
          </div>
          <div>
            <h2 className="text-2xl font-black text-white font-sans tracking-tight">Deploy New Collaborator</h2>
            <p className="text-sm text-zinc-400 font-sans mt-0.5">Authorise alternative account records into this workspace node context.</p>
          </div>
        </div>

        {!isUserViewer ? (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 pt-2">
            
            {/* EMAIL INPUT */}
            <div className="lg:col-span-6 space-y-2">
              <label className="text-xs font-mono text-zinc-400 uppercase tracking-widest block font-bold">Account Email Address</label>
              <div className="relative flex items-center">
                <Mail className="absolute left-5 text-zinc-500" size={18} />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Paste or type collaborator email..."
                  className="w-full bg-black/60 border border-slate-800 rounded-2xl pl-14 pr-5 py-4.5 text-base text-white outline-none focus:border-cyan-500/40 font-mono focus:bg-black transition-all shadow-inner placeholder:text-zinc-600"
                />
              </div>
            </div>

            {/* ROLE SELECT */}
            <div className="lg:col-span-3 space-y-2">
              <label className="text-xs font-mono text-zinc-400 uppercase tracking-widest block font-bold">Assigned Clearance Tier</label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full bg-black/60 border border-slate-800 rounded-2xl px-5 py-4.5 text-sm text-slate-200 outline-none focus:border-cyan-500/40 font-mono focus:bg-black transition-all h-[58px] cursor-pointer font-bold"
              >
                <option value="viewer">Viewer (Read-Only)</option>
                <option value="operator">Operator (Runtime Clearance)</option>
                {isUserAdmin && <option value="admin">Admin (Total Roots)</option>}
              </select>
            </div>

            {/* SUBMIT ACTION BUTTON */}
            <div className="lg:col-span-3 flex items-end">
              <button
                onClick={addMember}
                disabled={adding || !email.trim()}
                className="w-full h-[58px] bg-cyan-400 hover:bg-cyan-300 disabled:hover:bg-cyan-400 text-slate-950 font-sans font-black rounded-2xl transition-all disabled:opacity-30 flex items-center justify-center gap-2 text-sm tracking-wider uppercase shadow-[0_4px_20px_rgba(34,211,238,0.15)] disabled:cursor-not-allowed active:scale-[0.99]"
              >
                {adding ? (
                  <>
                    <Loader2 className="animate-spin text-slate-950" size={18} />
                    <span>INJECTING CREDENTIALS...</span>
                  </>
                ) : (
                  <>
                    <CheckCircle2 size={16} />
                    <span>Deploy Workspace Invitation</span>
                  </>
                )}
              </button>
            </div>

          </div>
        ) : (
          <div className="p-6 rounded-2xl bg-black/40 border border-slate-900 flex items-center gap-3 text-sm text-zinc-500 font-mono">
            <Lock size={16} className="text-zinc-600 shrink-0" /> 
            <span>Roster injection protocols are completely disabled for Viewer nodes. Access restricted.</span>
          </div>
        )}
      </div>

      {/* ==================================================== */}
      {/* 3. ROBUST, FULL-WIDTH TEAM LISTING MATRIX           */}
      {/* ==================================================== */}
      <div className="space-y-6">
        <div className="flex items-center justify-between border-b border-slate-900 pb-4">
          <div className="flex items-center gap-3">
            <Users size={22} className="text-cyan-400" />
            <h2 className="text-2xl font-black text-white font-sans tracking-tight">Active Cluster Roster</h2>
          </div>
          <span className="text-xs font-mono bg-slate-950 border border-slate-800 px-3 py-1 rounded-xl text-zinc-400">
            LOADED ENTITIES: <span className="text-cyan-400 font-bold">{members.length}</span>
          </span>
        </div>

        <div className="space-y-4">
          {members.length === 0 ? (
            <div className="p-16 text-center border-2 border-dashed border-slate-800 rounded-[24px] text-zinc-500 font-mono text-sm tracking-widest bg-black/10">
              CRITICAL WARNING: NO MEMBERS FOUND WITHIN ACTIVE TENANT ENVIRONMENT
            </div>
          ) : (
            members.map((member, idx) => (
              <div 
                key={member.user_id || idx} 
                className="p-6 md:p-8 rounded-[24px] bg-[#071120]/30 border border-slate-900/60 backdrop-blur-sm flex flex-col md:flex-row md:items-center justify-between gap-6 transition-all hover:border-cyan-500/20 hover:bg-[#071120]/50 group"
              >
                {/* User Identity Meta Grid */}
                <div className="space-y-2 flex-1">
                  <div className="text-white font-sans font-black text-lg break-all tracking-tight group-hover:text-cyan-300 transition-colors">
                    {member.email}
                  </div>
                  <div className="flex flex-wrap items-center gap-x-6 gap-y-2 font-mono text-xs text-zinc-500 uppercase tracking-wider">
                    <div className="flex items-center gap-1.5">
                      <Shield size={14} className="text-zinc-600" />
                      <span>Identifier Context:</span>
                      <span className="text-zinc-300 font-sans font-bold normal-case">{member.name || "Awaiting Setup Profile"}</span>
                    </div>
                    <div className="text-[10px] text-zinc-600">
                      ID: <span className="font-mono text-zinc-500">{member.user_id?.substring(0, 8) || "N/A"}...</span>
                    </div>
                  </div>
                </div>

                {/* Operations & Control Selection Gate */}
                <div className="flex items-center gap-4 self-end md:self-auto font-mono text-xs shrink-0">
                  
                  {isUserAdmin && member.email !== currentUserEmail ? (
                    <div className="flex items-center gap-3">
                      <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest font-bold hidden lg:inline block">Modify Tier:</span>
                      <select
                        value={member.role.toLowerCase()}
                        disabled={updatingRole === member.email}
                        onChange={(e) => handleRoleUpdate(member.email, e.target.value)}
                        className="bg-black border border-slate-800 rounded-xl h-12 px-4 text-slate-200 outline-none focus:border-cyan-500/40 font-bold transition-all text-xs min-w-[130px] cursor-pointer shadow-inner hover:border-slate-700"
                      >
                        <option value="viewer">Viewer</option>
                        <option value="operator">Operator</option>
                        <option value="admin">Admin</option>
                      </select>
                    </div>
                  ) : (
                    <div className={`px-4 py-2 rounded-xl text-xs font-black tracking-widest uppercase border ${
                      member.role.toLowerCase() === "admin" ? "bg-cyan-950/60 border-cyan-500/20 text-cyan-400 shadow-[0_0_15px_rgba(34,211,238,0.05)]" :
                      member.role.toLowerCase() === "operator" ? "bg-amber-950/60 border-amber-500/20 text-amber-400" :
                      "bg-slate-900 border-slate-800 text-slate-400"
                    }`}>
                      {member.role}
                    </div>
                  )}

                  {/* Destructive Eviction Trigger Link */}
                  {isUserAdmin && member.email !== currentUserEmail ? (
                    <button
                      onClick={() => removeMember(member.user_id)}
                      disabled={removing === member.user_id}
                      className="h-12 w-12 flex items-center justify-center rounded-xl border border-red-500/20 bg-red-500/5 hover:bg-red-500/20 text-red-400 transition-all active:scale-95"
                      title="Evict Member"
                    >
                      {removing === member.user_id ? (
                        <Loader2 className="animate-spin text-red-400" size={16} />
                      ) : (
                        <Trash2 size={18} />
                      )}
                    </button>
                  ) : (
                    member.email !== currentUserEmail && (
                      <div className="h-12 px-4 flex items-center justify-center gap-1.5 rounded-xl bg-black/40 border border-slate-900 text-zinc-600 font-sans font-semibold text-xs select-none">
                        <Lock size={14} /> Immutable Node
                      </div>
                    )
                  )}

                </div>
              </div>
            ))
          )}
        </div>
      </div>

    </div>
  );
}