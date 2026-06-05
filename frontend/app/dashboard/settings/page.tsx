"use client";

import { useState, useEffect } from "react";
import {
  KeyRound,
  ShieldCheck,
  Power,
  PlayCircle,
  LogOut,
  Settings,
  Cpu,
  AlertTriangle,
  User,
  ExternalLink,
  HelpCircle,
  Eye,
  EyeOff
} from "lucide-react";

import {
  stopAllAgents,
  resumeAllAgents,
  logout,
  deactivateAccount,
  getCurrentUser,
  apiKeyApi
} from "@/components/api";

import { toast } from "sonner";

export default function SettingsPage() {
  // ============================================
  // EXISTING INFRASTRUCTURE STATE
  // ============================================
  const [loadingKill, setLoadingKill] = useState(false);
  const [loadingResume, setLoadingResume] = useState(false);
  const [loadingDeactivate, setLoadingDeactivate] = useState(false);
  const [showDeactivateModal, setShowDeactivateModal] = useState(false);
  const [deactivatePassword, setDeactivatePassword] = useState("");

  // ============================================
  // NEW USER PROFILE & BYOK STATE MANAGEMENT
  // ============================================
  const [userProfile, setUserProfile] = useState<{ email: string; full_name?: string } | null>(null);
  const [loadingProfile, setLoadingProfile] = useState(true);
  
  // Provider Key Status States
  const [geminiStatus, setGeminiStatus] = useState({ connected: false, masked_key: "" });
  const [showInputProvider, setShowInputProvider] = useState<"gemini" | "openai" | null>(null);
  const [inputKey, setInputKey] = useState("");
  const [submittingKey, setSubmittingKey] = useState(false);
  const [hideTokenInput, setHideTokenInput] = useState(true);

  const providerLinks = {
    gemini: "https://aistudio.google.com/",
    openai: "https://platform.openai.com/api-keys"
  };

  // ============================================
  // LIFECYCLE INITIALIZATION
  // ============================================
  useEffect(() => {
    fetchProfileAndKeyStatus();
  }, []);

  async function fetchProfileAndKeyStatus() {
    try {
      // 1. Fetch user data from existing auth endpoint
      const user = await getCurrentUser();
      setUserProfile(user);

      // 2. Fetch secure personal credentials metadata configuration state (passing null for personal context)
      const kData = await apiKeyApi.getKeyStatus(null);
      setGeminiStatus(kData);
    } catch (err) {
      console.error("Failed to load account settings data context:", err);
    } finally {
      setLoadingProfile(false);
    }
  }

  // ============================================
  // STOP ALL AGENTS
  // ============================================
  async function handleKillAll() {
    if (loadingKill) return;
    try {
      setLoadingKill(true);
      const confirmed = window.confirm(
        "Are you sure you want to stop all runtime agents?"
      );
      if (!confirmed) {
        return;
      }
      await stopAllAgents();
      toast.success("All agents stopped successfully");
    } catch (err) {
      console.error(err);
      toast.error(
        err instanceof Error ? err.message : "Failed to stop agents"
      );
    } finally {
      setLoadingKill(false);
    }
  }

  // ============================================
  // RESUME ALL AGENTS
  // ============================================
  async function handleResumeAll() {
    if (loadingResume) return;
    try {
      setLoadingResume(true);
      const confirmed = window.confirm("Resume all autonomous agents?");
      if (!confirmed) {
        return;
      }
      await resumeAllAgents();
      toast.success("All agents resumed successfully");
    } catch (err) {
      console.error(err);
      toast.error(
        err instanceof Error ? err.message : "Failed to resume agents"
      );
    } finally {
      setLoadingResume(false);
    }
  }

  // ============================================
  // BYOK METADATA ACTIONS
  // ============================================
  async function handleConnectKey(e: React.FormEvent) {
    e.preventDefault();
    if (!showInputProvider || !inputKey.trim()) return;

    try {
      setSubmittingKey(true);
      await apiKeyApi.connectKey(showInputProvider, inputKey.trim(), null); // Null ensures it maps to private profile row
      toast.success(`Personal credentials linked for ${showInputProvider} successfully!`);
      setInputKey("");
      setShowInputProvider(null);
      fetchProfileAndKeyStatus(); // Refresh structural views
    } catch (err: any) {
      toast.error(err.message || "Key verification failed with provider cloud servers.");
    } finally {
      setSubmittingKey(false);
    }
  }

  async function handleDisconnectKey(provider: string) {
    const confirmed = window.confirm(`Completely detach and remove your personal key configurations for ${provider}?`);
    if (!confirmed) return;

    try {
      setSubmittingKey(true);
      await apiKeyApi.disconnectKey(provider, null);
      toast.success(`Removed personal token bounds for ${provider}.`);
      fetchProfileAndKeyStatus();
    } catch (err: any) {
      toast.error(err.message || "Failed to clear credentials configuration.");
    } finally {
      setSubmittingKey(false);
    }
  }

  // ============================================
  // DEACTIVATE ACCOUNT
  // ============================================
  async function handleDeactivateAccount() {
    if (loadingDeactivate) return;
    try {
      setLoadingDeactivate(true);
      await deactivateAccount(deactivatePassword);
      toast.success("Account deactivated successfully");
      setTimeout(() => {
        logout();
      }, 1200);
    } catch (err) {
      console.error(err);
      toast.error(
        err instanceof Error ? err.message : "Failed to deactivate account"
      );
    } finally {
      setLoadingDeactivate(false);
      setShowDeactivateModal(false);
      setDeactivatePassword("");
    }
  }

  if (loadingProfile) {
    return (
      <div className="p-8 text-sm font-mono text-cyan-400 animate-pulse">
        Initializing user configuration profile details...
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* HERO */}
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
        <div
          className="
            absolute
            top-0
            right-0
            h-72
            w-72
            rounded-full
            bg-cyan-500/10
            blur-3xl
          "
        />

        <div className="relative z-10">
          <div className="flex items-center gap-4 mb-6">
            <div
              className="
                h-16
                w-16
                rounded-3xl
                border
                border-cyan-500/20
                bg-cyan-500/10
                flex
                items-center
                justify-center
              "
            >
              <Settings className="text-cyan-300" size={32} />
            </div>
            <div>
              <h1 className="text-5xl font-black tracking-tight">User Settings</h1>
              <p className="mt-2 text-slate-400">
                Manage personal profile metadata, session parameters, and autonomous billing configurations.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* GRID CONTAINER */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
        
        {/* PROFILE OVERVIEW CARD */}
        <div
          className="
            rounded-[32px]
            border
            border-cyan-500/20
            bg-[linear-gradient(180deg,#071120_0%,#091525_100%)]
            p-8
          "
        >
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-3xl font-black">User Profile</h2>
              <p className="text-slate-400 mt-2">Active account identity data.</p>
            </div>
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
              <User className="text-cyan-300" size={28} />
            </div>
          </div>

          <div className="space-y-4 font-mono text-xs">
            <div className="p-4 rounded-2xl bg-slate-950/40 border border-slate-800/60 space-y-1">
              <div className="text-slate-500 uppercase tracking-wider text-[10px]">Identified Full Name</div>
              <div className="text-sm font-sans font-bold text-slate-200">{userProfile?.full_name || "Anonymous User Context"}</div>
            </div>

            <div className="p-4 rounded-2xl bg-slate-950/40 border border-slate-800/60 space-y-1">
              <div className="text-slate-500 uppercase tracking-wider text-[10px]">Email Reference</div>
              <div className="text-sm text-slate-300">{userProfile?.email}</div>
            </div>
          </div>
        </div>

        {/* SECURITY & SESSION CONTROL CARD */}
        <div
          className="
            rounded-[32px]
            border
            border-cyan-500/20
            bg-[linear-gradient(180deg,#071120_0%,#091525_100%)]
            p-8
          "
        >
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-3xl font-black">Security</h2>
              <p className="text-slate-400 mt-2">Session and API gateway configurations.</p>
            </div>
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
              <KeyRound className="text-cyan-300" size={28} />
            </div>
          </div>

          <div className="space-y-5">
            <div className="rounded-3xl border border-cyan-500/20 bg-cyan-500/10 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-black text-cyan-300">API Gateway</h3>
                  <p className="text-sm text-slate-400 mt-2">Runtime authentication active.</p>
                  <div className="mt-4 inline-flex items-center gap-2 rounded-full border border-green-500/20 bg-green-500/10 px-3 py-1 text-xs font-bold text-green-300">
                    <div className="h-2 w-2 rounded-full bg-green-400 animate-pulse" />
                    ACTIVE
                  </div>
                </div>
                <ShieldCheck className="text-cyan-300" size={28} />
              </div>
            </div>

            <button
              onClick={() => {
                toast.success("Session ended successfully");
                setTimeout(() => {
                  logout();
                }, 800);
              }}
              className="
                w-full
                rounded-3xl
                border
                border-red-500/20
                bg-red-500/10
                hover:bg-red-500/20
                transition-all
                p-6
                flex
                items-center
                justify-between
              "
            >
              <div className="flex items-center gap-4">
                <LogOut className="text-red-300" size={28} />
                <div className="text-left">
                  <h3 className="text-xl font-black text-red-300">Logout Session</h3>
                  <p className="text-sm text-slate-400 mt-1">Terminate current admin session.</p>
                </div>
              </div>
              <LogOut className="text-red-300" size={24} />
            </button>
          </div>
        </div>

        {/* RUNTIME MONITOR CONTROL */}
        <div
          className="
            rounded-[32px]
            border
            border-red-500/20
            bg-[linear-gradient(180deg,#071120_0%,#140808_100%)]
            p-8
            xl:col-span-2
          "
        >
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-3xl font-black">Runtime Control</h2>
              <p className="text-slate-400 mt-2">Manage global agent execution layers.</p>
            </div>
            <div
              className="
                h-14
                w-14
                rounded-2xl
                border
                border-red-500/20
                bg-red-500/10
                flex
                items-center
                justify-center
              "
            >
              <Cpu className="text-red-300" size={28} />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button
              onClick={handleKillAll}
              disabled={loadingKill}
              className="
                w-full
                rounded-3xl
                border
                border-red-500/20
                bg-red-500/10
                hover:bg-red-500/20
                transition-all
                p-6
                flex
                items-center
                justify-between
                disabled:opacity-50
                disabled:cursor-not-allowed
              "
            >
              <div className="flex items-center gap-4">
                <Power className="text-red-300" size={28} />
                <div className="text-left">
                  <h3 className="text-xl font-black text-red-300">
                    {loadingKill ? "Stopping Runtime..." : "Kill All Agents"}
                  </h3>
                  <p className="text-sm text-slate-400 mt-1">Emergency runtime stop.</p>
                </div>
              </div>
              <AlertTriangle className="text-red-300" size={24} />
            </button>

            <button
              onClick={handleResumeAll}
              disabled={loadingResume}
              className="
                w-full
                rounded-3xl
                border
                border-green-500/20
                bg-green-500/10
                hover:bg-green-500/20
                transition-all
                p-6
                flex
                items-center
                justify-between
                disabled:opacity-50
                disabled:cursor-not-allowed
              "
            >
              <div className="flex items-center gap-4">
                <PlayCircle className="text-green-300" size={28} />
                <div className="text-left">
                  <h3 className="text-xl font-black text-green-300">
                    {loadingResume ? "Resuming Runtime..." : "Resume Runtime"}
                  </h3>
                  <p className="text-sm text-slate-400 mt-1">Restart all autonomous agents.</p>
                </div>
              </div>
              <ShieldCheck className="text-green-300" size={24} />
            </button>
          </div>
        </div>

        {/* ==================================================== */}
        {/* HYBRID BRING YOUR OWN KEYS CONTROL PANEL (BYOK)      */}
        {/* ==================================================== */}
        <div
          className="
            rounded-[32px]
            border
            border-cyan-500/20
            bg-[linear-gradient(180deg,#071120_0%,#091525_100%)]
            p-8
            xl:col-span-2
            space-y-6
          "
        >
          <div>
            <h2 className="text-3xl font-black text-white flex items-center gap-3">
              <KeyRound className="text-cyan-300 w-8 h-8" /> Personal API Providers
            </h2>
            <p className="text-slate-400 text-sm mt-2 font-sans">
              Connect private API keys string. Autonomous tasks initialized outside group assets leverage these fallback parameters cleanly.
            </p>
          </div>

          <div className="bg-slate-950/80 border border-slate-800/80 rounded-2xl p-4 flex gap-3 text-xs leading-relaxed text-slate-400 font-sans">
            <HelpCircle className="w-5 h-5 text-cyan-400 shrink-0 mt-0.5" />
            <div className="space-y-1">
              <p className="text-slate-200 font-bold">How do fallback configurations compute?</p>
              <p>When an execution starts, the core tracker scans for shared Workspace Credentials first. If blank, it accesses this personal panel. Your raw credentials are cryptographically scrubbed via AES-256 Fernet layers immediately before writing to memory variables.</p>
            </div>
          </div>

          {/* CHANNELS ROW */}
          <div className="space-y-4">
            
            {/* GOOGLE GEMINI PANEL */}
            <div className="p-6 bg-slate-950/40 rounded-2xl border border-slate-800/80 flex flex-col md:flex-row md:items-center justify-between gap-4 font-mono text-xs">
              <div className="space-y-1">
                <div className="text-sm font-sans font-black text-slate-200">Google Gemini Developer Platform</div>
                <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-slate-500 text-[11px] pt-1">
                  <div className="flex items-center gap-1.5">
                    Status: 
                    {geminiStatus.connected ? (
                      <span className="text-emerald-400 bg-emerald-950/40 border border-emerald-500/20 px-2 py-0.5 rounded text-[10px] font-bold">CONNECTED</span>
                    ) : (
                      <span className="text-slate-500 bg-slate-900 border border-slate-800 px-2 py-0.5 rounded text-[10px] font-bold">NOT CONNECTED</span>
                    )}
                  </div>
                  {geminiStatus.connected && (
                    <div className="text-slate-300 bg-slate-900/60 border border-slate-800 px-2.5 py-1 rounded text-xs tracking-wider">
                      {geminiStatus.masked_key}
                    </div>
                  )}
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-2 self-start md:self-auto">
                <a
                  href={providerLinks.gemini}
                  target="_blank"
                  rel="noreferrer"
                  className="px-3 h-8 rounded-xl border border-slate-800 bg-slate-900 hover:bg-slate-800/80 text-slate-400 hover:text-slate-200 text-xs flex items-center gap-1 font-sans transition-all"
                >
                  Get Key <ExternalLink size={12} />
                </a>

                {geminiStatus.connected ? (
                  <>
                    <button
                      onClick={() => setShowInputProvider(showInputProvider === "gemini" ? null : "gemini")}
                      className="px-4 h-8 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-sans text-xs transition-all"
                    >
                      Update Key
                    </button>
                    <button
                      onClick={() => handleDisconnectKey("gemini")}
                      disabled={submittingKey}
                      className="px-4 h-8 rounded-xl border border-red-500/20 bg-red-500/10 hover:bg-red-500/20 text-red-300 font-sans text-xs transition-all"
                    >
                      Remove Key
                    </button>
                  </>
                ) : (
                  <button
                    onClick={() => setShowInputProvider(showInputProvider === "gemini" ? null : "gemini")}
                    className="px-4 h-8 rounded-xl bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/20 text-cyan-300 font-sans text-xs font-bold transition-all"
                  >
                    Connect Key
                  </button>
                )}
              </div>
            </div>

            {/* OPENAI API GATEWAY PANEL */}
            <div className="p-6 bg-slate-950/40 rounded-2xl border border-slate-800/80 flex flex-col md:flex-row md:items-center justify-between gap-4 font-mono text-xs opacity-60">
              <div className="space-y-1">
                <div className="text-sm font-sans font-black text-slate-400">OpenAI Commercial API Tier</div>
                <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-slate-600 text-[11px] pt-1">
                  <div className="flex items-center gap-1.5">
                    Status: <span className="text-slate-600 bg-slate-900 border border-slate-800 px-2 py-0.5 rounded text-[10px] font-bold">COMING SOON</span>
                  </div>
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-2 self-start md:self-auto">
                <a
                  href={providerLinks.openai}
                  target="_blank"
                  rel="noreferrer"
                  className="px-3 h-8 rounded-xl border border-slate-800 bg-slate-900 text-slate-500 text-xs flex items-center gap-1 font-sans cursor-not-allowed"
                >
                  Get Key <ExternalLink size={12} />
                </a>
              </div>
            </div>

          </div>

          {/* DYNAMIC TOKEN INPUT CONSOLE ROW */}
          {showInputProvider && (
            <form onSubmit={handleConnectKey} className="p-5 rounded-2xl bg-slate-950 border border-slate-800 max-w-2xl space-y-3 font-mono text-xs">
              <div className="text-slate-400 block font-sans">
                Input Secure Token String for <span className="text-cyan-300 capitalize font-bold">{showInputProvider}</span>
              </div>
              <div className="flex gap-2 relative">
                <input
                  type={hideTokenInput ? "password" : "text"}
                  value={inputKey}
                  onChange={(e) => setInputKey(e.target.value)}
                  placeholder={showInputProvider === "gemini" ? "AIzaSy..." : "sk-..."}
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
                  Save
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowInputProvider(null);
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

        {/* DANGER ZONE CONTAINER */}
        <div
          className="
            rounded-[32px]
            border
            border-red-500/20
            bg-[linear-gradient(180deg,#120707_0%,#190909_100%)]
            p-8
            xl:col-span-2
          "
        >
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-3xl font-black">Danger Zone</h2>
              <p className="text-slate-400 mt-2">Sensitive account parameters.</p>
            </div>
            <div
              className="
                h-14
                w-14
                rounded-2xl
                border
                border-red-500/20
                bg-red-500/10
                flex
                items-center
                justify-center
              "
            >
              <AlertTriangle className="text-red-300" size={28} />
            </div>
          </div>

          <button
            onClick={() => setShowDeactivateModal(true)}
            disabled={loadingDeactivate}
            className="
              w-full
              rounded-3xl
              border
              border-red-500/20
              bg-red-500/10
              hover:bg-red-500/20
              transition-all
              p-6
              flex
              items-center
              justify-between
              disabled:opacity-50
              disabled:cursor-not-allowed
            "
          >
            <div className="flex items-center gap-4">
              <AlertTriangle className="text-red-300" size={28} />
              <div className="text-left">
                <h3 className="text-xl font-black text-red-300">Deactivate Account</h3>
                <p className="text-sm text-slate-400 mt-1">Disable access to your profile parameters and runtime logs.</p>
              </div>
            </div>
            <Power className="text-red-300" size={24} />
          </button>
        </div>
      </div>

      {/* ============================================
          DEACTIVATE MODAL
      ============================================ */}
      {showDeactivateModal && (
        <div
          className="
            fixed
            inset-0
            z-50
            bg-black/70
            backdrop-blur-sm
            flex
            items-center
            justify-center
            p-6
          "
        >
          <div
            className="
              w-full
              max-w-lg
              rounded-[32px]
              border
              border-red-500/20
              bg-[#091120]
              p-8
              shadow-2xl
            "
          >
            <div className="flex items-center gap-4 mb-6">
              <div
                className="
                  h-14
                  w-14
                  rounded-2xl
                  border
                  border-red-500/20
                  bg-red-500/10
                  flex
                  items-center
                  justify-center
                "
              >
                <AlertTriangle className="text-red-300" size={28} />
              </div>
              <div>
                <h2 className="text-3xl font-black">Deactivate Account</h2>
                <p className="text-slate-400 mt-1">This action disables access to your account parameters.</p>
              </div>
            </div>

            <div className="space-y-3">
              <label className="text-sm font-bold text-slate-300">Confirm Password</label>
              <input
                type="password"
                value={deactivatePassword}
                onChange={(e) => setDeactivatePassword(e.target.value)}
                placeholder="Enter password"
                className="
                  w-full
                  rounded-2xl
                  border
                  border-red-500/20
                  bg-red-500/5
                  px-5
                  py-4
                  text-white
                  outline-none
                  focus:border-red-400
                "
              />
            </div>

            <div className="flex items-center justify-end gap-4 mt-8">
              <button
                onClick={() => {
                  setShowDeactivateModal(false);
                  setDeactivatePassword("");
                }}
                className="
                  rounded-2xl
                  border
                  border-white/10
                  px-6
                  py-3
                  text-slate-300
                  hover:bg-white/5
                  transition-all
                "
              >
                Cancel
              </button>

              <button
                onClick={handleDeactivateAccount}
                disabled={loadingDeactivate || !deactivatePassword}
                className="
                  rounded-2xl
                  border
                  border-red-500/20
                  bg-red-500/10
                  px-6
                  py-3
                  text-red-300
                  font-bold
                  hover:bg-red-500/20
                  transition-all
                  disabled:opacity-50
                "
              >
                {loadingDeactivate ? "Deactivating..." : "Deactivate"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}