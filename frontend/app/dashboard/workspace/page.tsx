"use client";

import { useState, useEffect } from "react";
import {
  Users,
  Layers,
  Lock,
  ExternalLink,
  ShieldAlert,
  UserPlus,
  Trash2,
  KeyRound,
  Eye,
  EyeOff,
  Calendar
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
  // ============================================
  // MEMBERSHIP STATE
  // ============================================
  const [members, setMembers] = useState<any[]>([]);
  const [loadingMembers, setLoadingMembers] = useState(true);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState("viewer");
  const [submittingInvite, setSubmittingInvite] = useState(false);

  // ============================================
  // BYOK & RBAC CLEARANCE STATE
  // ============================================
  const [currentUserEmail, setCurrentUserEmail] = useState("");
  const [currentUserRole, setCurrentUserRole] = useState<"admin" | "operator" | "viewer">("viewer");
  const [activeWorkspaceId, setActiveWorkspaceId] = useState<string | null>(null);
  
  // Shared Workspace Credentials Metadata
  const [workspaceKeyStatus, setWorkspaceKeyStatus] = useState({ connected: false, last_updated: "", owner_context: "" });
  const [showInput, setShowInput] = useState(false);
  const [inputKey, setInputKey] = useState("");
  const [submittingKey, setSubmittingKey] = useState(false);
  const [hideTokenInput, setHideTokenInput] = useState(true);

  const providerLinks = {
    gemini: "https://aistudio.google.com/"
  };

  // ============================================
  // INITIALIZATION RUNTIME
  // ============================================
  useEffect(() => {
    if (typeof window !== "undefined") {
      const storedWorkspaceId = localStorage.getItem("workspace_id");
      setActiveWorkspaceId(storedWorkspaceId);
    }
    fetchBaseWorkspaceContext();
  }, []);

  // Listen for global toolbar dropdown workspace variations automatically
  useEffect(() => {
    const handleWorkspaceChange = () => {
      if (typeof window !== "undefined") {
        const currentId = localStorage.getItem("workspace_id");
        setActiveWorkspaceId(currentId);
        fetchWorkspaceContextDetails(currentId);
      }
    };

    window.addEventListener("storage", handleWorkspaceChange);
    const interval = setInterval(handleWorkspaceChange, 2000);

    return () => {
      window.removeEventListener("storage", handleWorkspaceChange);
      clearInterval(interval);
    };
  }, [activeWorkspaceId, currentUserEmail]);

  async function fetchBaseWorkspaceContext() {
    try {
      const me = await getCurrentUser();
      setCurrentUserEmail(me.email);
      
      if (typeof window !== "undefined") {
        const currentId = localStorage.getItem("workspace_id");
        fetchWorkspaceContextDetails(currentId);
      }
    } catch (err) {
      console.error("Failed to load initial profile data context:", err);
    }
  }

  async function fetchWorkspaceContextDetails(wId: string | null) {
    if (!wId) return;
    try {
      setLoadingMembers(true);
      const roster = await getWorkspaceMembers();
      setMembers(roster);

      if (currentUserEmail) {
        const match = roster.find((m: any) => m.user_email === currentUserEmail);
        if (match && match.role) {
          setCurrentUserRole(match.role.toLowerCase());
        }
      }

      const kData = await apiKeyApi.getKeyStatus(wId);
      setWorkspaceKeyStatus(kData);

    } catch (err) {
      console.error("Failed to populate active workspace logs:", err);
    } finally {
      setLoadingMembers(false);
    }
  }

  // ============================================
  // MEMBER MANAGEMENT ACTIONS
  // ============================================
  async function handleAddMember(e: React.FormEvent) {
    e.preventDefault();
    if (!inviteEmail.trim() || submittingInvite) return;

    try {
      setSubmittingInvite(true);
      await createWorkspaceMember({
        email: inviteEmail.trim(),
        role: inviteRole,
      });
      toast.success("Team invitation dispatched successfully!");
      setInviteEmail("");
      if (activeWorkspaceId) fetchWorkspaceContextDetails(activeWorkspaceId);
    } catch (err: any) {
      toast.error(err.message || "Failed to inject workspace membership.");
    } finally {
      setSubmittingInvite(false);
    }
  }

  async function handleRemoveMember(userId: string) {
    const confirmed = window.confirm("Revoke this member's workspace access authorizations?");
    if (!confirmed) return;

    try {
      await deleteWorkspaceMember(userId);
      toast.success("Membership authorization revoked.");
      if (activeWorkspaceId) fetchWorkspaceContextDetails(activeWorkspaceId);
    } catch (err: any) {
      toast.error(err.message || "Failed to remove member record context.");
    }
  }

  // ============================================
  // SHARED WORKSPACE BYOK CREDENTIAL ACTIONS
  // ============================================
  async function handleConnectWorkspaceKey(e: React.FormEvent) {
    e.preventDefault();
    if (!activeWorkspaceId || !inputKey.trim()) return;

    try {
      setSubmittingKey(true);
      await apiKeyApi.connectKey("gemini", inputKey.trim(), activeWorkspaceId);
      toast.success("Shared Workspace API integration saved and verified successfully!");
      setInputKey("");
      setShowInput(false);
      fetchWorkspaceContextDetails(activeWorkspaceId);
    } catch (err: any) {
      toast.error(err.message || "Shared key authorization sync failed with Google servers.");
    } finally {
      setSubmittingKey(false);
    }
  }

  async function handleDisconnectWorkspaceKey() {
    const confirmed = window.confirm("Completely erase shared provider key integrations? All team agents will lose billing backup.");
    if (!confirmed) return;

    try {
      setSubmittingKey(true);
      await apiKeyApi.disconnectKey("gemini", activeWorkspaceId);
      toast.success("Workspace API backup infrastructure disconnected.");
      fetchWorkspaceContextDetails(activeWorkspaceId);
    } catch (err: any) {
      toast.error(err.message || "Erase configurations skipped.");
    } finally {
      setSubmittingKey(false);
    }
  }

  const isUserWorkspaceAdmin = currentUserRole === "admin";

  if (loadingMembers && members.length === 0) {
    return (
      <div className="p-8 text-sm font-mono text-cyan-400 animate-pulse">
        Syncing global workspace operational contexts...
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* HERO BANNER SECTION */}
      <div
        className="
          rounded-[32px]
          border
          border-cyan-500/20
          bg-[linear-gradient(180deg,#071120_0%,#091525_100%)]
          p-8
          overflow-hidden
          relative
        "
      >
        <div className="absolute top-0 right-0 h-72 w-72 rounded-full bg-cyan-500/10 blur-3xl" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="h-16 w-16 rounded-3xl border border-cyan-500/20 bg-cyan-500/10 flex items-center justify-center">
              <Layers className="text-cyan-300" size={32} />
            </div>
            <div>
              <h1 className="text-5xl font-black tracking-tight">Workspace Control</h1>
              <p className="mt-2 text-slate-400">
                Configure group operational access parameters, role hierarchies, and shared api models.
              </p>
            </div>
          </div>

          <div className="flex flex-col items-start md:items-end gap-1.5 font-mono text-xs">
            <span className="text-slate-500 text-[10px] tracking-wider uppercase">Your Access Clearance</span>
            <span className={`px-4 py-1.5 rounded-full text-xs font-black tracking-widest uppercase border border-cyan-500/20 bg-[linear-gradient(180deg,#0e2238_0%,#071120_100%)] ${
              currentUserRole === "admin" ? "text-cyan-300 shadow-[0_0_15px_rgba(34,211,238,0.1)]" :
              currentUserRole === "operator" ? "text-amber-400" : "text-slate-400"
            }`}>
              {currentUserRole}
            </span>
          </div>
        </div>
      </div>

      {/* GRID LAYOUT SECTION */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
        
        {/* MEMBERS ROSTER SYSTEM */}
        <div className="rounded-[32px] border border-cyan-500/20 bg-[linear-gradient(180deg,#071120_0%,#091525_100%)] p-8 space-y-6">
          <div className="flex items-center justify-between mb-2">
            <div>
              <h2 className="text-3xl font-black">Team Roster</h2>
              <p className="text-slate-400 mt-2">Manage workspace members and roles.</p>
            </div>
            <div className="h-14 w-14 rounded-2xl border border-cyan-500/20 bg-cyan-500/10 flex items-center justify-center">
              <Users className="text-cyan-300" size={28} />
            </div>
          </div>

          {currentUserRole !== "viewer" ? (
            <form onSubmit={handleAddMember} className="p-4 rounded-2xl bg-slate-950/40 border border-slate-800/60 flex flex-col sm:flex-row gap-2 font-mono text-xs">
              <input
                type="email"
                required
                value={inviteEmail}
                onChange={(e) => setInviteEmail(e.target.value)}
                placeholder="developer@agentpulse.ai"
                className="flex-1 bg-slate-900/60 border border-slate-800 rounded-xl px-4 h-10 text-white outline-none focus:border-cyan-500/40"
              />
              <select
                value={inviteRole}
                onChange={(e) => setInviteRole(e.target.value)}
                className="bg-slate-900 border border-slate-800 rounded-xl px-3 h-10 text-slate-300 outline-none focus:border-cyan-500/40"
              >
                <option value="viewer">Viewer</option>
                <option value="operator">Operator</option>
                <option value="admin">Admin</option>
              </select>
              <button
                type="submit"
                disabled={submittingInvite || !inviteEmail.trim()}
                className="px-4 h-10 bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/20 text-cyan-300 rounded-xl font-sans font-bold flex items-center justify-center gap-1 transition-all disabled:opacity-40"
              >
                <UserPlus size={16} /> Invite
              </button>
            </form>
          ) : (
            <div className="p-4 rounded-2xl bg-slate-950/20 border border-slate-900 flex items-center gap-2 text-xs font-mono text-slate-500">
              <Lock size={14} /> Organization member injection locked by Workspace Administrator rules.
            </div>
          )}

          <div className="space-y-3 font-mono text-xs">
            {members.map((member: any) => (
              <div
                key={member.id || member.user_id}
                className="p-4 rounded-2xl bg-slate-950/30 border border-slate-800/40 flex items-center justify-between gap-4 transition-all hover:border-slate-800"
              >
                <div className="space-y-1">
                  <div className="text-slate-200 font-sans font-bold break-all">{member.user_email}</div>
                  <div className="text-[10px] text-slate-500 uppercase tracking-widest">
                    Role Clearance Level: <span className="text-cyan-400">{member.role}</span>
                  </div>
                </div>

                {isUserWorkspaceAdmin && member.user_email !== currentUserEmail && (
                  <button
                    onClick={() => handleRemoveMember(member.id || member.user_id)}
                    className="p-2 rounded-xl border border-red-500/10 bg-red-500/5 text-red-400 hover:bg-red-500/20 transition-all shrink-0"
                  >
                    <Trash2 size={16} />
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* SHARED WORKSPACE PROVIDERS PRIVACY SYSTEM CARD */}
        <div className="rounded-[32px] border border-cyan-500/20 bg-[linear-gradient(180deg,#071120_0%,#091525_100%)] p-8 space-y-6">
          <div className="flex items-center justify-between mb-2">
            <div>
              <h2 className="text-3xl font-black">Shared Models</h2>
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
    </div>
  );
}