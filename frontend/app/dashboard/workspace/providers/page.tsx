"use client";

import { useState, useEffect } from "react";
import { 
  KeyRound, 
  ShieldAlert, 
  Calendar, 
  Lock, 
  Eye, 
  EyeOff, 
  Loader2, 
  ExternalLink,
  Cpu,
  LockKeyhole
} from "lucide-react";
import { getCurrentUser, getWorkspaceMembers, apiKeyApi } from "@/components/api";
import { toast } from "sonner";

export default function WorkspaceProvidersPage() {
  const [loading, setLoading] = useState(true);
  const [userRole, setUserRole] = useState<"admin" | "operator" | "viewer" | null>(null);
  const [activeWorkspaceId, setActiveWorkspaceId] = useState<string | null>(null);

  const [workspaceKeyStatus, setWorkspaceKeyStatus] = useState({ connected: false, last_updated: "", owner_context: "" });
  const [showInput, setShowInput] = useState(false);
  const [inputKey, setInputKey] = useState("");
  const [submittingKey, setSubmittingKey] = useState(false);
  const [hideTokenInput, setHideTokenInput] = useState(true);

  const providerLinks = {
    gemini: "https://aistudio.google.com/"
  };

  useEffect(() => {
    async function initializeSecureContext() {
      try {
        setLoading(true);
        const me = await getCurrentUser();
        const roster = await getWorkspaceMembers();
        
        if (me?.email && roster) {
          const match = roster.find((m: any) => m.user_email === me.email || m.email === me.email);
          if (match?.role) {
            const computedRole = match.role.toLowerCase();
            setUserRole(computedRole as any);
            if (computedRole !== "admin") {
              setLoading(false);
              return;
            }
          }
        }

        if (typeof window !== "undefined") {
          const storedWorkspaceId = localStorage.getItem("workspace_id");
          if (storedWorkspaceId) {
            setActiveWorkspaceId(storedWorkspaceId);
            
            // Fetch status from backend using the correct workspace ID
            const kData = await apiKeyApi.getKeyStatus(storedWorkspaceId);
            setWorkspaceKeyStatus(kData);
          }
        }
      } catch (err) {
        console.error("Failed loading keys:", err);
      } finally {
        setLoading(false);
      }
    }
    initializeSecureContext();
  }, []);

  // ============================================
  // SECURE WORKSPACE BYOK CREDENTIAL ACTIONS
  // ============================================
  async function handleConnectWorkspaceKey(e: React.FormEvent) {
    e.preventDefault();
    if (!activeWorkspaceId || !inputKey.trim()) return;
    try {
      setSubmittingKey(true);
      
      // FIX 1: We send "GEMINI_API_KEY" to backend instead of "gemini"
      await apiKeyApi.connectKey("GEMINI_API_KEY", inputKey.trim(), activeWorkspaceId);
      
      toast.success("Shared Workspace API key updated and validated successfully!");
      setInputKey("");
      setShowInput(false);
      
      // Refresh status instantly
      const kData = await apiKeyApi.getKeyStatus(activeWorkspaceId);
      setWorkspaceKeyStatus(kData);
    } catch (err: any) {
      toast.error(err.message || "Failed to validate key with Google model list parameters.");
    } finally {
      setSubmittingKey(false);
    }
  }

  async function handleDisconnectWorkspaceKey() {
    if (!activeWorkspaceId) return;
    if (!window.confirm("Disconnect this shared key integration?")) return;
    try {
      setSubmittingKey(true);
      
      // Send correct backend key variable name to erase configuration
      await apiKeyApi.disconnectKey("GEMINI_API_KEY", activeWorkspaceId);
      
      toast.success("Workspace configuration decoupled cleanly.");
      const kData = await apiKeyApi.getKeyStatus(activeWorkspaceId);
      setWorkspaceKeyStatus(kData);
      setShowInput(false);
    } catch (err: any) {
      toast.error(err.message || "Failed to disconnect.");
    } finally {
      setSubmittingKey(false);
    }
  }

  if (loading) {
    return (
      <div className="h-[50vh] w-full flex flex-col items-center justify-center gap-3 font-mono text-xs text-cyan-400 tracking-widest">
        <Loader2 className="animate-spin text-cyan-400" size={24} />
        <span>LOADING VAULT METRICS...</span>
      </div>
    );
  }

  if (userRole !== "admin") {
    return (
      <div className="rounded-2xl border border-red-500/10 bg-[#0c0505]/40 p-12 text-center max-w-2xl mx-auto my-12 space-y-4">
        <LockKeyhole size={40} className="text-red-400 mx-auto animate-pulse" />
        <h3 className="text-lg font-bold text-white uppercase tracking-tight">Access Prohibited</h3>
        <p className="text-zinc-400 text-xs font-sans leading-relaxed">
          Secure cluster fallback configurations are restricted strictly to Workspace Administrators.
        </p>
      </div>
    );
  }

  return (
    <div className="w-full space-y-8 animate-fadeIn">
      
      {/* HORIZONTAL PROVIDER DATA CELL CARD */}
      <div className="bg-[#090f1c]/40 border border-slate-800/60 rounded-2xl overflow-hidden shadow-xl">
        <div className="p-6 md:p-8 flex flex-col lg:flex-row lg:items-center justify-between gap-6 bg-slate-950/20">
          
          {/* PROVIDER DETAILS */}
          <div className="flex items-center gap-4 flex-1">
            <div className="h-11 w-11 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 shrink-0">
              <KeyRound size={20} />
            </div>
            <div className="space-y-1">
              <div className="text-base font-bold text-white">Google Gemini Provider</div>
              <div className="flex flex-wrap items-center gap-x-4 text-xs font-mono text-zinc-500">
                <div className="flex items-center gap-1.5">
                  Status: 
                  {workspaceKeyStatus.connected ? (
                    <span className="text-green-400 font-bold">CONNECTED</span>
                  ) : (
                    <span className="text-zinc-500">NOT CONFIGURED</span>
                  )}
                </div>
                {workspaceKeyStatus.connected && (
                  <div className="flex items-center gap-1 text-zinc-400">
                    <Calendar size={12} className="text-zinc-600" /> Synced: <span className="text-zinc-300">{workspaceKeyStatus.last_updated || "Live"}</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* ACTION BUTTON HORIZONTAL LAYOUT */}
          <div className="flex items-center gap-3 font-sans text-xs shrink-0 self-end lg:self-auto">
            <a
              href={providerLinks.gemini}
              target="_blank"
              rel="noreferrer"
              className="px-3.5 h-10 rounded-xl border border-slate-800 bg-zinc-950 hover:bg-slate-900 text-zinc-400 hover:text-zinc-200 flex items-center gap-1.5 font-bold transition-colors"
            >
              <span>Get Token</span>
              <ExternalLink size={12} />
            </a>

            {workspaceKeyStatus.connected ? (
              <>
                <button
                  onClick={() => setShowInput(!showInput)}
                  className="px-4 h-10 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-200 font-bold transition-colors"
                >
                  Update
                </button>
                <button
                  onClick={handleDisconnectWorkspaceKey}
                  disabled={submittingKey}
                  className="px-4 h-10 rounded-xl border border-red-500/20 bg-red-500/10 hover:bg-red-500/20 text-red-300 font-bold transition-colors"
                >
                  {submittingKey ? <Loader2 className="animate-spin" size={14} /> : "Remove"}
                </button>
              </>
            ) : (
              <button
                onClick={() => setShowInput(!showInput)}
                className="px-5 h-10 bg-cyan-400 hover:bg-cyan-300 text-slate-950 font-bold rounded-xl transition-all"
              >
                Connect Provider
              </button>
            )}
          </div>
        </div>

        {/* INPUT COMPONENT SLIDER ROW */}
        {showInput && (
          <form onSubmit={handleConnectWorkspaceKey} className="p-6 bg-black/40 border-t border-slate-800/60 flex flex-col sm:flex-row gap-3 font-mono text-xs animate-fadeIn">
            <div className="relative flex-1 flex items-center">
              <input
                type={hideTokenInput ? "password" : "text"}
                value={inputKey}
                onChange={(e) => setInputKey(e.target.value)}
                placeholder="Enter Google AI Studio key (AIzaSy...)"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl h-11 px-4 pr-12 text-white outline-none focus:border-cyan-500/40 text-xs font-mono font-sans"
              />
              <button
                type="button"
                onClick={() => setHideTokenInput(!hideTokenInput)}
                className="absolute right-4 text-zinc-500 hover:text-zinc-300"
              >
                {hideTokenInput ? <Eye size={16} /> : <EyeOff size={16} />}
              </button>
            </div>
            
            <div className="flex gap-2 font-sans text-xs">
              <button
                type="submit"
                disabled={submittingKey || !inputKey.trim()}
                className="bg-cyan-400 hover:bg-cyan-300 text-slate-950 font-bold px-5 h-11 rounded-xl transition-all disabled:opacity-40 whitespace-nowrap"
              >
                {submittingKey ? "Saving..." : "Save Configuration"}
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowInput(false);
                  setInputKey("");
                }}
                className="bg-transparent border border-slate-800 text-zinc-400 px-4 h-11 rounded-xl hover:bg-zinc-900 transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        )}
      </div>

    </div>
  );
}