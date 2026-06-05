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
  LockIcon
} from "lucide-react";
import { getCurrentUser, getWorkspaceMembers, apiKeyApi } from "@/components/api";
import { toast } from "sonner";

export default function WorkspaceProvidersPage() {
  const [loading, setLoading] = useState(true);
  const [userRole, setUserRole] = useState<"admin" | "operator" | "viewer" | null>(null);
  const [activeWorkspaceId, setActiveWorkspaceId] = useState<string | null>(null);

  // Secure Cryptographic State 
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
        
        // 1. Authenticate user account identity role
        const me = await getCurrentUser();
        const roster = await getWorkspaceMembers();
        
        if (me?.email && roster) {
          const match = roster.find((m: any) => m.user_email === me.email || m.email === me.email);
          if (match?.role) {
            const computedRole = match.role.toLowerCase();
            setUserRole(computedRole as any);
            
            // Short-circuit evaluations immediately if current session identity is not Admin
            if (computedRole !== "admin") {
              setLoading(false);
              return;
            }
          }
        }

        // 2. Pull operational workspace parameters from memory variables
        if (typeof window !== "undefined") {
          const storedWorkspaceId = localStorage.getItem("workspace_id");
          if (storedWorkspaceId) {
            setActiveWorkspaceId(storedWorkspaceId);
            const kData = await apiKeyApi.getKeyStatus(storedWorkspaceId);
            setWorkspaceKeyStatus(kData);
          }
        }
      } catch (err) {
        console.error("Cryptographic context mapping failure:", err);
        toast.error("Failed to load secure fallback configurations");
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
      await apiKeyApi.connectKey("gemini", inputKey.trim(), activeWorkspaceId);
      toast.success("Shared Workspace API backup token synchronized successfully!");
      setInputKey("");
      setShowInput(false);
      
      // Sync fresh lookup values back into memory layout views
      const kData = await apiKeyApi.getKeyStatus(activeWorkspaceId);
      setWorkspaceKeyStatus(kData);
    } catch (err: any) {
      toast.error(err.message || "Failed to establish integration parameters.");
    } finally {
      setSubmittingKey(false);
    }
  }

  async function handleDisconnectWorkspaceKey() {
    if (!activeWorkspaceId) return;
    if (!window.confirm("Completely wipe shared provider key integrations? All team autonomous engines will instantly drop billing fallback variables.")) return;

    try {
      setSubmittingKey(true);
      await apiKeyApi.disconnectKey("gemini", activeWorkspaceId);
      toast.success("Shared workspace infrastructure parameters decoupled.");
      
      const kData = await apiKeyApi.getKeyStatus(activeWorkspaceId);
      setWorkspaceKeyStatus(kData);
      setShowInput(false);
    } catch (err: any) {
      toast.error(err.message || "Erase configurations execution failure.");
    } finally {
      setSubmittingKey(false);
    }
  }

  if (loading) {
    return (
      <div className="h-[50vh] w-full flex items-center justify-center gap-2 font-mono text-xs text-cyan-400">
        <Loader2 className="animate-spin" size={20} />
        <span>DECRYPTING VAULT SCHEMATICS...</span>
      </div>
    );
  }

  // URL SECURITY GUARDRAIL: If direct browser URL manipulation occurs, hard-block rendering layouts immediately
  if (userRole !== "admin") {
    return (
      <div className="rounded-[32px] border border-red-500/20 bg-gradient-to-b from-[#190909]/60 to-[#020817] p-12 text-center space-y-4 max-w-2xl mx-auto my-10 animate-fadeIn">
        <LockIcon size={48} className="text-red-400 mx-auto animate-pulse" />
        <h2 className="text-2xl font-black text-white uppercase tracking-tight">Access Prohibited</h2>
        <p className="text-zinc-400 text-sm font-sans leading-relaxed">
          Your current clearance credentials (<span className="text-red-400 font-mono font-bold uppercase">{userRole}</span>) lack administrative rights. Secure cluster fallback encryption variables lookups are restricted strictly to Workspace Administrators.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto animate-fadeIn">
      
      {/* CARD CONTEXT TITLE BAR HEADER */}
      <div className="rounded-[32px] border border-cyan-500/10 bg-[#071120]/40 p-8 space-y-6 relative overflow-hidden">
        <div className="absolute top-0 right-0 h-48 w-48 rounded-full bg-cyan-500/5 blur-2xl pointer-events-none" />
        
        <div className="flex items-center gap-4">
          <div className="h-14 w-14 rounded-2xl border border-cyan-500/20 bg-cyan-500/10 flex items-center justify-center text-cyan-400">
            <KeyRound size={26} />
          </div>
          <div>
            <h2 className="text-3xl font-black text-white">Shared Models Configuration</h2>
            <p className="text-zinc-400 text-xs font-sans mt-1 leading-relaxed">Establish base model fallback API parameters. Workspace tokens compute dynamically across all standard agent activities inside this cluster.</p>
          </div>
        </div>

        {/* SECURITY EDUCATION SUB CONTAINER BANNER */}
        <div className="bg-black/40 border border-slate-900 rounded-2xl p-5 flex gap-4 text-xs leading-relaxed text-zinc-400 font-sans">
          <ShieldAlert className="w-5 h-5 text-cyan-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="text-zinc-200 font-bold">Cryptographic Isolation Protocol Active</p>
            <p>Shared variables are immediate write-only processed. Plaintext tracking loops are completely removed from structural responses across user nodes. Teammate entities share the orchestration capability without ever knowing your underlying token payload strings.</p>
          </div>
        </div>

        {/* GOOGLE GEMINI BACKPLANE PANEL MODULE */}
        <div className="space-y-4 pt-2">
          <div className="p-6 bg-black/60 rounded-2xl border border-slate-900 flex flex-col md:flex-row md:items-center justify-between gap-4 font-mono text-xs transition-all hover:border-cyan-500/10">
            <div className="space-y-2.5">
              <div className="text-base font-sans font-black text-slate-200">Google Gemini API Gateway</div>
              
              <div className="flex flex-wrap items-center gap-x-5 gap-y-2 text-zinc-500 text-xs">
                <div className="flex items-center gap-1.5">
                  Status: 
                  {workspaceKeyStatus.connected ? (
                    <span className="text-green-400 font-bold bg-green-500/10 border border-green-500/20 px-2 py-0.5 rounded text-[10px] tracking-wide">CONNECTED</span>
                  ) : (
                    <span className="text-zinc-500 bg-zinc-900 border border-zinc-800 px-2 py-0.5 rounded text-[10px] font-bold tracking-wide">NOT CONFIGURED</span>
                  )}
                </div>

                {workspaceKeyStatus.connected && (
                  <>
                    <div className="flex items-center gap-1 text-zinc-400">
                      <Calendar size={13} className="text-zinc-500" /> Updated: <span className="text-zinc-300">{workspaceKeyStatus.last_updated || "Live Asset"}</span>
                    </div>
                    <div className="flex items-center gap-1 text-zinc-400">
                      <Lock size={13} className="text-zinc-500" /> Storage Block: <span className="text-cyan-400/80 italic font-sans font-semibold">AES-256 Masked</span>
                    </div>
                  </>
                )}
              </div>
            </div>

            {/* DYNAMIC FORM BUTTON ROUTER LAYOUT LINKS */}
            <div className="flex flex-wrap items-center gap-2 self-start md:self-auto font-sans text-xs">
              <a
                href={providerLinks.gemini}
                target="_blank"
                rel="noreferrer"
                className="px-3 h-9 rounded-xl border border-slate-800 bg-zinc-950 hover:bg-slate-900 text-zinc-400 hover:text-zinc-200 flex items-center gap-1.5 font-medium transition-colors"
              >
                <span>Get Token</span>
                <ExternalLink size={12} />
              </a>

              {workspaceKeyStatus.connected ? (
                <>
                  <button
                    onClick={() => setShowInput(!showInput)}
                    className="px-4 h-9 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-200 font-bold transition-all"
                  >
                    Update Infrastructure
                  </button>
                  <button
                    onClick={handleDisconnectWorkspaceKey}
                    disabled={submittingKey}
                    className="px-4 h-9 rounded-xl border border-red-500/20 bg-red-500/10 hover:bg-red-500/20 text-red-300 font-bold transition-all flex items-center justify-center"
                  >
                    {submittingKey ? <Loader2 className="animate-spin text-red-400" size={14} /> : "Disconnect"}
                  </button>
                </>
              ) : (
                <button
                  onClick={() => setShowInput(!showInput)}
                  className="px-5 h-9 rounded-xl bg-cyan-400 hover:bg-cyan-300 text-black font-black transition-all"
                >
                  Configure Fallback Key
                </button>
              )}
            </div>
          </div>

          {/* DYNAMIC TOKEN SLIDE FORM DISPLAY ZONE */}
          {showInput && (
            <form onSubmit={handleConnectWorkspaceKey} className="p-6 rounded-2xl bg-black border border-slate-900 space-y-4 font-mono text-xs max-w-3xl animate-fadeIn">
              <div className="text-zinc-400 text-sm font-sans font-bold">
                Input Vault Token Parameter Variable for Workspace (`gemini`)
              </div>
              <div className="flex flex-col sm:flex-row gap-3 relative">
                <div className="relative flex-1">
                  <input
                    type={hideTokenInput ? "password" : "text"}
                    value={inputKey}
                    onChange={(e) => setInputKey(e.target.value)}
                    placeholder="AIzaSy..."
                    className="w-full bg-zinc-950 border border-slate-800 rounded-xl h-11 px-4 pr-12 text-white outline-none focus:border-cyan-500/30 font-mono text-xs"
                  />
                  <button
                    type="button"
                    onClick={() => setHideTokenInput(!hideTokenInput)}
                    className="absolute right-4 top-3.5 text-zinc-500 hover:text-zinc-300"
                  >
                    {hideTokenInput ? <Eye size={16} /> : <EyeOff size={16} />}
                  </button>
                </div>
                
                <div className="flex gap-2 font-sans text-xs">
                  <button
                    type="submit"
                    disabled={submittingKey || !inputKey.trim()}
                    className="bg-cyan-400 hover:bg-cyan-300 text-black font-black px-5 h-11 rounded-xl transition-all disabled:opacity-40 flex items-center justify-center gap-1.5 whitespace-nowrap"
                  >
                    {submittingKey && <Loader2 className="animate-spin text-black" size={14} />}
                    <span>SYNC KEY VALUE</span>
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
              </div>
            </form>
          )}

        </div>
      </div>
    </div>
  );
}