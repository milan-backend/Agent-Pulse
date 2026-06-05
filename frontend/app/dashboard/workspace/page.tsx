"use client";

import {
  useEffect,
  useState,
} from "react";

import {
  Shield,
  UserPlus,
  Users,
  Settings,
  Trash2,
  KeyRound,
  Eye,
  EyeOff,
  ShieldAlert,
  Calendar,
  Lock
} from "lucide-react";

import {
  createWorkspaceMember,
  updateWorkspaceMemberRole,
  getWorkspaceMembers,
  deleteWorkspaceMember,
  getCurrentUser,
  apiKeyApi
} from "@/components/api";

import { toast } from "sonner";

interface WorkspaceMember {
  user_id: string;
  email: string;
  name: string;
  role: string;
}

export default function WorkspacePage() {
  const [members, setMembers] =
    useState<WorkspaceMember[]>([]);

  const [email, setEmail] =
    useState("");

  const [role, setRole] =
    useState("viewer");

  const [loading, setLoading] =
    useState(true);

  const [adding, setAdding] =
    useState(false);

  const [updatingRole, setUpdatingRole] =
    useState<string | null>(null);

  const [removing, setRemoving] =
    useState<string | null>(null);

  // ============================================
  // BYOK & RBAC CLEARANCE STATE
  // ============================================
  const [currentUserEmail, setCurrentUserEmail] = useState("");
  const [currentUserRole, setCurrentUserRole] = useState<"admin" | "operator" | "viewer">("viewer");
  const [activeWorkspaceId, setActiveWorkspaceId] = useState<string | null>(null);
  const [workspaceKeyStatus, setWorkspaceKeyStatus] = useState({ connected: false, last_updated: "", owner_context: "" });
  const [showInput, setShowInput] = useState(false);
  const [inputKey, setInputKey] = useState("");
  const [submittingKey, setSubmittingKey] = useState(false);
  const [hideTokenInput, setHideTokenInput] = useState(true);

  // =========================
  // LOAD MEMBERS
  // =========================

  async function loadMembers() {
    try {
      const data =
        await getWorkspaceMembers();

      setMembers(data || []);

      // Discover logged in user's permission role context inside this workspace roster
      if (currentUserEmail && data) {
        const match = data.find((m: any) => m.user_email === currentUserEmail || m.email === currentUserEmail);
        if (match?.role) {
          setCurrentUserRole(match.role.toLowerCase() as any);
        }
      }

      // Fetch shared workspace provider credentials token metadata status safely
      const storedWorkspaceId = localStorage.getItem("workspace_id");
      if (storedWorkspaceId) {
        setActiveWorkspaceId(storedWorkspaceId);
        const kData = await apiKeyApi.getKeyStatus(storedWorkspaceId);
        setWorkspaceKeyStatus(kData);
      }

    } catch (error) {
      console.error(error);
      toast.error(
        "Failed to load workspace members"
      );
    } finally {
      setLoading(false);
    }
  }

  // ============================================
  // INITIAL LOAD & STORAGE LIFECYCLE HANDLERS
  // ============================================

  useEffect(() => {
    async function initializeContext() {
      try {
        const me = await getCurrentUser();
        setCurrentUserEmail(me.email);
      } catch (err) {
        console.error(err);
      } finally {
        await loadMembers();
      }
    }
    initializeContext();
  }, [currentUserEmail]);

  // Sync automatically when dynamic layout toolbar triggers workspace rotation
  useEffect(() => {
    const handleWorkspaceChange = () => {
      loadMembers();
    };
    window.addEventListener("storage", handleWorkspaceChange);
    const interval = setInterval(handleWorkspaceChange, 2000);

    return () => {
      window.removeEventListener("storage", handleWorkspaceChange);
      clearInterval(interval);
    };
  }, [activeWorkspaceId, currentUserEmail]);

  // =========================
  // ADD MEMBER
  // =========================

  async function addMember() {
    if (!email.trim()) {
      toast.error(
        "Email is required"
      );

      return;
    }

    try {
      setAdding(true);

      const response =
        await createWorkspaceMember({
          email,
          role,
        });

      toast.success(
        response?.message ||
        `Workspace member added successfully`
      );

      setEmail("");

      setRole("viewer");

      await loadMembers();

    } catch (error: any) {
      console.error(error);

      toast.error(
        error?.message ||
        "Failed to add member"
      );
    } finally {
      setAdding(false);
    }
  }

  // =========================
  // UPDATE ROLE
  // =========================

  async function updateRole(
    memberEmail: string,
    newRole: string
  ) {
    try {
      setUpdatingRole(
        memberEmail
      );

      const response =
        await updateWorkspaceMemberRole(
          memberEmail,
          newRole
        );

      toast.success(
        response?.message ||
        "Workspace role updated"
      );

      await loadMembers();

    } catch (error: any) {
      console.error(error);

      toast.error(
        error?.message ||
        "Failed to update role"
      );
    } finally {
      setUpdatingRole(null);
    }
  }

  // =========================
  // DELETE MEMBER
  // =========================

  async function removeMember(
    userId: string
  ) {
    const confirmed =
      window.confirm(
        "Remove this workspace member?"
      );

    if (!confirmed) {
      return;
    }

    try {
      setRemoving(userId);

      const response =
        await deleteWorkspaceMember(
          userId
        );

      toast.success(
        response?.message ||
        "Workspace member removed"
      );

      await loadMembers();

    } catch (error: any) {
      console.error(error);

      toast.error(
        error?.message ||
        "Failed to remove member"
      );
    } finally {
      setRemoving(null);
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
      toast.success("Shared Workspace API key saved successfully!");
      setInputKey("");
      setShowInput(false);
      await loadMembers();
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
      await loadMembers();
    } catch (err: any) {
      toast.error(err.message || "Failed to remove key.");
    } finally {
      setSubmittingKey(false);
    }
  }

  const isUserWorkspaceAdmin = currentUserRole === "admin";

  // =========================
  // LOADING
  // =========================

  if (loading) {
    return (
      <div
        className="
          min-h-screen
          bg-[#020817]
          text-white
          flex
          items-center
          justify-center
        "
      >
        Loading workspace...
      </div>
    );
  }

  // =========================
  // UI
  // =========================

  return (
    <div
      className="
        min-h-screen
        bg-[#020817]
        text-white
        p-8
      "
    >
      {/* HEADER */}

      <div
        className="
          flex
          items-center
          justify-between
          flex-wrap
          gap-6
        "
      >
        <div>
          <h1
            className="
              text-6xl
              font-black
              text-cyan-400
            "
          >
            Workspace
          </h1>

          <p
            className="
              mt-3
              text-zinc-400
              text-lg
            "
          >
            Manage team members and roles.
          </p>
        </div>

        <div
          className="
            rounded-3xl
            border
            border-cyan-500/20
            bg-cyan-500/10
            px-8
            py-5
          "
        >
          <div
            className="
              flex
              items-center
              gap-4
            "
          >
            <Users
              className="
                text-cyan-300
              "
            />

            <div>
              <p className="text-zinc-400">
                Team Members
              </p>

              <h2
                className="
                  text-4xl
                  font-black
                  text-cyan-300
                "
              >
                {members.length}
              </h2>
            </div>
          </div>
        </div>
      </div>

      {/* ADD MEMBER */}

      <div
        className="
          mt-10
          rounded-3xl
          border
          border-cyan-500/10
          bg-[#08111f]
          p-8
        "
      >
        <div
          className="
            flex
            items-center
            gap-4
          "
        >
          <UserPlus
            className="
              text-cyan-300
            "
          />

          <h2
            className="
              text-4xl
              font-black
            "
          >
            Add Workspace Member
          </h2>
        </div>

        <div
          className="
            mt-8
            grid
            grid-cols-1
            xl:grid-cols-3
            gap-6
          "
        >
          <input
            value={email}
            onChange={(e) =>
              setEmail(
                e.target.value
              )
            }
            placeholder="member@email.com"
            className="
              rounded-2xl
              bg-black
              border
              border-cyan-500/10
              p-5
              outline-none
            "
          />

          <select
            value={role}
            onChange={(e) =>
              setRole(
                e.target.value
              )
            }
            className="
              rounded-2xl
              bg-black
              border
              border-cyan-500/10
              p-5
              outline-none
            "
          >
            <option value="viewer">
              Viewer
            </option>

            <option value="operator">
              Operator
            </option>

            <option value="admin">
              Admin
            </option>
          </select>

          <button
            onClick={addMember}
            disabled={adding}
            className="
              rounded-2xl
              bg-cyan-400
              text-black
              font-black
              transition-all
              hover:bg-cyan-300
              disabled:opacity-50
              disabled:cursor-not-allowed
            "
          >
            {
              adding
                ? "Adding Member..."
                : "Add Member"
            }
          </button>
        </div>
      </div>

      {/* MEMBERS */}

      <div
        className="
          mt-10
          grid
          grid-cols-1
          xl:grid-cols-2
          gap-6
        "
      >
        {members.length === 0 && (
          <div
            className="
              col-span-full
              rounded-3xl
              border
              border-white/10
              bg-[#08111f]
              p-14
              text-center
            "
          >
            <Users
              size={60}
              className="
                mx-auto
                text-zinc-600
              "
            />

            <h2
              className="
                mt-6
                text-3xl
                font-black
              "
            >
              No Workspace Members
            </h2>

            <p
              className="
                mt-3
                text-zinc-500
              "
            >
              Invite workspace members to
              collaborate with your AI runtime.
            </p>
          </div>
        )}

        {members.map((member, index) => (
          <div
            key={index}
            className="
              rounded-3xl
              border
              border-cyan-500/10
              bg-[#08111f]
              p-8
            "
          >
            <div
              className="
                flex
                items-start
                justify-between
                gap-6
                flex-wrap
              "
            >
              <div>
                <p className="text-zinc-400">
                  Workspace Member
                </p>

                <h2
                  className="
                    mt-3
                    text-2xl
                    font-black
                    break-all
                    text-cyan-300
                  "
                >
                  {member.email}
                </h2>

                <p
                  className="
                    mt-2
                    text-zinc-500
                  "
                >
                  {member.name}
                </p>

                <div
                  className="
                    mt-5
                    inline-flex
                    items-center
                    gap-2
                    rounded-2xl
                    border
                    border-cyan-500/20
                    bg-cyan-500/10
                    px-4
                    py-2
                  "
                >
                  <Shield
                    size={16}
                    className="text-cyan-300"
                  />

                  <span
                    className="
                      font-bold
                      capitalize
                    "
                  >
                    {member.role}
                  </span>
                </div>
              </div>

              <div
                className="
                  flex
                  items-center
                  gap-3
                  flex-wrap
                "
              >
                <select
                  value={member.role}
                  disabled={
                    updatingRole === member.email
                  }
                  onChange={(e) =>
                    updateRole(
                      member.email,
                      e.target.value
                    )
                  }
                  className="
                    rounded-2xl
                    bg-black
                    border
                    border-cyan-500/10
                    px-5
                    py-4
                    outline-none
                  "
                >
                  <option value="viewer">
                    Viewer
                  </option>

                  <option value="operator">
                    Operator
                  </option>

                  <option value="admin">
                    Admin
                  </option>
                </select>

                <button
                  onClick={() =>
                    removeMember(
                      member.user_id
                    )
                  }
                  disabled={
                    removing === member.user_id
                  }
                  className="
                    h-14
                    px-5
                    rounded-2xl
                    bg-red-500/20
                    border
                    border-red-500/20
                    text-red-300
                    hover:bg-red-500/30
                    flex
                    items-center
                    justify-center
                  "
                >
                  {
                    removing === member.user_id
                      ? (
                        <div
                          className="
                            h-5
                            w-5
                            rounded-full
                            border-2
                            border-red-300/30
                            border-t-red-300
                            animate-spin
                          "
                        />
                      )
                      : (
                        <Trash2 size={18} />
                      )
                  }
                </button>

                <div
                  className="
                    h-14
                    w-14
                    rounded-2xl
                    border
                    border-cyan-500/20
                    bg-cyan-500/10
                    flex
                    items-center
                    justify-center
                  "
                >
                  <Settings
                    className="
                      text-cyan-300
                    "
                  />
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* ==================================================== */}
      {/* ADDED MODULE: SHARED WORKSPACE API KEYS PANEL (BYOK) */}
      {/* ==================================================== */}
      <div
        className="
          mt-10
          rounded-3xl
          border
          border-cyan-500/10
          bg-[#08111f]
          p-8
          space-y-6
        "
      >
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <KeyRound className="text-cyan-300" size={32} />
            <div>
              <h2 className="text-4xl font-black">Shared Workspace Models</h2>
              <p className="text-zinc-400 mt-1 text-sm">Configure backup API infrastructure keys shared across active team operations.</p>
            </div>
          </div>
        </div>

        <div className="bg-black/40 border border-cyan-500/5 rounded-2xl p-5 flex gap-4 text-sm leading-relaxed text-zinc-400">
          <ShieldAlert className="w-5 h-5 text-cyan-300 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="text-zinc-200 font-bold">Workspace Privacy Enforced</p>
            <p>Shared provider secrets are encrypted immediately upon entry. Plain-text key character loops are completely hidden to prevent credential exposure among collaborators. Custom modifications are restricted to Workspace Administrators.</p>
          </div>
        </div>

        <div className="p-6 bg-black rounded-2xl border border-cyan-500/10 flex flex-col lg:flex-row lg:items-center justify-between gap-4 font-mono text-xs">
          <div className="space-y-2">
            <div className="text-lg font-sans font-black text-cyan-300">Google Gemini Workspace Tier</div>
            <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-zinc-500 text-sm">
              <div className="flex items-center gap-2">
                Status: 
                {workspaceKeyStatus.connected ? (
                  <span className="text-green-400 font-bold bg-green-500/10 border border-green-500/20 px-2.5 py-0.5 rounded text-xs">CONNECTED</span>
                ) : (
                  <span className="text-zinc-500 font-bold bg-zinc-900 border border-zinc-800 px-2.5 py-0.5 rounded text-xs">NOT CONFIGURED</span>
                )}
              </div>
              {workspaceKeyStatus.connected && (
                <>
                  <div className="flex items-center gap-1 text-zinc-400">
                    <Calendar size={14} className="text-zinc-500" /> Sync: <span className="text-zinc-300">{workspaceKeyStatus.last_updated}</span>
                  </div>
                  <div className="flex items-center gap-1 text-zinc-400">
                    <Lock size={14} className="text-zinc-500" /> Key: <span className="text-cyan-400/80 italic">Encrypted</span>
                  </div>
                </>
              )}
            </div>
          </div>

          <div className="flex items-center gap-3 self-start lg:self-auto font-sans">
            {isUserWorkspaceAdmin ? (
              workspaceKeyStatus.connected ? (
                <>
                  <button
                    onClick={() => setShowInput(!showInput)}
                    className="px-5 py-2.5 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-sm font-bold transition-all"
                  >
                    Update Key
                  </button>
                  <button
                    onClick={handleDisconnectWorkspaceKey}
                    className="px-5 py-2.5 rounded-xl border border-red-500/20 bg-red-500/10 hover:bg-red-500/20 text-red-300 text-sm font-bold transition-all"
                  >
                    Remove Key
                  </button>
                </>
              ) : (
                <button
                  onClick={() => setShowInput(!showInput)}
                  className="px-5 py-2.5 rounded-xl bg-cyan-400 hover:bg-cyan-300 text-black text-sm font-bold transition-all"
                >
                  Connect Key
                </button>
              )
            ) : (
              <div className="text-xs text-zinc-500 flex items-center gap-1.5 bg-zinc-950 px-4 py-2 rounded-xl border border-zinc-900 font-mono">
                <Lock size={14} /> Managed by Workspace Admin
              </div>
            )}
          </div>
        </div>

        {showInput && isUserWorkspaceAdmin && (
          <form onSubmit={handleConnectWorkspaceKey} className="p-6 rounded-2xl bg-black border border-cyan-500/10 space-y-4">
            <div className="text-zinc-400 text-sm font-bold">
              Provide Workspace Token String (`gemini`)
            </div>
            <div className="flex flex-col sm:flex-row gap-3 relative">
              <div className="relative flex-1">
                <input
                  type={hideTokenInput ? "password" : "text"}
                  value={inputKey}
                  onChange={(e) => setInputKey(e.target.value)}
                  placeholder="Enter Google AI Studio key (AIzaSy...)"
                  className="w-full bg-zinc-950 border border-cyan-500/10 rounded-xl h-12 px-5 pr-12 text-white outline-none focus:border-cyan-500/30 font-mono text-xs"
                />
                <button
                  type="button"
                  onClick={() => setHideTokenInput(!hideTokenInput)}
                  className="absolute right-4 top-3.5 text-zinc-500 hover:text-zinc-300"
                >
                  {hideTokenInput ? <Eye size={18} /> : <EyeOff size={18} />}
                </button>
              </div>
              <div className="flex gap-2">
                <button
                  type="submit"
                  disabled={submittingKey || !inputKey.trim()}
                  className="bg-cyan-400 hover:bg-cyan-300 text-black text-xs font-bold px-5 h-12 rounded-xl transition-all disabled:opacity-40"
                >
                  Save Key
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowInput(false);
                    setInputKey("");
                  }}
                  className="bg-transparent border border-zinc-800 text-zinc-400 text-xs px-4 h-12 rounded-xl hover:bg-zinc-900"
                >
                  Cancel
                </button>
              </div>
            </div>
          </form>
        )}
      </div>

    </div>
  );
}