"use client";

import { useState, useEffect } from "react";
import { 
  KeyRound, 
  Calendar, 
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

  // Tracks active connectivity markers, string configurations, and default status flags
  const [geminiStatus, setGeminiStatus] = useState({ connected: false, last_updated: "", masked_key: "", is_default: false, model_version: "" });
  const [openaiStatus, setOpenaiStatus] = useState({ connected: false, last_updated: "", masked_key: "", is_default: false, model_version: "" });

  // Dropdown selector state tracking
  const [selectedGeminiModel, setSelectedGeminiModel] = useState("gemini-2.5-flash-lite");
  const [selectedOpenAIModel, setSelectedOpenAIModel] = useState("gpt-4o-mini");

  // Input controller states
  const [activeProviderForm, setActiveProviderForm] = useState<"gemini" | "openai" | null>(null);
  const [inputKey, setInputKey] = useState("");
  const [submittingKey, setSubmittingKey] = useState(false);
  const [togglingDefault, setTogglingDefault] = useState(false);
  const [hideTokenInput, setHideTokenInput] = useState(true);

  const providerMeta = {
    gemini: {
      name: "Google Gemini",
      link: "https://aistudio.google.com/",
      placeholder: "Enter Google AI Studio key (AIzaSy...)",
      models: ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro", "gemini-1.5-pro"]
    },
    openai: {
      name: "OpenAI Platform",
      link: "https://platform.openai.com/api-keys",
      placeholder: "Enter OpenAI platform key (sk-proj-...)",
      models: ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "o1-mini"]
    }
  };

  async function syncAllStatuses(workspaceId: string) {
    try {
      // Passes explicitly null for agent_id parameter to ensure workspace-level key isolation
      const geminiData = await apiKeyApi.getKeyStatus(workspaceId, "gemini", null, selectedGeminiModel);
      if (geminiData) {
        setGeminiStatus({
          connected: !!geminiData.connected,
          last_updated: geminiData.last_updated || "Live Asset",
          masked_key: geminiData.masked_key || "Connected",
          is_default: !!geminiData.is_default,
          model_version: geminiData.model_version || "gemini-2.5-flash-lite"
        });
        if (geminiData.model_version) {
          setSelectedGeminiModel(geminiData.model_version);
        }
      }

      const openaiData = await apiKeyApi.getKeyStatus(workspaceId, "openai", null, selectedOpenAIModel);
      if (openaiData) {
        setOpenaiStatus({
          connected: !!openaiData.connected,
          last_updated: openaiData.last_updated || "Live Asset",
          masked_key: openaiData.masked_key || "Connected",
          is_default: !!openaiData.is_default,
          model_version: openaiData.model_version || "gpt-4o-mini"
        });
        if (openaiData.model_version) {
          setSelectedOpenAIModel(openaiData.model_version);
        }
      }
    } catch (err) {
      console.error("Failed to sync structural provider data matrix:", err);
    }
  }

  // Trigger status sync whenever dropdown selections switch to verify variant-level existence checks
  useEffect(() => {
    if (activeWorkspaceId) {
      syncAllStatuses(activeWorkspaceId);
    }
  }, [selectedGeminiModel, selectedOpenAIModel, activeWorkspaceId]);

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
    
    const targetModelVersion = activeProviderForm === "gemini" ? selectedGeminiModel : selectedOpenAIModel;

    try {
      setSubmittingKey(true);
      await apiKeyApi.connectKey(activeProviderForm, inputKey.trim(), activeWorkspaceId, null, targetModelVersion);
      
      // Auto-Toggle the saved target to become default active for this workspace tier immediately
      await apiKeyApi.setDefaultProvider(activeProviderForm, activeWorkspaceId, targetModelVersion, null);

      toast.success(`${providerMeta[activeProviderForm].name} API token stored and activated successfully!`);
      setInputKey("");
      setActiveProviderForm(null);
      await syncAllStatuses(activeWorkspaceId);
    } catch (err: any) {
      toast.error(err.message || "Key verification handshaking failure.");
    } finally {
      setSubmittingKey(false);
    }
  }

  async function handleDisconnectWorkspaceKey(providerKey: "gemini" | "openai") {
    if (!activeWorkspaceId) return;
    if (!window.confirm(`Disconnect shared ${providerMeta[providerKey].name} credential variables?`)) return;
    
    const targetModelVersion = providerKey === "gemini" ? selectedGeminiModel : selectedOpenAIModel;
    
    try {
      setSubmittingKey(true);
      // FIXED: Passed targetModelVersion so backend find-and-delete queries succeed perfectly
      await apiKeyApi.disconnectKey(providerKey, activeWorkspaceId, null, targetModelVersion);
      toast.success(`${providerMeta[providerKey].name} token cleared cleanly.`);
      
      if (providerKey === "gemini") setGeminiStatus({ connected: false, last_updated: "", masked_key: "", is_default: false, model_version: "" });
      else setOpenaiStatus({ connected: false, last_updated: "", masked_key: "", is_default: false, model_version: "" });
      
      await syncAllStatuses(activeWorkspaceId);
      setActiveProviderForm(null);
    } catch (err: any) {
      toast.error(err.message || "Failed to disconnect target.");
    } finally {
      setSubmittingKey(false);
    }
  }

  async function handleSetDefaultProvider(providerKey: "gemini" | "openai") {
    if (!activeWorkspaceId) return;
    const targetModelVersion = providerKey === "gemini" ? selectedGeminiModel : selectedOpenAIModel;
    try {
      setTogglingDefault(true);
      // Passes agent_id as null explicitly to safeguard global routing scopes
      await apiKeyApi.setDefaultProvider(providerKey, activeWorkspaceId, targetModelVersion, null);
      toast.success(`${providerMeta[providerKey].name} set as workspace routing default.`);
      await syncAllStatuses(activeWorkspaceId);
    } catch (err: any) {
      toast.error(err.message || "Failed to update default workspace runtime configuration.");
    } finally {
      setTogglingDefault(false);
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
      
      <div className="space-y-4">
        
        {/* ======================================= */}
        {/* PROVIDER ROW 1: GOOGLE GEMINI          */}
        {/* ======================================= */}
        <div className={`bg-[#090f1c]/40 border rounded-2xl overflow-hidden shadow-xl transition-all duration-300 ${geminiStatus.is_default && geminiStatus.model_version === selectedGeminiModel ? 'border-green-500/30 ring-1 ring-green-500/10' : 'border-slate-800/60'}`}>
          <div className="p-6 md:p-8 flex flex-col lg:flex-row lg:items-center justify-between gap-6 bg-slate-950/20">
            <div className="flex items-center gap-4 flex-1">
              <div className="h-11 w-11 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 shrink-0">
                <KeyRound size={20} />
              </div>
              <div className="space-y-2 flex-1">
                <div className="flex items-center gap-2">
                  <div className="text-base font-bold text-white">Google Gemini Provider</div>
                  {geminiStatus.is_default && geminiStatus.model_version === selectedGeminiModel && (
                    <span className="flex items-center gap-1 text-[10px] uppercase tracking-wider font-mono font-bold text-green-400 bg-green-500/10 border border-green-500/20 px-2 py-0.5 rounded-full">Active Default</span>
                  )}
                </div>
                <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-xs font-mono text-zinc-500">
                  <div className="flex items-center gap-1.5">
                    Status: {geminiStatus.connected ? <span className="text-green-400 font-bold">CONNECTED</span> : <span className="text-zinc-500">NOT CONFIGURED</span>}
                  </div>
                  {geminiStatus.connected && (
                    <>
                      <div className="text-zinc-400 font-sans font-medium bg-slate-950 px-2 py-0.5 rounded border border-slate-800/60 text-[11px]">{geminiStatus.masked_key}</div>
                      <div className="flex items-center gap-1 text-zinc-400"><Calendar size={12} /> Synced: <span className="text-zinc-300">{geminiStatus.last_updated}</span></div>
                    </>
                  )}
                </div>

                {/* Model Version Dropdown Selection Field */}
                <div className="flex items-center gap-2 pt-1 font-sans text-xs">
                  <span className="text-zinc-400 font-medium">Model Selection:</span>
                  <select
                    value={selectedGeminiModel}
                    onChange={(e) => setSelectedGeminiModel(e.target.value)}
                    className="bg-slate-950 border border-slate-800 text-zinc-300 rounded-lg px-2.5 py-1 text-xs focus:border-cyan-500/40 outline-none transition-colors"
                  >
                    {providerMeta.gemini.models.map((model) => (
                      <option key={model} value={model}>{model}</option>
                    ))}
                  </select>
                </div>

              </div>
            </div>
            <div className="flex items-center gap-3 font-sans text-xs shrink-0 self-end lg:self-auto">
              <a href={providerMeta.gemini.link} target="_blank" rel="noreferrer" className="px-3.5 h-10 rounded-xl border border-slate-800 bg-zinc-950 hover:bg-slate-900 text-zinc-400 flex items-center gap-1.5 font-bold transition-colors"><ExternalLink size={12} /></a>
              {geminiStatus.connected && (
                <button
                  type="button"
                  disabled={togglingDefault}
                  onClick={() => handleSetDefaultProvider("gemini")}
                  className={`px-4 h-10 rounded-xl font-bold transition-all border ${
                    geminiStatus.is_default && geminiStatus.model_version === selectedGeminiModel
                      ? "bg-green-500/10 border-green-500/30 text-green-400 cursor-default"
                      : "border-slate-800 bg-slate-900 text-zinc-300 hover:bg-slate-800 hover:text-white"
                  }`}
                >
                  {geminiStatus.is_default && geminiStatus.model_version === selectedGeminiModel ? "✓ Default Active" : "Set as Default"}
                </button>
              )}
              {geminiStatus.connected ? (
                <>
                  <button type="button" onClick={() => { setActiveProviderForm("gemini"); setInputKey(""); }} className="px-4 h-10 rounded-xl bg-zinc-800 text-zinc-200 font-bold hover:bg-zinc-700 transition-colors">Update</button>
                  <button type="button" onClick={() => handleDisconnectWorkspaceKey("gemini")} className="px-4 h-10 rounded-xl border border-red-500/20 bg-red-500/10 text-red-300 font-bold hover:bg-red-500/20 transition-colors">Remove</button>
                </>
              ) : (
                <button type="button" onClick={() => { setActiveProviderForm("gemini"); setInputKey(""); }} className="px-5 h-10 bg-cyan-400 hover:bg-cyan-300 text-slate-950 font-bold rounded-xl transition-all">Connect Provider</button>
              )}
            </div>
          </div>
        </div>

        {/* ======================================= */}
        {/* PROVIDER ROW 2: OPENAI PLATFORM        */}
        {/* ======================================= */}
        <div className={`bg-[#090f1c]/40 border rounded-2xl overflow-hidden shadow-xl transition-all duration-300 ${openaiStatus.is_default && openaiStatus.model_version === selectedOpenAIModel ? 'border-green-500/30 ring-1 ring-green-500/10' : 'border-slate-800/60'}`}>
          <div className="p-6 md:p-8 flex flex-col lg:flex-row lg:items-center justify-between gap-6 bg-slate-950/20">
            <div className="flex items-center gap-4 flex-1">
              <div className="h-11 w-11 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 shrink-0">
                <Cpu size={20} />
              </div>
              <div className="space-y-2 flex-1">
                <div className="flex items-center gap-2">
                  <div className="text-base font-bold text-white">OpenAI Core Provider</div>
                  {openaiStatus.is_default && openaiStatus.model_version === selectedOpenAIModel && (
                    <span className="flex items-center gap-1 text-[10px] uppercase tracking-wider font-mono font-bold text-green-400 bg-green-500/10 border border-green-500/20 px-2 py-0.5 rounded-full">Active Default</span>
                  )}
                </div>
                <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-xs font-mono text-zinc-500">
                  <div className="flex items-center gap-1.5">
                    Status: {openaiStatus.connected ? <span className="text-green-400 font-bold">CONNECTED</span> : <span className="text-zinc-500">NOT CONFIGURED</span>}
                  </div>
                  {openaiStatus.connected && (
                    <>
                      <div className="text-zinc-400 font-sans font-medium bg-slate-950 px-2 py-0.5 rounded border border-slate-800/60 text-[11px]">{openaiStatus.masked_key}</div>
                      <div className="flex items-center gap-1 text-zinc-400"><Calendar size={12} /> Synced: <span className="text-zinc-300">{openaiStatus.last_updated}</span></div>
                    </>
                  )}
                </div>

                {/* Model Version Dropdown Selection Field */}
                <div className="flex items-center gap-2 pt-1 font-sans text-xs">
                  <span className="text-zinc-400 font-medium">Model Selection:</span>
                  <select
                    value={selectedOpenAIModel}
                    onChange={(e) => setSelectedOpenAIModel(e.target.value)}
                    className="bg-slate-950 border border-slate-800 text-zinc-300 rounded-lg px-2.5 py-1 text-xs focus:border-cyan-500/40 outline-none transition-colors"
                  >
                    {providerMeta.openai.models.map((model) => (
                      <option key={model} value={model}>{model}</option>
                    ))}
                  </select>
                </div>

              </div>
            </div>
            <div className="flex items-center gap-3 font-sans text-xs shrink-0 self-end lg:self-auto">
              <a href={providerMeta.openai.link} target="_blank" rel="noreferrer" className="px-3.5 h-10 rounded-xl border border-slate-800 bg-zinc-950 hover:bg-slate-900 text-zinc-400 flex items-center gap-1.5 font-bold transition-colors"><ExternalLink size={12} /></a>
              {openaiStatus.connected && (
                <button
                  type="button"
                  disabled={togglingDefault}
                  onClick={() => handleSetDefaultProvider("openai")}
                  className={`px-4 h-10 rounded-xl font-bold transition-all border ${
                    openaiStatus.is_default && openaiStatus.model_version === selectedOpenAIModel
                      ? "bg-green-500/10 border-green-500/30 text-green-400 cursor-default"
                      : "border-slate-800 bg-slate-900 text-zinc-300 hover:bg-slate-800 hover:text-white"
                  }`}
                >
                  {openaiStatus.is_default && openaiStatus.model_version === selectedOpenAIModel ? "✓ Default Active" : "Set as Default"}
                </button>
              )}
              {openaiStatus.connected ? (
                <>
                  <button type="button" onClick={() => { setActiveProviderForm("openai"); setInputKey(""); }} className="px-4 h-10 rounded-xl bg-zinc-800 text-zinc-200 font-bold hover:bg-zinc-700 transition-colors">Update</button>
                  <button type="button" onClick={() => handleDisconnectWorkspaceKey("openai")} className="px-4 h-10 rounded-xl border border-red-500/20 bg-red-500/10 text-red-300 font-bold hover:bg-red-500/20 transition-colors">Remove</button>
                </>
              ) : (
                <button type="button" onClick={() => { setActiveProviderForm("openai"); setInputKey(""); }} className="px-5 h-10 bg-cyan-400 hover:bg-cyan-300 text-slate-950 font-bold rounded-xl transition-all">Connect Provider</button>
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