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
  Loader2 
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

  // RBAC Client Identity parameters
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
      <div className="h-[60vh] w-full flex items-center justify-center gap-2 font-mono text-xs text-cyan-400">
        <Loader2 className="animate-spin" size={20} />
        <span>SYNCING ROSTER METRIC MATRIX...</span>
      </div>
    );
  }

  const isUserAdmin = currentUserRole === "admin";
  const isUserViewer = currentUserRole === "viewer";

  return (
    <div className="space-y-8 animate-fadeIn">
      
      {/* 1. LAYER ONE: ROLE RULES CARD EXPLANATORY MATRIX PANEL */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        
        {/* ADMIN RULE BADGE */}
        <div className="p-5 rounded-2xl border border-cyan-500/20 bg-gradient-to-b from-[#0a1931]/60 to-[#071120]/40 relative overflow-hidden">
          <div className="flex items-center gap-3 text-cyan-400 mb-2">
            <Crown size={18} />
            <h3 className="font-sans font-black tracking-wide text-sm">Workspace Admin</h3>
          </div>
          <p className="text-zinc-400 text-xs font-sans leading-relaxed">Full system governance capability. Configures environment secrets, billing arrays, and modifies operational member matrices.</p>
        </div>

        {/* OPERATOR RULE BADGE */}
        <div className="p-5 rounded-2xl border border-amber-500/10 bg-gradient-to-b from-[#1c160c]/40 to-[#071120]/40">
          <div className="flex items-center gap-3 text-amber-400 mb-2">
            <ShieldCheck size={18} />
            <h3 className="font-sans font-black tracking-wide text-sm">Engine Operator</h3>
          </div>
          <p className="text-zinc-400 text-xs font-sans leading-relaxed">Runtime control rights. Generates pipelines, invites runtime staff, and monitors execution flows. Key storage read-only protected.</p>
        </div>

        {/* VIEWER RULE BADGE */}
        <div className="p-5 rounded-2xl border border-slate-800 bg-gradient-to-b from-slate-950/40 to-[#071120]/40">
          <div className="flex items-center gap-3 text-zinc-400 mb-2">
            <Eye size={18} />
            <h3 className="font-sans font-black tracking-wide text-sm">Roster Viewer</h3>
          </div>
          <p className="text-zinc-400 text-xs font-sans leading-relaxed">Auditing privileges. Observes logs, processes structural view reports, and views active statuses. Inputs and write commands completely frozen.</p>
        </div>

      </div>

      {/* TWO COLUMN WORK MATRIX SECTION */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8 items-start">
        
        {/* LEFT COMPONENT COLUMN: THE ACTIVE TEAM LOG MATRIX */}
        <div className="xl:col-span-2 rounded-[32px] border border-cyan-500/10 bg-[#071120]/40 p-6 space-y-4">
          <h2 className="text-xl font-black text-white flex items-center gap-2">
            <Users size={20} className="text-cyan-400" /> Active Roster Configurations
          </h2>

          <div className="space-y-4 pt-2">
            {members.length === 0 ? (
              <div className="p-12 text-center border border-dashed border-slate-800 rounded-2xl text-zinc-500 font-mono text-xs">
                EMPTY TEAM ROSTER HANDSHAKE ERROR
              </div>
            ) : (
              members.map((member, idx) => (
                <div 
                  key={member.user_id || idx} 
                  className="p-5 rounded-2xl bg-black/40 border border-slate-900 flex flex-col sm:flex-row sm:items-center justify-between gap-4 transition-all hover:border-cyan-500/10"
                >
                  <div className="space-y-1.5">
                    <div className="text-slate-200 font-sans font-bold text-sm break-all">{member.email}</div>
                    <div className="text-[11px] font-mono text-zinc-500 uppercase tracking-widest flex items-center gap-1">
                      <Shield size={12} className="text-zinc-600" /> Name Ref: <span className="text-zinc-400 font-sans font-semibold capitalize">{member.name || "Pending Entry"}</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 self-end sm:self-auto font-mono text-xs">
                    {/* IF LOGGED IN USER IS ADMIN: GIVE DYNAMIC ROLE DROP SELECT */}
                    {isUserAdmin && member.email !== currentUserEmail ? (
                      <select
                        value={member.role.toLowerCase()}
                        disabled={updatingRole === member.email}
                        onChange={(e) => handleRoleUpdate(member.email, e.target.value)}
                        className="bg-zinc-950 border border-slate-800 rounded-xl h-11 px-3 text-slate-300 outline-none focus:border-cyan-500/30 font-bold transition-all text-xs"
                      >
                        <option value="viewer">Viewer</option>
                        <option value="operator">Operator</option>
                        <option value="admin">Admin</option>
                      </select>
                    ) : (
                      /* Display static high visibility cyberpunk tag if non-admin or self row reference */
                      <span className={`px-3 py-1 rounded-lg text-[10px] font-black tracking-widest uppercase border ${
                        member.role.toLowerCase() === "admin" ? "bg-cyan-950 border-cyan-500/20 text-cyan-400" :
                        member.role.toLowerCase() === "operator" ? "bg-amber-950 border-amber-500/20 text-amber-400" :
                        "bg-slate-900 border-slate-800 text-slate-400"
                      }`}>
                        {member.role}
                      </span>
                    )}

                    {/* DESTRUCTIVE REMOVAL INTERFACE LINK TRASH ACTIONS */}
                    {isUserAdmin && member.email !== currentUserEmail ? (
                      <button
                        onClick={() => removeMember(member.user_id)}
                        disabled={removing === member.user_id}
                        className="h-11 w-11 flex items-center justify-center rounded-xl border border-red-500/20 bg-red-500/5 hover:bg-red-500/20 text-red-400 transition-all shrink-0"
                      >
                        {removing === member.user_id ? (
                          <Loader2 className="animate-spin text-red-400" size={14} />
                        ) : (
                          <Trash2 size={16} />
                        )}
                      </button>
                    ) : (
                      member.email !== currentUserEmail && (
                        <div className="h-11 px-3 flex items-center justify-center gap-1 rounded-xl bg-zinc-950 border border-zinc-900 text-zinc-600 font-sans font-medium text-[11px] select-none">
                          <Lock size={12} /> Guarded
                        </div>
                      )
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* RIGHT COMPONENT COLUMN: THE CONTROL CARD TO DISPATCH INVITATIONS */}
        <div className="rounded-[32px] border border-cyan-500/10 bg-[#071120]/40 p-6 space-y-4">
          <div className="flex items-center gap-2 text-lg font-black text-white">
            <UserPlus size={18} className="text-cyan-400" />
            <span>Deploy Collaborator</span>
          </div>
          <p className="text-xs text-zinc-400 font-sans leading-relaxed">Inject alternative authorized accounts variables directly into this group's localized permission layer model.</p>

          {!isUserViewer ? (
            <div className="space-y-4 pt-2 font-mono text-xs">
              
              <div className="space-y-1.5">
                <label className="text-[10px] text-zinc-500 uppercase tracking-wider">Account Email Address</label>
                <div className="relative flex items-center">
                  <Mail className="absolute left-3.5 text-zinc-500" size={14} />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="teammate@domain.com"
                    className="w-full bg-black border border-slate-800 rounded-xl pl-10 pr-4 h-11 text-white outline-none focus:border-cyan-500/30 text-xs"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-[10px] text-zinc-500 uppercase tracking-wider">Assigned Roster Role</label>
                <select
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className="w-full bg-black border border-slate-800 rounded-xl px-3 h-11 text-slate-300 outline-none focus:border-cyan-500/30 text-xs font-bold"
                >
                  <option value="viewer">Viewer (Auditor Clearance)</option>
                  <option value="operator">Operator (Runtime Execution)</option>
                  {isUserAdmin && <option value="admin">Admin (Total Authorization)</option>}
                </select>
              </div>

              <button
                onClick={addMember}
                disabled={adding || !email.trim()}
                className="w-full h-11 bg-cyan-400 hover:bg-cyan-300 text-black font-sans font-black rounded-xl transition-all disabled:opacity-40 flex items-center justify-center gap-2 text-xs"
              >
                {adding ? (
                  <>
                    <Loader2 className="animate-spin text-black" size={14} />
                    <span>INJECTING RECORD...</span>
                  </>
                ) : (
                  <span>DISPATCH INVITATION</span>
                )}
              </button>

            </div>
          ) : (
            <div className="p-4 rounded-xl bg-black/60 border border-slate-900 flex items-center gap-2 text-xs text-zinc-500 leading-relaxed font-mono">
              <Lock size={14} className="text-zinc-600 shrink-0" /> 
              <span>Invite privileges restricted to Admin or Operator clearance nodes.</span>
            </div>
          )}
        </div>

      </div>

    </div>
  );
}