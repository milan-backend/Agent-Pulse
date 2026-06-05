"use client";

import { useState, useEffect } from "react";
import { Users } from "lucide-react";
import { getWorkspaceMembers, createWorkspaceMember, deleteWorkspaceMember } from "@/components/api";
import { toast } from "sonner";

export default function WorkspacePage() {
  const [members, setMembers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("viewer");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchMembers();
  }, []);

  async function fetchMembers() {
    try {
      setLoading(true);
      const data = await getWorkspaceMembers();
      setMembers(data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  async function handleInvite(e: React.FormEvent) {
    e.preventDefault();
    if (!email) return;
    try {
      setSubmitting(true);
      await createWorkspaceMember({ email, role });
      toast.success("Invitation sent successfully");
      setEmail("");
      fetchMembers();
    } catch (err: any) {
      toast.error(err.message || "Failed to send invitation");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleRemove(userId: string) {
    if (!confirm("Are you sure you want to remove this member?")) return;
    try {
      await deleteWorkspaceMember(userId);
      toast.success("Member removed successfully");
      fetchMembers();
    } catch (err: any) {
      toast.error(err.message || "Failed to remove member");
    }
  }

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      {/* Top Banner Row */}
      <div className="flex justify-between items-center bg-slate-900/40 p-6 rounded-3xl border border-slate-800">
        <div>
          <h1 className="text-3xl font-black text-white">Workspace</h1>
          <p className="text-xs text-slate-400 mt-1">Manage team members and roles.</p>
        </div>
        
        {/* Total Team Members Counter Widget */}
        <div className="bg-slate-950 border border-slate-800 rounded-2xl p-4 flex items-center gap-4 min-w-[200px]">
          <div className="p-2.5 bg-cyan-500/10 rounded-xl text-cyan-400">
            <Users size={20} />
          </div>
          <div>
            <div className="text-[10px] text-slate-500 font-mono uppercase tracking-wider">Team Members</div>
            <div className="text-2xl font-sans font-bold text-white">{members.length}</div>
          </div>
        </div>
      </div>

      {/* Add Workspace Member Form Card */}
      <div className="bg-slate-900/20 border border-slate-800 rounded-[22px] p-6 space-y-4">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <span className="text-cyan-400 font-black">+</span> Add Workspace Member
        </h2>
        
        <form onSubmit={handleInvite} className="flex flex-col sm:flex-row gap-4 items-center">
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="member@email.com"
            className="w-full bg-slate-950 border border-slate-800 rounded-xl h-11 px-4 text-xs text-white outline-none focus:border-cyan-500/40 font-mono"
          />
          
          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            className="w-full sm:w-48 bg-slate-950 border border-slate-800 rounded-xl h-11 px-3 text-xs text-slate-300 outline-none focus:border-cyan-500/40 font-mono"
          >
            <option value="viewer">Viewer</option>
            <option value="operator">Operator</option>
            <option value="admin">Admin</option>
          </select>

          <button
            type="submit"
            disabled={submitting || !email}
            className="w-full sm:w-auto px-6 h-11 bg-cyan-400 hover:bg-cyan-300 text-slate-950 font-sans text-xs font-bold rounded-xl transition-all disabled:opacity-40 shrink-0"
          >
            {submitting ? "Adding..." : "Add Member"}
          </button>
        </form>
      </div>

      {/* Roster Listing Row Container */}
      <div className="bg-slate-900/20 border border-slate-800 rounded-[22px] p-6">
        {loading ? (
          <div className="text-center py-6 text-xs text-cyan-400 animate-pulse font-mono">
            Loading workspace roster configurations...
          </div>
        ) : members.length === 0 ? (
          <div className="py-8 flex flex-col items-center justify-center gap-3 text-slate-400">
            <Users size={40} className="text-slate-600 animate-pulse" />
            <div className="text-sm font-bold tracking-wide">No Workspace Members</div>
          </div>
        ) : (
          <div className="space-y-3 font-mono text-xs">
            {members.map((member) => (
              <div 
                key={member.id || member.user_id} 
                className="p-4 rounded-xl bg-slate-950/40 border border-slate-800 flex items-center justify-between gap-4"
              >
                <div className="text-slate-200 font-sans font-medium break-all">{member.user_email}</div>
                <div className="flex items-center gap-4">
                  <span className="text-cyan-400 uppercase text-[10px] bg-cyan-950/40 border border-cyan-500/20 px-2 py-0.5 rounded font-bold">
                    {member.role}
                  </span>
                  <button
                    onClick={() => handleRemove(member.id || member.user_id)}
                    className="p-1.5 rounded-lg border border-red-500/10 bg-red-500/5 text-red-400 hover:bg-red-500/20 transition-all"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}