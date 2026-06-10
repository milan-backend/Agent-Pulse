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
  LockKeyhole,
  Plus,
  Trash2,
  CheckCircle2,
  HelpCircle,
  Users
} from "lucide-react";
import { getCurrentUser, getWorkspaceMembers, getWorkspaceAgents, apiKeyApi } from "@/components/api";
import { toast } from "sonner";

// Type definition matching the structural database models natively
interface WorkspaceProviderItem {
  id: string;
  provider: "gemini" | "openai";
  provider_name: string;
  model_version: string;
  assigned_agents: string[];
  is_global_default: boolean;
  last_updated?: string;
  masked_key?: string;
}

export default function WorkspaceProvidersPage() {
  const [loading, setLoading] = useState(true);
  const [userRole, setUserRole] = useState<"admin" | "operator" | "viewer" | null>(null);
  const [activeWorkspaceId, setActiveWorkspaceId] = useState<string | null>(null);

  // Advanced array state management to dynamically list unlimited provider items
  const [providersList, setProvidersList] = useState<WorkspaceProviderItem[]>([]);
  const [availableAgents, setAvailableAgents] = useState<{ id: string; name: string }[]>([]);

  // Selection state parameters for adding new provider integration models
  const [selectedGeminiModel, setSelectedGeminiModel] = useState("gemini-2.5-flash-lite");
  const [selectedOpenAIModel, setSelectedOpenAIModel] = useState("gpt-4o-mini");

  // Multi-Provider Form tracking control variables
  const [activeProviderForm, setActiveProviderForm] = useState<"gemini" | "openai" | null>(null);
  const [inputKey, setInputKey] = useState("");
  const [customProviderName, setCustomProviderName] = useState("");
  const [isGlobalDefaultCheck, setIsGlobalDefaultCheck] = useState(false);
  const [selectedAgentsToAssign, setSelectedAgentsToAssign] = useState<string[]>([]);
  
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

  // Syncs all active workspace items directly via the updated backend architecture layout
  async function fetchWorkspaceProvidersMatrix(workspaceId: string) {
    try {
      const data = await apiKeyApi.listWorkspaceProviders(workspaceId);
      
      if (Array.isArray(data)) {
        setProvidersList(data);
      } else {
        // Fallback backward compatibility sync block if backend arrays are empty
        const geminiData = await apiKeyApi.getKeyStatus(workspaceId, "gemini", null, selectedGeminiModel);
        const openaiData = await apiKeyApi.getKeyStatus(workspaceId, "openai", null, selectedOpenAIModel);
        
        const syntheticList: WorkspaceProviderItem[] = [];
        if (geminiData && geminiData.connected) {
          syntheticList.push({
            id: geminiData.id || "gemini-default",
            provider: "gemini",
            provider_name: geminiData.provider_name || "Workspace Gemini Base",
            model_version: geminiData.model_version || "gemini-2.5-flash-lite",
            assigned_agents: geminiData.assigned_agents || [],
            is_global_default: !!geminiData.is_default,
            masked_key: geminiData.masked_key || "Connected",
            last_updated: geminiData.last_updated || "Live"
          });
        }
        if (openaiData && openaiData.connected) {
          syntheticList.push({
            id: openaiData.id || "openai-default",
            provider: "openai",
            provider_name: openaiData.provider_name || "Workspace OpenAI Base",
            model_version: openaiData.model_version || "gpt-4o-mini",
            assigned_agents: openaiData.assigned_agents || [],
            is_global_default: !!openaiData.is_default,
            masked_key: openaiData.masked_key || "Connected",
            last_updated: openaiData.last_updated || "Live"
          });
        }
        setProvidersList(syntheticList);
      }
    } catch (err) {
      console.error("Failed to parse structural multi-provider collections:", err);
    }
  }

  // Fetch available workspace-isolated agents dynamically to assemble selection grids safely
  async function fetchWorkspaceAgentsRoster(workspaceId: string) {
    try {
      // ✅ FIXED: Calls the new authorized getWorkspaceAgents endpoint from api.ts
      const agentsData = await getWorkspaceAgents(workspaceId);
      const agentsArray = agentsData?.agents || agentsData?.data || agentsData || [];
      
      if (Array.isArray(agentsArray)) {
        setAvailableAgents(agentsArray.map((a: any) => ({ 
          id: String(a.id), 
          name: String(a.name || "Unnamed Agent") 
        })));
      }
    } catch (err) {
      console.error("Error collecting workspace scoped agent parameters:", err);
    }
  }

  useEffect(() => {
    if (activeWorkspaceId) {
      fetchWorkspaceProvidersMatrix(activeWorkspaceId);
    }
  }, [activeWorkspaceId, selectedGeminiModel, selectedOpenAIModel]);

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
            await fetchWorkspaceProvidersMatrix(storedWorkspaceId);
            await fetchWorkspaceAgentsRoster(storedWorkspaceId);
          }
        }
      } catch (err) {
        console.error("Cryptographic initialization loop failure:", err);
      } finally {
        setLoading(false);
      }
    }
    initializeSecureContext();
  }, []);

  // ============================================
  // SECURE MULTI-PROVIDER CRUD FORM ACTIONS
  // ============================================
  
  async function handleConnectWorkspaceKey(e: React.FormEvent) {
    e.preventDefault();
    if (!activeWorkspaceId || !inputKey.trim() || !activeProviderForm) return;

    const targetModelVersion = activeProviderForm === "gemini" ? selectedGeminiModel : selectedOpenAIModel;
    const finalProviderLabel = customProviderName.trim() || `${providerMeta[activeProviderForm].name} Configuration`;

    try {
      setSubmittingKey(true);

      await apiKeyApi.connectKey(
        activeProviderForm,
        inputKey.trim(),
        activeWorkspaceId,
        null, 
        targetModelVersion
      );

      toast.success(`Successfully initialized and routed provider instance: "${finalProviderLabel}"`);
      
      // Clean up controller states
      setInputKey("");
      setCustomProviderName("");
      setIsGlobalDefaultCheck(false);
      setSelectedAgentsToAssign([]);
      setActiveProviderForm(null);
      
      await fetchWorkspaceProvidersMatrix(activeWorkspaceId);
    } catch (err: any) {
      toast.error(err.message || "Key verification handshaking failure.");
    } finally {
      setSubmittingKey(false);
    }
  }

  async function handleDisconnectWorkspaceKey(providerId: string) {
    if (!activeWorkspaceId) return;
    if (!window.confirm("Permanently disconnect and clear this targeted provider configuration instance variables?")) return;

    try {
      setSubmittingKey(true);
      
      await apiKeyApi.disconnectKey(
        "gemini", 
        activeWorkspaceId,
        null,
        null
      );

      toast.success("Provider configuration parameters scrubbed cleanly.");
      await fetchWorkspaceProvidersMatrix(activeWorkspaceId);
    } catch (err: any) {
      toast.error(err.message || "Failed to disconnect target.");
    } finally {
      setSubmittingKey(false);
    }
  }

  async function handleSetDefaultProvider(providerId: string, engineType: string) {
    if (!activeWorkspaceId) return;
    try {
      setTogglingDefault(true);
      
      await apiKeyApi.setDefaultProvider(
        engineType,
        activeWorkspaceId,
        null,
        null
      );

      toast.success("Designated configuration instance as primary workspace fallback router choice.");
      await fetchWorkspaceProvidersMatrix(activeWorkspaceId);
    } catch (err: any) {
      toast.error(err.message || "Failed to update default workspace runtime configuration.");
    } finally {
      setTogglingDefault(false);
    }
  }

  function toggleAgentAssignmentSelection(agentId: string) {
    setSelectedAgentsToAssign(prev => 
      prev.includes(agentId) ? prev.filter(id => id !== agentId) : [...prev, agentId]
    );
  }

  if (loading) {
    return (
      <div className="h-[50vh] w-full flex flex-col items-center justify-center gap-3 font-mono text-xs text-cyan-400 tracking-widest">
        <Loader2 className="animate-spin text-cyan-400" size={24} />
        <span>LOADING CRYPTOGRAPHIC MULTI-PROVIDER MATRIX...</span>
      </div>
    );
  }

  if (userRole !== "admin") {
    return (
      <div className="rounded-2xl border border-red-500/10 bg-[#0c0505]/40 p-12 text-center max-w-2xl mx-auto my-12 space-y-4">
        <LockKeyhole size={40} className="text-red-400 mx-auto animate-pulse" />
        <h3 className="text-lg font-bold text-white uppercase tracking-tight">Access Prohibited</h3>
        <p className="text-zinc-400 text-xs font-sans leading-relaxed">
          Secure provider multi-configuration metrics lookups are restricted strictly to Workspace Administrators.
        </p>
      </div>
    );
  }

  return (
    <div className="w-full space-y-6 animate-fadeIn">
      
      {/* HEADER SECTION ROW PLATFORM HOOKS */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-slate-900/20 border border-slate-800/40 p-4 rounded-xl">
        <div className="space-y-1">
          <h2 className="text-base font-bold text-white tracking-tight">Multi-Provider Shared Workspaces Configurations</h2>
          <p className="text-zinc-500 text-xs">Add unlimited custom keys per provider engine, establish automated team-level routing, and guard failsafe lookups.</p>
        </div>
        <div className="flex gap-2 shrink-0">
          <button type="button" onClick={() => { setActiveProviderForm("gemini"); setInputKey(""); }} className="px-3.5 py-2 bg-cyan-950 text-cyan-400 border border-cyan-800/50 rounded-xl font-bold flex items-center gap-1.5 hover:bg-cyan-900/60 transition-colors text-xs"><Plus size={14} /> Gemini Instance</button>
          <button type="button" onClick={() => { setActiveProviderForm("openai"); setInputKey(""); }} className="px-3.5 py-2 bg-purple-950 text-purple-400 border border-purple-800/50 rounded-xl font-bold flex items-center gap-1.5 hover:bg-purple-900/60 transition-colors text-xs"><Plus size={14} /> OpenAI Instance</button>
        </div>
      </div>

      {/* DYNAMIC COLLAPSIBLE INPUT CONTROL SLIDER BLOCK */}
      {activeProviderForm && (
        <form onSubmit={handleConnectWorkspaceKey} className="p-6 bg-[#040c18] border border-slate-800/80 rounded-2xl space-y-4 font-sans text-xs animate-fadeIn shadow-2xl">
          <div className="flex flex-col md:flex-row gap-4">
            
            {/* Field A: Custom Label Name Identification field */}
            <div className="flex-1 space-y-2">
              <label className="text-zinc-400 font-medium">Provider Configuration Name Label:</label>
              <input
                type="text"
                required
                value={customProviderName}
                onChange={(e) => setCustomProviderName(e.target.value)}
                placeholder={activeProviderForm === "gemini" ? "e.g., Gemini Research Dev, Workspace Backup" : "e.g., OpenAI Production Tier, GPT-5 Premium Key"}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl h-11 px-4 text-white outline-none focus:border-cyan-500/40 text-xs font-mono"
              />
            </div>

            {/* Field B: Underlying Dropdown Version Picker Choice */}
            <div className="w-full md:w-64 space-y-2">
              <label className="text-zinc-400 font-medium">Assigned Base Model Variant Choice:</label>
              <select
                value={activeProviderForm === "gemini" ? selectedGeminiModel : selectedOpenAIModel}
                onChange={(e) => activeProviderForm === "gemini" ? setSelectedGeminiModel(e.target.value) : setSelectedOpenAIModel(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 text-zinc-300 rounded-xl h-11 px-4 text-xs focus:border-cyan-500/40 outline-none transition-colors"
              >
                {providerMeta[activeProviderForm].models.map((model) => (
                  <option key={model} value={model}>{model}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Field C: API Credential Plain Token Vector string component input */}
          <div className="space-y-2">
            <label className="text-zinc-400 font-medium">AI Console API Authentication Token Key Structure:</label>
            <div className="relative flex items-center">
              <input
                type={hideTokenInput ? "password" : "text"}
                value={inputKey}
                required
                onChange={(e) => setInputKey(e.target.value)}
                placeholder={providerMeta[activeProviderForm].placeholder}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl h-11 px-4 pr-12 text-white outline-none focus:border-cyan-500/40 font-mono text-xs"
              />
              <button
                type="button"
                onClick={() => setHideTokenInput(!hideTokenInput)}
                className="absolute right-4 text-zinc-500 hover:text-zinc-300"
              >
                {hideTokenInput ? <Eye size={16} /> : <EyeOff size={16} />}
              </button>
            </div>
          </div>

          {/* FIELD D: ENTERPRISE TEAM ROUTING ROUTER OVERVIEW GRID AREA */}
          <div className="border border-slate-800/60 bg-slate-950/40 rounded-xl p-4 space-y-3">
            <div className="flex justify-between items-center border-b border-slate-800/40 pb-2">
              <div className="space-y-0.5">
                <div className="text-zinc-300 font-bold flex items-center gap-1.5"><Users size={14} className="text-cyan-400" /> Scoped Agent Assignment Engine Routing (Optional)</div>
                <div className="text-zinc-500 text-[11px]">Select which specific agents route through this key. Leave unselected to expose as an available workspace baseline fallback choice.</div>
              </div>
              <label className="flex items-center gap-2 bg-slate-950 border border-slate-800 px-3 py-1.5 rounded-lg cursor-pointer hover:bg-slate-900 transition-colors select-none text-[11px]">
                <input
                  type="checkbox"
                  checked={isGlobalDefaultCheck}
                  onChange={(e) => setIsGlobalDefaultCheck(e.target.checked)}
                  className="rounded border-slate-800 text-cyan-400 focus:ring-0 outline-none bg-slate-950"
                />
                <span className="text-zinc-300 font-bold">Designate Workspace Global Fallback</span>
              </label>
            </div>

            {availableAgents.length > 0 ? (
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2 max-h-32 overflow-y-auto pr-2 custom-scrollbar">
                {availableAgents.map((agent) => {
                  const isChecked = selectedAgentsToAssign.includes(agent.id);
                  return (
                    <div 
                      key={agent.id}
                      onClick={() => toggleAgentAssignmentSelection(agent.id)}
                      className={`p-2.5 rounded-lg border text-left cursor-pointer select-none transition-all ${isChecked ? 'bg-cyan-500/10 border-cyan-500/40 text-cyan-400 font-bold' : 'bg-slate-950/60 border-slate-800/80 text-zinc-400 hover:border-zinc-700'}`}
                    >
                      <div className="truncate text-[11px]">{agent.name}</div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-4 text-zinc-500 text-[11px] font-mono">NO ACTIVE AGENTS REGISTERED IN THIS WORKSPACE TENANT POOL</div>
            )}
          </div>
          
          <div className="flex gap-2 justify-end pt-2 text-xs">
            <button
              type="button"
              onClick={() => {
                setActiveProviderForm(null);
                setInputKey("");
                setCustomProviderName("");
                setIsGlobalDefaultCheck(false);
                setSelectedAgentsToAssign([]);
              }}
              className="bg-transparent border border-slate-800 text-zinc-400 px-4 h-10 rounded-xl hover:bg-zinc-900 transition-colors font-bold"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submittingKey || !inputKey.trim()}
              className="bg-cyan-400 hover:bg-cyan-300 text-slate-950 font-bold px-5 h-10 rounded-xl transition-all disabled:opacity-40 whitespace-nowrap"
            >
              {submittingKey ? "Syncing Workspace Providers..." : `Save ${providerMeta[activeProviderForm].name} Key Configuration`}
            </button>
          </div>
        </form>
      )}

      {/* ========================================================= */}
      {/* DYNAMIC LIST GRID INTERFACE RENDERING ACTIVE KEY GROUPS   */}
      {/* ========================================================= */}
      <div className="space-y-3">
        {providersList.length > 0 ? (
          providersList.map((prov) => {
            const isGemini = prov.provider === "gemini";
            return (
              <div 
                key={prov.id} 
                className={`bg-[#090f1c]/40 border rounded-2xl overflow-hidden shadow-xl transition-all duration-300 ${prov.is_global_default ? 'border-green-500/30 ring-1 ring-green-500/10' : 'border-slate-800/60'}`}
              >
                <div className="p-5 md:p-6 flex flex-col lg:flex-row lg:items-center justify-between gap-4 bg-slate-950/20">
                  <div className="flex items-center gap-4 flex-1">
                    <div className={`h-10 w-10 rounded-xl border flex items-center justify-center shrink-0 ${isGemini ? 'bg-cyan-500/10 border-cyan-500/20 text-cyan-400' : 'bg-purple-500/10 border-purple-500/20 text-purple-400'}`}>
                      {isGemini ? <KeyRound size={18} /> : <Cpu size={18} />}
                    </div>
                    
                    <div className="space-y-1 flex-1">
                      <div className="flex items-center flex-wrap gap-2">
                        <span className="text-sm font-bold text-white tracking-wide">{prov.provider_name}</span>
                        <span className={`text-[10px] uppercase font-mono px-2 py-0.5 rounded border ${isGemini ? 'bg-cyan-950/40 border-cyan-800/40 text-cyan-400' : 'bg-purple-950/40 border-purple-800/40 text-purple-400'}`}>{prov.provider}</span>
                        {prov.is_global_default && (
                          <span className="flex items-center gap-1 text-[9px] uppercase tracking-wider font-mono font-bold text-green-400 bg-green-500/10 border border-green-500/20 px-2 py-0.5 rounded-full">Global Fallback</span>
                        )}
                      </div>

                      <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-[11px] font-mono text-zinc-500">
                        <div className="flex items-center gap-1">
                          Model Layer: <span className="text-zinc-300 font-sans">{prov.model_version}</span>
                        </div>
                        {prov.masked_key && (
                          <div className="text-zinc-400 bg-slate-950/80 px-2 py-0.5 rounded border border-slate-800/60 text-[10px]">{prov.masked_key}</div>
                        )}
                        {prov.last_updated && (
                          <div className="flex items-center gap-1 text-zinc-500"><Calendar size={11} /> Configured: <span className="text-zinc-400">{prov.last_updated}</span></div>
                        )}
                      </div>

                      {/* TEAM ASSIGNED ROUTING FOOTPRINT METADATA */}
                      <div className="pt-1.5 flex flex-wrap items-center gap-1.5 text-[10px]">
                        <span className="text-zinc-500 font-mono font-medium">Assigned Routing Access Scopes:</span>
                        {prov.assigned_agents.length > 0 ? (
                          prov.assigned_agents.map((agId) => {
                            const foundAgentName = availableAgents.find(a => a.id === agId)?.name || agId;
                            return (
                              <span key={agId} className="bg-slate-900 border border-slate-800 px-1.5 py-0.5 rounded text-zinc-400 font-sans truncate max-w-[120px]" title={foundAgentName}>
                                @ {foundAgentName}
                              </span>
                            );
                          })
                        ) : (
                          <span className="text-zinc-600 font-mono italic">Exposed globally to unassigned workspace components</span>
                        )}
                      </div>

                    </div>
                  </div>

                  {/* ACTION TRIGGER CONTROLLER SETS */}
                  <div className="flex items-center gap-2 shrink-0 self-end lg:self-auto font-sans text-xs">
                    <a href={isGemini ? providerMeta.gemini.link : providerMeta.openai.link} target="_blank" rel="noreferrer" className="p-2 h-9 rounded-xl border border-slate-800 bg-zinc-950 hover:bg-slate-900 text-zinc-400 flex items-center justify-center transition-colors shadow-inner" title="Open API Console panel"><ExternalLink size={12} /></a>
                    
                    {!prov.is_global_default && (
                      <button
                        type="button"
                        disabled={togglingDefault}
                        onClick={() => handleSetDefaultProvider(prov.id, prov.provider)}
                        className="px-3 h-9 rounded-xl border border-slate-800 bg-slate-900 text-zinc-400 hover:bg-slate-800 hover:text-zinc-200 font-bold transition-colors"
                      >
                        Set Fallback
                      </button>
                    )}

                    <button 
                      type="button" 
                      disabled={submittingKey}
                      onClick={() => handleDisconnectWorkspaceKey(prov.id)} 
                      className="px-3 h-9 rounded-xl border border-red-500/10 bg-red-500/5 hover:bg-red-500/10 text-red-400/80 font-bold flex items-center justify-center gap-1 transition-all"
                      title="Revoke and wipe token settings rows entirely"
                    >
                      <Trash2 size={13} />
                      <span>Remove</span>
                    </button>
                  </div>

                </div>
              </div>
            );
          })
        ) : (
          <div className="border border-dashed border-slate-800 bg-[#060b13]/20 p-12 rounded-2xl text-center space-y-2">
            <HelpCircle size={32} className="text-zinc-600 mx-auto animate-bounce" />
            <h4 className="text-sm font-bold text-zinc-400 uppercase tracking-tight">No Workspace Providers Found</h4>
            <p className="text-zinc-500 text-xs font-sans max-w-sm mx-auto leading-relaxed">
              Click the top buttons to register your initial Google Gemini or OpenAI infrastructure integration keys inside this tenant ecosystem workspace.
            </p>
          </div>
        )}
      </div>

    </div>
  );
}