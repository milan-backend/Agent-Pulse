"use client";

import { useState, useEffect } from "react";
import { 
  Users, 
  Mail, 
  Trash2, 
  UserPlus, 
  Lock, 
  Shield, 
  Crown, 
  Loader2,
  SlidersHorizontal,
  Briefcase
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
        //  FIXED: Clean execution pathway block
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
      toast.error("Failed to sync workspace roster records");
    } finally {
      setLoading(false);
    }
  }

  async function addMember() {
    if (!email.trim()) {
      toast.error("Please enter a valid email address");
      return;
    }
    try {
      setAdding(true);
      const response = await createWorkspaceMember({ email: email.trim(), role });
      toast.success(response?.message || "Workspace invitation sent");
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
      toast.success(response?.message || "Workspace role updated successfully");
      await loadMembers();
    } catch (error: any) {
      toast.error(error?.message || "Failed to modify role context");
    } finally {
      setUpdatingRole(null);
    }
  }

  async function removeMember(userId: string) {
    if (!window.confirm("Are you sure you want to remove this member from the workspace?")) return;
    try {
      setRemoving(userId);
      const response = await deleteWorkspaceMember(userId);
      toast.success(response?.message || "Member removed successfully");
      await loadMembers();
    } catch (error: any) {
      toast.error(error?.message || "Failed to clear member record");
    } finally {
      setRemoving(null);
    }
  }

  if (loading && members.length === 0) {
    return (
      <div className="h-[50vh] w-full flex flex-col items-center justify-center gap-3 font-mono text-xs text-cyan-400 tracking-widest">
        <Loader2 className="animate-spin" size={24} />
        <span>LOADING WORKSPACE CONTEXT...</span>
      </div>
    );
  }

  const isUserAdmin = currentUserRole === "admin";
  const isUserViewer = currentUserRole === "viewer";

  return (
    <div className="max-w-7xl mx-auto space-y-8 px-2 font-sans antialiased animate-fadeIn">
      
      {/* TOP HEADER CONTEXT CONTROL ROW */}
      <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 bg-[#090f1c]/60 border border-slate-800/80 p-6 rounded-2xl">
        <div className="space-y-1">
          <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <Briefcase size={20} className="text-cyan-400" /> Organization Management
          </h2>
          <p className="text-xs text-zinc-400">Control active user credentials, configure network clearances, and allocate runtime permissions.</p>
        </div>

        {/* SYSTEM SUMMARY MINI STATS (HORIZONTAL DENSE BADGES) */}
        <div className="flex items-center gap-3 font-mono text-[11px]">
          <div className="bg-slate-950 border border-slate-800 rounded-xl px-4 py-2 flex items-center gap-2">
            <Users size={14} className="text-cyan-400" />
            <span className="text-zinc-500">Members:</span>
            <span className="text-white font-bold">{members.length}</span>
          </div>
          <div className="bg-slate-950 border border-slate-800 rounded-xl px-4 py-2 flex items-center gap-2">
            <Crown size={14} className="text-purple-400" />
            <span className="text-zinc-500">Admins:</span>
            <span className="text-white font-bold">{members.filter(m => m.role?.toLowerCase() === "admin").length}</span>
          </div>
        </div>
      </div>

      {/* HORIZONTAL DEPLOY MEMBER FORM CARD */}
      <div className="bg-[#090f1c]/40 border border-slate-800/60 rounded-2xl p-6 relative overflow-hidden">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-1 shrink-0 max-w-xs">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <UserPlus size={16} className="text-cyan-400" /> Invite Teammate
            </h3>
            <p className="text-[11px] text-zinc-500">Add operational collaborators directly into this workspace environment cluster.</p>
          </div>

          {!isUserViewer ? (
            <div className="flex-1 flex flex-col sm:flex-row gap-3 w-full max-w-4xl font-mono text-xs">
              
              {/* EMAIL INPUT */}
              <div className="relative flex-1 flex items-center">
                <Mail className="absolute left-4 text-zinc-600" size={16} />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@company.com"
                  className="w-full h-12 bg-slate-950 border border-slate-800 rounded-xl pl-12 pr-4 text-sm text-white outline-none focus:border-cyan-500/40 transition-all font-sans"
                />
              </div>

              {/* CLEARANCE DROP MENU */}
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="bg-slate-950 border border-slate-800 rounded-xl h-12 px-4 text-xs text-slate-300 outline-none focus:border-cyan-500/40 font-bold transition-all sm:w-56 cursor-pointer"
              >
                <option value="viewer">Viewer (Read-Only)</option>
                <option value="operator">Operator (Run Agents)</option>
                {isUserAdmin && <option value="admin">Admin (Full Roots)</option>}
              </select>

              {/* ACTION TRIGGER */}
              <button
                onClick={addMember}
                disabled={adding || !email.trim()}
                className="h-12 px-6 bg-cyan-400 hover:bg-cyan-300 text-slate-950 font-sans font-bold text-xs rounded-xl transition-all disabled:opacity-30 flex items-center justify-center gap-2 uppercase shrink-0 tracking-wider disabled:cursor-not-allowed"
              >
                {adding ? (
                  <Loader2 className="animate-spin text-slate-950" size={16} />
                ) : (
                  <span>Send Invite</span>
                )}
              </button>

            </div>
          ) : (
            <div className="flex-1 max-w-xl p-3.5 rounded-xl bg-slate-950/60 border border-slate-900 flex items-center gap-2 text-xs font-mono text-zinc-500">
              <Lock size={14} className="text-zinc-600 shrink-0" /> Invitation routines are locked to Admin/Operator clearance parameters.
            </div>
          )}
        </div>
      </div>

      {/* ENTERPRISE HORIZONTAL DATA ROSTER TABLE */}
      <div className="bg-[#090f1c]/40 border border-slate-800/60 rounded-2xl overflow-hidden shadow-xl">
        <div className="px-6 py-4.5 border-b border-slate-800 flex items-center justify-between">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <SlidersHorizontal size={14} className="text-cyan-400" /> Active Roster Workspace Context
          </h3>
        </div>

        <div className="overflow-x-auto w-full">
          <table className="w-full border-collapse text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800/80 bg-slate-950/50 text-zinc-500 uppercase tracking-widest text-[10px]">
                <th className="py-4 px-6 font-bold font-mono">Email / Account Identity</th>
                <th className="py-4 px-6 font-bold font-mono">Reference Holder</th>
                <th className="py-4 px-6 font-bold font-mono">Clearance Assignment</th>
                <th className="py-4 px-6 font-bold font-mono text-right">Operational Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/40">
              {members.length === 0 ? (
                <tr>
                  <td colSpan={4} className="py-12 text-center text-zinc-600 tracking-wider">NO ROSTER RECORDS RETURNED</td>
                </tr>
              ) : (
                members.map((member, index) => (
                  <tr key={member.user_id || index} className="hover:bg-slate-900/10 transition-colors group">
                    
                    {/* COLUMN 1: EMAIL IDENTIFIER */}
                    <td className="py-4 px-6 font-sans text-sm font-bold text-slate-200 group-hover:text-cyan-400 transition-colors break-all max-w-xs">
                      {member.email}
                    </td>

                    {/* COLUMN 2: NAME REFERENCE */}
                    <td className="py-4 px-6 text-zinc-400 text-xs font-sans font-medium capitalize">
                      {member.name || <span className="text-zinc-600 italic font-mono text-[11px] normal-case">uninitialized</span>}
                    </td>

                    {/* COLUMN 3: ROLE ASSIGNMENT STATUS DROP / TAG */}
                    <td className="py-4 px-6">
                      {isUserAdmin && member.email !== currentUserEmail ? (
                        <select
                          value={member.role.toLowerCase()}
                          disabled={updatingRole === member.email}
                          onChange={(e) => handleRoleUpdate(member.email, e.target.value)}
                          className="bg-slate-950 border border-slate-800 rounded-xl h-9 px-3 text-slate-300 outline-none focus:border-cyan-500/30 font-bold transition-all text-[11px] min-w-[120px] cursor-pointer"
                        >
                          <option value="viewer">Viewer</option>
                          <option value="operator">Operator</option>
                          <option value="admin">Admin</option>
                        </select>
                      ) : (
                        <span className={`px-2.5 py-1 rounded-lg text-[10px] font-black tracking-widest uppercase border inline-block ${
                          member.role.toLowerCase() === "admin" ? "bg-cyan-950/40 border-cyan-500/20 text-cyan-400" :
                          member.role.toLowerCase() === "operator" ? "bg-amber-950/40 border-amber-500/20 text-amber-400" :
                          "bg-slate-900/60 border-slate-800 text-slate-400"
                        }`}>
                          {member.role}
                        </span>
                      )}
                    </td>

                    {/* COLUMN 4: REMOVAL COMMAND TRIGGER ACTIONS */}
                    <td className="py-4 px-6 text-right">
                      {isUserAdmin && member.email !== currentUserEmail ? (
                        <button
                          onClick={() => removeMember(member.user_id)}
                          disabled={removing === member.user_id}
                          className="h-9 w-9 inline-flex items-center justify-center rounded-xl border border-red-500/20 bg-red-500/5 hover:bg-red-500/20 text-red-400 transition-all active:scale-[0.97]"
                          title="Revoke Member Permission"
                        >
                          {removing === member.user_id ? (
                            <Loader2 className="animate-spin text-red-400" size={14} />
                          ) : (
                            <Trash2 size={15} />
                          )}
                        </button>
                      ) : (
                        member.email !== currentUserEmail && (
                          <div className="inline-flex items-center gap-1 text-[11px] font-sans font-semibold text-zinc-600 select-none bg-slate-950/30 px-2.5 py-1 rounded-lg border border-slate-900">
                            <Lock size={12} /> Secure
                          </div>
                        )
                      )}
                    </td>

                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}