"use client";

import { useState, useEffect } from "react";
import { 
  KeyRound, 
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

  // Independent configuration states for individual card metrics lookups
  const [geminiStatus, setGeminiStatus] = useState({ connected: false, last_updated: "" });
  const [openaiStatus, setOpenaiStatus] = useState({ connected: false, last_updated: "" });

  // Input controller hooks
  const [activeProviderForm, setActiveProviderForm] = useState<"GEMINI_API_KEY" | "OPENAI_API_KEY" | null>(null);
  const [inputKey, setInputKey] = useState("");
  const [submittingKey, setSubmittingKey] = useState(false);
  const [hideTokenInput, setHideTokenInput] = useState(true);

  const providerMeta = {
    GEMINI_API_KEY: {
      name: "Google Gemini",
      link: "https://aistudio.google.com/",
      placeholder: "Enter Google AI Studio key (AIzaSy...)"
    },
    OPENAI_API_KEY: {
      name: "OpenAI Platform",
      link: "https://platform.openai.com/api-keys",
      placeholder: "Enter OpenAI platform key (sk-proj-...)"
    }
  };

  async function syncAllStatuses(workspaceId: string) {
    try {
      // Fetch our new unified multi-provider response payload dictionary
      const responseData = await apiKeyApi.getKeyStatus(workspaceId);
      
      if (responseData) {
        // Direct map parsing matching our secure backend keys explicitly
        if (responseData.GEMINI_API_KEY) {
          setGeminiStatus({
            connected: !!responseData.GEMINI_API_KEY.connected,
            last_updated: responseData.GEMINI_API_KEY.last_updated || ""
          });
        }
        
        if (responseData.OPENAI_API_KEY) {
          setOpenaiStatus({
            connected: !!responseData.OPENAI_API_KEY.connected,
            last_updated: responseData.OPENAI_API_KEY.last_updated || ""
          });
        }
      }
    } catch (err) {
      console.error("Failed to sync structural provider data matrix:", err);
    }
  }

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
            await syncAllStatuses(storedWorkspaceId);
          }
        }
      } catch (err) {
        console.error(err);
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
    if (!activeWorkspaceId || !inputKey.trim() || !activeProviderForm) return;
    try {
      setSubmittingKey(true);
      await apiKeyApi.connectKey(activeProviderForm, inputKey.trim(), activeWorkspaceId);
      toast.success(`${providerMeta[activeProviderForm].name} API token stored successfully!`);
      setInputKey("");
      setActiveProviderForm(null);
      await syncAllStatuses(activeWorkspaceId);
    } catch (err: any) {
      toast.error(err.message || "Key verification handshaking failure.");
    } finally {
      setSubmittingKey(false);
    }
  }

  async function handleDisconnectWorkspaceKey(providerKey: "GEMINI_API_KEY" | "OPENAI_API_KEY") {
    if (!activeWorkspaceId) return;
    if (!window.confirm(`Disconnect shared ${providerMeta[providerKey].name} credential variables?`)) return;
    try {
      setSubmittingKey(true);
      await apiKeyApi.disconnectKey(providerKey, activeWorkspaceId);
      toast.success(`${providerMeta[providerKey].name} token cleared cleanly.`);
      
      if (providerKey === "GEMINI_API_KEY") setGeminiStatus({ connected: false, last_updated: "" });
      else setOpenaiStatus({ connected: false, last_updated: "" });
      
      await syncAllStatuses(activeWorkspaceId);
      setActiveProviderForm(null);
    } catch (err: any) {
      toast.error(err.message || "Failed to disconnect target.");
    } finally {
      setSubmittingKey(false);
    }
  }

  if (loading) {
    return (
      <div className="h-[50vh] w-full flex flex-col items-center justify-center gap-3 font-mono text-xs text-cyan-400 tracking-widest">
        <Loader2 className="animate-spin text-cyan-400" size={24} />
        <span>LOADING CRYPTOGRAPHIC INFRASTRUCTURE...</span>
      </div>
    );
  }

  if (userRole !== "admin") {
    return (
      <div className="rounded-2xl border border-red-500/10 bg-[#0c0505]/40 p-12 text-center max-w-2xl mx-auto my-12 space-y-4">
        <LockKeyhole size={40} className="text-red-400 mx-auto animate-pulse" />
        <h3 className="text-lg font-bold text-white uppercase tracking-tight">Access Prohibited</h3>
        <p className="text-zinc-400 text-xs font-sans leading-relaxed">
          Secure provider metrics lookups are restricted strictly to Workspace Administrators.
        </p>
      </div>
    );
  }

  return (
    <div className="w-full space-y-6 animate-fadeIn">
      
      {/* MAP ARRAY DATA INTO COMPACT HORIZONTAL CELL BLOCKS */}
      <div className="space-y-4">
        
        {/* ======================================= */}
        {/* PROVIDER ROW 1: GOOGLE GEMINI          */}
        {/* ======================================= */}
        <div className="bg-[#090f1c]/40 border border-slate-800/60 rounded-2xl overflow-hidden shadow-xl">
          <div className="p-6 md:p-8 flex flex-col lg:flex-row lg:items-center justify-between gap-6 bg-slate-950/20">
            <div className="flex items-center gap-4 flex-1">
              <div className="h-11 w-11 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 shrink-0">
                <KeyRound size={20} />
              </div>
              <div className="space-y-1">
                <div className="text-base font-bold text-white">Google Gemini Provider</div>
                <div className="flex flex-wrap items-center gap-x-4 text-xs font-mono text-zinc-500">
                  <div className="flex items-center gap-1.5">
                    Status: {geminiStatus.connected ? <span className="text-green-400 font-bold">CONNECTED</span> : <span className="text-zinc-500">NOT CONFIGURED</span>}
                  </div>
                  {geminiStatus.connected && geminiStatus.last_updated && (
                    <div className="flex items-center gap-1 text-zinc-400"><Calendar size={12} /> Synced: <span className="text-zinc-300">{geminiStatus.last_updated}</span></div>
                  )}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-3 font-sans text-xs shrink-0 self-end lg:self-auto">
              <a href={providerMeta.GEMINI_API_KEY.link} target="_blank" rel="noreferrer" className="px-3.5 h-10 rounded-xl border border-slate-800 bg-zinc-950 hover:bg-slate-900 text-zinc-400 flex items-center gap-1.5 font-bold transition-colors"><ExternalLink size={12} /></a>
              {geminiStatus.connected ? (
                <>
                  <button type="button" onClick={() => { setActiveProviderForm("GEMINI_API_KEY"); setInputKey(""); }} className="px-4 h-10 rounded-xl bg-zinc-800 text-zinc-200 font-bold hover:bg-zinc-700 transition-colors">Update</button>
                  <button type="button" onClick={() => handleDisconnectWorkspaceKey("GEMINI_API_KEY")} className="px-4 h-10 rounded-xl border border-red-500/20 bg-red-500/10 text-red-300 font-bold hover:bg-red-500/20 transition-colors">Remove</button>
                </>
              ) : (
                <button type="button" onClick={() => { setActiveProviderForm("GEMINI_API_KEY"); setInputKey(""); }} className="px-5 h-10 bg-cyan-400 hover:bg-cyan-300 text-slate-950 font-bold rounded-xl transition-all">Connect Provider</button>
              )}
            </div>
          </div>
        </div>

        {/* ======================================= */}
        {/* PROVIDER ROW 2: OPENAI PLATFORM        */}
        {/* ======================================= */}
        <div className="bg-[#090f1c]/40 border border-slate-800/60 rounded-2xl overflow-hidden shadow-xl">
          <div className="p-6 md:p-8 flex flex-col lg:flex-row lg:items-center justify-between gap-6 bg-slate-950/20">
            <div className="flex items-center gap-4 flex-1">
              <div className="h-11 w-11 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 shrink-0">
                <Cpu size={20} />
              </div>
              <div className="space-y-1">
                <div className="text-base font-bold text-white">OpenAI Core Provider</div>
                <div className="flex flex-wrap items-center gap-x-4 text-xs font-mono text-zinc-500">
                  <div className="flex items-center gap-1.5">
                    Status: {openaiStatus.connected ? <span className="text-green-400 font-bold">CONNECTED</span> : <span className="text-zinc-500">NOT CONFIGURED</span>}
                  </div>
                  {openaiStatus.connected && openaiStatus.last_updated && (
                    <div className="flex items-center gap-1 text-zinc-400"><Calendar size={12} /> Synced: <span className="text-zinc-300">{openaiStatus.last_updated}</span></div>
                  )}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-3 font-sans text-xs shrink-0 self-end lg:self-auto">
              <a href={providerMeta.OPENAI_API_KEY.link} target="_blank" rel="noreferrer" className="px-3.5 h-10 rounded-xl border border-slate-800 bg-zinc-950 hover:bg-slate-900 text-zinc-400 flex items-center gap-1.5 font-bold transition-colors"><ExternalLink size={12} /></a>
              {openaiStatus.connected ? (
                <>
                  <button type="button" onClick={() => { setActiveProviderForm("OPENAI_API_KEY"); setInputKey(""); }} className="px-4 h-10 rounded-xl bg-zinc-800 text-zinc-200 font-bold hover:bg-zinc-700 transition-colors">Update</button>
                  <button type="button" onClick={() => handleDisconnectWorkspaceKey("OPENAI_API_KEY")} className="px-4 h-10 rounded-xl border border-red-500/20 bg-red-500/10 text-red-300 font-bold hover:bg-red-500/20 transition-colors">Remove</button>
                </>
              ) : (
                <button type="button" onClick={() => { setActiveProviderForm("OPENAI_API_KEY"); setInputKey(""); }} className="px-5 h-10 bg-cyan-400 hover:bg-cyan-300 text-slate-950 font-bold rounded-xl transition-all">Connect Provider</button>
              )}
            </div>
          </div>
        </div>

      </div>

      {/* DYNAMIC COLLAPSIBLE INPUT CONTROL SLIDER BLOCK */}
      {activeProviderForm && (
        <form onSubmit={handleConnectWorkspaceKey} className="p-6 bg-[#040c18] border border-slate-800 rounded-2xl flex flex-col sm:flex-row gap-3 font-mono text-xs animate-fadeIn">
          <div className="relative flex-1 flex items-center">
            <input
              type={hideTokenInput ? "password" : "text"}
              value={inputKey}
              onChange={(e) => setInputKey(e.target.value)}
              placeholder={providerMeta[activeProviderForm].placeholder}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl h-11 px-4 pr-12 text-white outline-none focus:border-cyan-500/40 text-xs font-sans"
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
              {submittingKey ? "Syncing..." : `Save ${providerMeta[activeProviderForm].name} Key`}
            </button>
            <button
              type="button"
              onClick={() => {
                setActiveProviderForm(null);
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
  );
}