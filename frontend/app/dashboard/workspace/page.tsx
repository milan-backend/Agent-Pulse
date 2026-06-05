"use client";

import { useState, useEffect } from "react";
import { 
  Users, 
  Mail, 
  Shield, 
  Trash2, 
  UserPlus, 
  Layers, 
  Lock, 
  Calendar, 
  Eye, 
  EyeOff, 
  ShieldAlert, 
  KeyRound,
  ShieldCheck 
} from "lucide-react";
import { 
  getWorkspaceMembers, 
  createWorkspaceMember, 
  deleteWorkspaceMember, 
  getCurrentUser,
  apiKeyApi 
} from "@/components/api";
import { toast } from "sonner";

export default function WorkspacePage() {
  const [members, setMembers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("viewer");
  const [submitting, setSubmitting] = useState(false);

  // BYOK & RBAC Clearance States
  const [currentUserEmail, setCurrentUserEmail] = useState("");
  const [currentUserRole, setCurrentUserRole] = useState<"admin" | "operator" | "viewer">("viewer");
  const [activeWorkspaceId, setActiveWorkspaceId] = useState<string | null>(null);
  const [workspaceKeyStatus, setWorkspaceKeyStatus] = useState({ connected: false, last_updated: "", owner_context: "" });
  const [showInput, setShowInput] = useState(false);
  const [inputKey, setInputKey] = useState("");
  const [submittingKey, setSubmittingKey] = useState(false);
  const [hideTokenInput, setHideTokenInput] = useState(true);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const storedWorkspaceId = localStorage.getItem("workspace_id");
      setActiveWorkspaceId(storedWorkspaceId);
    }
    fetchBaseContext();
  }, []);

  // Sync automatically when localStorage workspace switches
  useEffect(() => {
    const handleWorkspaceChange = () => {
      if (typeof window !== "undefined") {
        const currentId = localStorage.getItem("workspace_id");
        setActiveWorkspaceId(currentId);
        fetchWorkspaceData(currentId);
      }
    };

    window.addEventListener("storage", handleWorkspaceChange);
    const interval = setInterval(handleWorkspaceChange, 2000);

    return () => {
      window.removeEventListener("storage", handleWorkspaceChange);
      clearInterval(interval);
    };
  }, [activeWorkspaceId, currentUserEmail]);

  async function fetchBaseContext() {
    try {
      const me = await getCurrentUser();
      setCurrentUserEmail(me.email);
      if (typeof window !== "undefined") {
        const currentId = localStorage.getItem("workspace_id");
        fetchWorkspaceData(currentId);
      }
    } catch (err) {
      console.error(err);
    }
  }

  async function fetchWorkspaceData(wId: string | null) {
    try {
      setLoading(true);
      const data = await getWorkspaceMembers();
      setMembers(data || []);

      if (currentUserEmail && data) {
        const match = data.find((m: any) => m.user_email === currentUserEmail);
        if (match?.role) {
          setCurrentUserRole(match.role.toLowerCase());
        }
      }

      if (wId) {
        const kData = await apiKeyApi.getKeyStatus(wId);
        setWorkspaceKeyStatus(kData);
      }
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
      const currentId = localStorage.getItem("workspace_id");
      fetchWorkspaceData(currentId);
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
      const currentId = localStorage.getItem("workspace_id");
      fetchWorkspaceData(currentId);
    } catch (err: any) {
      toast.error(err.message || "Failed to remove member");
    }
  }

  async function handleConnectWorkspaceKey(e: React.FormEvent) {
    e.preventDefault();
    if (!activeWorkspaceId || !inputKey.trim()) return;
    try {
      setSubmittingKey(true);
      await apiKeyApi.connectKey("gemini", inputKey.trim(), activeWorkspaceId);
      toast.success("Shared Workspace API key saved successfully!");
      setInputKey("");
      setShowInput(false);
      fetchWorkspaceData(activeWorkspaceId);
    } catch (err: any) {
      toast.error(err.message || "Failed to save workspace key.");
    } finally {
      setSubmittingKey(false);
    }
  }

  async function handleDisconnectWorkspaceKey() {
    if (!confirm("Completely erase shared provider key integrations? All team agents will lose billing backup.")) return;
    try {
      setSubmittingKey(true);
      await apiKeyApi.disconnectKey("gemini", activeWorkspaceId);
      toast.success("Workspace API key disconnected successfully.");
      fetchWorkspaceData(activeWorkspaceId);
    } catch (err: any) {
      toast.error(err.message || "Failed to remove key.");
    } finally {
      setSubmittingKey(false);
    }
  }

  const isUserWorkspaceAdmin = currentUserRole === "admin";

  return (
    <div className="space-y-8 p-6 max-w-7xl mx-auto">
      {/* HEADER */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-4xl font-black tracking-tight text-white">Workspace Settings</h1>
          <p className="mt-2 text-slate-400">Manage team members, roles, permissions, and shared resources.</p>
        </div>
        <div className="flex items-center gap-2 rounded-full border border-cyan-500/20 bg-cyan-500/5 px-4 py-1.5 font-mono text-xs">
          <span className="text-slate-500 uppercase">Clearance:</span>
          <span className="text-cyan-300 font-bold uppercase tracking-wider">{currentUserRole}</span>
        </div>
      </div>

      {/* TOP CONFIGURATION STATS GRID */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="rounded-3xl border border-slate-800 bg-slate-900/40 p-6 flex items-center gap-4">
          <div className="h-12 w-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
            <Users size={24} />
          </div>
          <div>
            <div className="text-2xl font-black text-white">{members.length}</div>
            <div className="text-xs text-slate-400 mt-0.5">Total Members</div>
          </div>
        </div>

        <div className="rounded-3xl border border-slate-800 bg-slate-900/40 p-6 flex items-center gap-4">
          <div className="h-12 w-12 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
            <Shield size={24} />
          </div>
          <div>
            <div className="text-2xl font-black text-white">
              {members.filter(m => m.role?.toLowerCase() === "admin").length}
            </div>
            <div className="text-xs text-slate-400 mt-0.5">Workspace Admins</div>
          </div>
        </div>

        <div className="rounded-3xl border border-slate-800 bg-slate-900/40 p-6 flex items-center gap-4">
          <div className="h-12 w-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
            <ShieldCheck size={24} />
          </div>
          <div>
            <div className="text-2xl font-black text-white">
              {members.filter(m => m.role?.toLowerCase() === "operator").length}
            </div>
            <div className="text-xs text-slate-400 mt-0.5">Active Operators</div>
          </div>
        </div>
      </div>

      {/* CORE INTERFACE SPLIT GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
        {/* MEMBERS ROSTER TABLE LIST */}
        <div className="lg:col-span-2 rounded-[32px] border border-slate-800 bg-slate-900/20 p-6 space-y-4">
          <h2 className="text-xl font-black text-white">Active Team Members</h2>
          
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse font-mono text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-500 uppercase tracking-wider text-[10px]">
                  <th className="py-3 px-4">Email</th>
                  <th className="py-3 px-4">Role</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/40">
                {loading ? (
                  <tr>
                    <td colSpan={3} className="py-8 text-center text-cyan-400 animate-pulse">Loading roster records...</td>
                  </tr>
                ) : members.length === 0 ? (
                  <tr>
                    <td colSpan={3} className="py-8 text-center text-slate-500">No active members found.</td>
                  </tr>
                ) : (
                  members.map((member) => (
                    <tr key={member.id || member.user_id} className="hover:bg-slate-900/30 transition-all">
                      <td className="py-3.5 px-4 text-slate-200 font-sans font-medium break-all">{member.user_email}</td>
                      <td className="py-3.5 px-4">
                        <span className={`px-2 py-0.5 rounded uppercase tracking-wider text-[10px] font-bold ${
                          member.role?.toLowerCase() === 'admin' ? 'bg-cyan-950 text-cyan-400 border border-cyan-500/20' :
                          member.role?.toLowerCase() === 'operator' ? 'bg-amber-950 text-amber-400 border border-amber-500/20' :
                          'bg-slate-800 text-slate-400'
                        }`}>
                          {member.role}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        {isUserWorkspaceAdmin && member.user_email !== currentUserEmail ? (
                          <button
                            onClick={() => handleRemove(member.id || member.user_id)}
                            className="p-1.5 rounded-lg border border-red-500/10 bg-red-500/5 text-red-400 hover:bg-red-500/20 transition-all"
                          >
                            <Trash2 size={14} />
                          </button>
                        ) : (
                          <span className="text-slate-600 italic text-[11px] font-sans">Locked</span>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* INVITE NEW MEMBER FORM LAYER */}
        <div className="rounded-[32px] border border-slate-800 bg-slate-900/20 p-6 space-y-4">
          <div className="flex items-center gap-2 text-lg font-black text-white">
            <UserPlus size={20} className="text-cyan-400" />
            <span>Invite Member</span>
          </div>
          <p className="text-xs text-slate-400 font-sans leading-relaxed">Add operational collaborators into this specific workspace perimeter.</p>

          {currentUserRole !== "viewer" ? (
            <form onSubmit={handleInvite} className="space-y-4 pt-2">
              <div className="space-y-1.5">
                <label className="text-[10px] font-mono text-slate-500 uppercase tracking-wider">Email Address</label>
                <div className="relative flex items-center">
                  <Mail className="absolute left-3.5 text-slate-500" size={14} />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="name@company.com"
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 h-10 text-xs text-white outline-none focus:border-cyan-500/40"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-[10px] font-mono text-slate-500 uppercase tracking-wider">Workspace Role</label>
                <select
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 h-10 text-xs text-slate-300 outline-none focus:border-cyan-500/40 font-mono"
                >
                  <option value="viewer">Viewer (Read-only)</option>
                  <option value="operator">Operator (Run Engines)</option>
                  <option value="admin">Admin (Full Control)</option>
                </select>
              </div>

              <button
                type="submit"
                disabled={submitting || !email}
                className="w-full h-10 bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/20 text-cyan-300 rounded-xl font-sans text-xs font-bold transition-all disabled:opacity-40"
              >
                {submitting ? "Sending..." : "Send Invitation"}
              </button>
            </form>
          ) : (
            <div className="p-4 rounded-xl bg-slate-950/40 border border-slate-900 flex items-center gap-2 text-xs font-mono text-slate-500">
              <Lock size={12} /> Invite privileges restricted to Admins and Operators.
            </div>
          )}
        </div>
      </div>

      {/* ==================================================== */}
      {/* SHARED WORKSPACE PROVIDERS PRIVACY SYSTEM CARD       */}
      {/* ==================================================== */}
      <div className="rounded-[32px] border border-cyan-500/20 bg-[linear-gradient(180deg,#071120_0%,#091525_100%)] p-8 space-y-6">
        <div className="flex items-center justify-between mb-2">
          <div>
            <h2 className="text-3xl font-black text-white">Shared Workspace Models</h2>
            <p className="text-slate-400 mt-2">Shared workspace backup infrastructure keys.</p>
          </div>
          <div className="h-14 w-14 rounded-2xl border border-cyan-500/20 bg-cyan-500/10 flex items-center justify-center">
            <KeyRound className="text-cyan-300" size={28} />
          </div>
        </div>

        <div className="bg-slate-950/80 border border-slate-800/80 rounded-2xl p-4 flex gap-3 text-xs leading-relaxed text-slate-400 font-sans">
          <ShieldAlert className="w-5 h-5 text-cyan-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="text-slate-200 font-bold">Workspace Privacy Regulations Active</p>
            <p>Shared tokens are 100% obscured. To prevent credentials leaks across teams, plain-text character parsing is mathematically omitted for multi-member views. Modifications lock to strict Admin context.</p>
          </div>
        </div>

        <div className="space-y-4">
          <div className="p-6 bg-slate-950/40 rounded-2xl border border-slate-800/80 flex flex-col lg:flex-row lg:items-center justify-between gap-4 font-mono text-xs">
            <div className="space-y-2">
              <div className="text-sm font-sans font-black text-slate-200">Google Gemini Workspace Tier</div>
              
              <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-slate-500 text-[11px]">
                <div className="flex items-center gap-1">
                  Status: 
                  {workspaceKeyStatus.connected ? (
                    <span className="text-emerald-400 bg-emerald-950/40 border border-emerald-500/20 px-2 py-0.5 rounded text-[10px] font-bold tracking-wide">CONNECTED</span>
                  ) : (
                    <span className="text-slate-500 bg-slate-900 border border-slate-800 px-2 py-0.5 rounded text-[10px] font-bold tracking-wide">NOT CONFIGURED</span>
                  )}
                </div>

                {workspaceKeyStatus.connected && (
                  <>
                    <div className="flex items-center gap-1 text-slate-400">
                      <Calendar size={12} className="text-slate-500" /> Updated: <span className="text-slate-300">{workspaceKeyStatus.last_updated}</span>
                    </div>
                    <div className="flex items-center gap-1 text-slate-400">
                      <Lock size={12} className="text-slate-500" /> Key Payload: <span className="text-cyan-400/80 italic">Encrypted & Hidden</span>
                    </div>
                  </>
                )}
              </div>
            </div>

            <div className="flex items-center gap-2 self-start lg:self-auto">
              {isUserWorkspaceAdmin ? (
                workspaceKeyStatus.connected ? (
                  <>
                    <button
                      onClick={() => setShowInput(!showInput)}
                      className="px-4 h-8 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-sans text-xs transition-all"
                    >
                      Update Key
                    </button>
                    <button
                      onClick={handleDisconnectWorkspaceKey}
                      className="px-4 h-8 rounded-xl border border-red-500/20 bg-red-500/10 hover:bg-red-500/20 text-red-300 font-sans text-xs transition-all"
                    >
                      Remove Key
                    </button>
                  </>
                ) : (
                  <button
                    onClick={() => setShowInput(!showInput)}
                    className="px-4 h-8 rounded-xl bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/20 text-cyan-300 font-sans text-xs font-bold transition-all"
                  >
                    Connect Key
                  </button>
                )
              ) : (
                <div className="text-[11px] font-sans text-slate-500 flex items-center gap-1 bg-slate-950 px-3 py-1 rounded-xl border border-slate-900">
                  <Lock size={12} /> Managed by Workspace Admin
                </div>
              )}
            </div>
          </div>

          {showInput && isUserWorkspaceAdmin && (
            <form onSubmit={handleConnectWorkspaceKey} className="p-5 rounded-2xl bg-slate-950 border border-slate-800 space-y-3 font-mono text-xs">
              <div className="text-slate-400 block font-sans">
                Inject Shared Workspace Token String (`gemini`)
              </div>
              <div className="flex gap-2 relative">
                <input
                  type={hideTokenInput ? "password" : "text"}
                  value={inputKey}
                  onChange={(e) => setInputKey(e.target.value)}
                  placeholder="Enter Google AI Studio key (AIzaSy...)"
                  className="w-full bg-slate-900/40 border border-slate-800 rounded-xl h-10 px-4 pr-10 text-white outline-none focus:border-cyan-500/40 font-mono text-xs"
                />
                <button
                  type="button"
                  onClick={() => setHideTokenInput(!hideTokenInput)}
                  className="absolute right-24 top-2.5 text-slate-500 hover:text-slate-300"
                >
                  {hideTokenInput ? <Eye size={16} /> : <EyeOff size={16} />}
                </button>
                <button
                  type="submit"
                  disabled={submittingKey || !inputKey.trim()}
                  className="bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/20 text-cyan-300 text-xs font-sans font-bold px-4 h-10 rounded-xl transition-all disabled:opacity-40"
                >
                  Inject
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowInput(false);
                    setInputKey("");
                  }}
                  className="bg-transparent border border-slate-800 text-slate-400 text-xs font-sans px-3 h-10 rounded-xl hover:bg-slate-900"
                >
                  Cancel
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}