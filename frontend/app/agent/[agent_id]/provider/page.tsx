"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { 
  KeyRound, 
  Calendar, 
  Eye, 
  EyeOff, 
  Loader2, 
  ExternalLink,
  Cpu,
  Trash2
} from "lucide-react";
import { getAgent, apiKeyApi } from "@/components/api";
import { toast } from "sonner";
import Link from "next/link";

export default function AgentProviderPage() {
  const params = useParams();
  const agentId = params?.agent_id as string;

  const [loading, setLoading] = useState(true);
  const [agentName, setAgentName] = useState("Agent");

  // Private cryptographic track arrays matching individual sandbox contexts
  const [geminiStatus, setGeminiStatus] = useState({ connected: false, last_updated: "", masked_key: "" });
  const [openaiStatus, setOpenaiStatus] = useState({ connected: false, last_updated: "", masked_key: "" });

  // Dropdown option tracking loops
  const [selectedGeminiModel, setSelectedGeminiModel] = useState("gemini-2.5-flash-lite");
  const [selectedOpenAIModel, setSelectedOpenAIModel] = useState("gpt-4o-mini");

  // Form toggles
  const [activeProviderForm, setActiveProviderForm] = useState<"gemini" | "openai" | null>(null);
  const [inputKey, setInputKey] = useState("");
  const [submittingKey, setSubmittingKey] = useState(false);
  const [hideTokenInput, setHideTokenInput] = useState(true);

  const providerMeta = {
    gemini: {
      name: "Google Gemini",
      link: "https://aistudio.google.com/",
      placeholder: "Enter private Gemini key override (AIzaSy...)",
      models: ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro", "gemini-1.5-pro"]
    },
    openai: {
      name: "OpenAI Platform",
      link: "https://platform.openai.com/api-keys",
      placeholder: "Enter private OpenAI key override (sk-proj-...)",
      models: ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "o1-mini"]
    }
  };

  async function syncAgentStatuses() {
    if (typeof window === "undefined") return;
    const workspaceId = localStorage.getItem("workspace_id");

    try {
      // 1. Check Gemini Status bound to this explicit agent context (FIXED: Passed workspaceId instead of null)
      const geminiData = await apiKeyApi.getKeyStatus(workspaceId, "gemini", agentId);
      if (geminiData) {
        setGeminiStatus({
          connected: !!geminiData.connected,
          last_updated: geminiData.last_updated || "Live Override",
          masked_key: geminiData.masked_key || "Overridden Context"
        });
        if (geminiData.model_version) {
          setSelectedGeminiModel(geminiData.model_version);
        }
      }

      // 2. Check OpenAI Status bound to this explicit agent context (FIXED: Passed workspaceId instead of null)
      const openaiData = await apiKeyApi.getKeyStatus(workspaceId, "openai", agentId);
      if (openaiData) {
        setOpenaiStatus({
          connected: !!openaiData.connected,
          last_updated: openaiData.last_updated || "Live Override",
          masked_key: openaiData.masked_key || "Overridden Context"
        });
        if (openaiData.model_version) {
          setSelectedOpenAIModel(openaiData.model_version);
        }
      }
    } catch (err) {
      console.error("Failed to sync fine-grained agent key mapping:", err);
    }
  }

  useEffect(() => {
    async function loadAgentAndCredentials() {
      if (!agentId) return;
      try {
        setLoading(true);
        const response = await getAgent(agentId);
        const agentData = response?.agent || response;
        setAgentName(agentData?.name || "Agent");

        await syncAgentStatuses();
      } catch (err) {
        console.error(err);
        toast.error("Failed to load runtime authentication status.");
      } finally {
        setLoading(false);
      }
    }
    loadAgentAndCredentials();
  }, [agentId]);

  async function handleConnectAgentKey(e: React.FormEvent) {
    e.preventDefault();
    if (!agentId || !inputKey.trim() || !activeProviderForm) return;

    const chosenModel = activeProviderForm === "gemini" ? selectedGeminiModel : selectedOpenAIModel;
    const workspaceId = localStorage.getItem("workspace_id");

    try {
      setSubmittingKey(true);
      // Calls updated payload with mandatory workspace isolation verification checks
      await apiKeyApi.connectKey(activeProviderForm, inputKey.trim(), workspaceId, agentId, chosenModel);
      
      // Automatically trigger the /set-default configuration for this specific agent's scope
      await apiKeyApi.setDefaultProvider(activeProviderForm, workspaceId, chosenModel, agentId);

      toast.success(`Private ${providerMeta[activeProviderForm].name} credential override assigned cleanly!`);
      setInputKey("");
      setActiveProviderForm(null);
      await syncAgentStatuses();
    } catch (err: any) {
      toast.error(err.message || "Failed to finalize encryption override configuration handshake.");
    } finally {
      setSubmittingKey(false);
    }
  }

  async function handleRemoveAgentOverride(providerKey: "gemini" | "openai") {
    if (!agentId) return;
    if (!window.confirm(`Delete private ${providerMeta[providerKey].name} credential overrides? This will immediately revert this agent back to standard Workspace configurations.`)) return;
    
    const workspaceId = localStorage.getItem("workspace_id");
    const chosenModel = providerKey === "gemini" ? selectedGeminiModel : selectedOpenAIModel;
    
    try {
      setSubmittingKey(true);
      await apiKeyApi.disconnectKey(providerKey, workspaceId, agentId, chosenModel);
      toast.success(`Private ${providerMeta[providerKey].name} mapping deleted. Reverted to shared workspace assets.`);
      
      if (providerKey === "gemini") setGeminiStatus({ connected: false, last_updated: "", masked_key: "" });
      else setOpenaiStatus({ connected: false, last_updated: "", masked_key: "" });
      
      await syncAgentStatuses();
      setActiveProviderForm(null);
    } catch (err: any) {
      toast.error(err.message || "Failed to drop custom target row mapping.");
    } finally {
      setSubmittingKey(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[#071018] text-white flex items-center justify-center">
        <div className="flex items-center gap-4 rounded-3xl border border-cyan-500/20 bg-cyan-500/10 px-8 py-6">
          <Loader2 className="animate-spin text-cyan-300" size={24} />
          <span className="text-xl font-bold text-cyan-300 tracking-tight">Syncing Agent Cryptographic Context...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#071018] text-white p-8 space-y-10 animate-fadeIn">
      
      {/* HEADER SECTION */}
      <div className="flex items-start justify-between gap-6 flex-wrap">
        <div>
          <h1 className="text-6xl font-black text-cyan-400 tracking-tight">
            {agentName} Credentials
          </h1>
          <p className="mt-2 text-gray-400">
            Configure private AI console tokens to insulate this sandbox execution stream.
          </p>
          <div className="inline-flex items-center gap-3 rounded-full border border-yellow-500/20 bg-yellow-500/10 text-yellow-300 px-5 py-2.5 mt-5 text-xs font-medium font-sans">
            <div className="h-1.5 w-1.5 rounded-full bg-yellow-400 animate-pulse" />
            <span>If unconfigured, runtime defaults automatically fall back onto shared Workspace parameters.</span>
          </div>
        </div>

        <div className="flex items-center gap-4 flex-wrap">
          <button 
            type="button"
            onClick={syncAgentStatuses} 
            className="rounded-2xl border border-cyan-500/20 bg-cyan-500/10 px-6 py-4 font-bold text-cyan-300 hover:bg-cyan-500/20 transition-all"
          >
            Refresh Context
          </button>
          <Link 
            href={`/agent/${agentId}`} 
            className="rounded-2xl border border-cyan-400 px-8 py-4 font-bold hover:bg-cyan-400 hover:text-black transition-all"
          >
            Back To Agent
          </Link>
        </div>
      </div>

      {/* PROVIDER PLATES GRID DISPLAY LOOP */}
      <div className="grid gap-8 lg:grid-cols-2">
        
        {/* plate 1: GOOGLE GEMINI SANDBOX OVERRIDE */}
        <div className={`rounded-3xl border p-8 transition-all duration-300 bg-[#09131f] ${geminiStatus.connected ? 'border-green-500/20 ring-1 ring-green-500/5' : 'border-cyan-500/30'}`}>
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="h-14 w-14 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-300 shrink-0">
                <KeyRound size={24} />
              </div>
              <div className="space-y-1.5">
                <h3 className="text-3xl font-black text-white">Google Gemini</h3>
                <div className="flex flex-wrap items-center gap-x-4 text-xs font-mono text-gray-500">
                  <div>Override Status: {geminiStatus.connected ? <span className="text-green-400 font-bold">ACTIVE OVERRIDE</span> : <span className="text-gray-500">INHERITING WORKSPACE</span>}</div>
                </div>
              </div>
            </div>
            <a href={providerMeta.gemini.link} target="_blank" rel="noreferrer" className="rounded-xl border border-white/10 p-2.5 text-zinc-400 hover:bg-white/5 transition-colors"><ExternalLink size={16} /></a>
          </div>

          {geminiStatus.connected && (
            <div className="mt-6 font-sans flex items-center justify-between p-4 bg-black rounded-xl border border-slate-800/60 text-xs text-zinc-400">
              <div className="font-mono text-[11px] bg-slate-900 px-2 py-1 rounded text-zinc-300 border border-slate-800/40">{geminiStatus.masked_key}</div>
              <div className="flex items-center gap-1"><Calendar size={12} /> Sync: {geminiStatus.last_updated}</div>
            </div>
          )}

          {/* DYNAMIC DEPENDENT dropdown selector */}
          <div className="mt-6 space-y-2 font-sans text-xs">
            <p className="text-zinc-400 font-medium">Model Variant Execution Target:</p>
            <select
              value={selectedGeminiModel}
              onChange={(e) => setSelectedGeminiModel(e.target.value)}
              className="w-full bg-black border border-slate-800 rounded-xl h-12 px-4 outline-none text-zinc-200 text-xs focus:border-cyan-500/30 font-sans transition-colors"
            >
              {providerMeta.gemini.models.map((model) => (
                <option key={model} value={model}>{model}</option>
              ))}
            </select>
          </div>

          <div className="mt-6 flex gap-3 font-sans text-xs font-bold">
            <button 
              type="button" 
              onClick={() => { setActiveProviderForm("gemini"); setInputKey(""); }} 
              className="flex-1 bg-cyan-400 hover:bg-cyan-300 text-black py-4 rounded-xl transition-all"
            >
              {geminiStatus.connected ? "Update Keys" : "Connect Private Override"}
            </button>
            {geminiStatus.connected && (
              <button 
                type="button" 
                onClick={() => handleRemoveAgentOverride("gemini")} 
                className="px-4 bg-red-500/10 border border-red-500/20 hover:bg-red-500/20 text-red-400 rounded-xl transition-all flex items-center justify-center"
              >
                <Trash2 size={16} />
              </button>
            )}
          </div>
        </div>

        {/* plate 2: OPENAI CORE SANDBOX OVERRIDE */}
        <div className={`rounded-3xl border p-8 transition-all duration-300 bg-[#09131f] ${openaiStatus.connected ? 'border-green-500/20 ring-1 ring-green-500/5' : 'border-cyan-500/30'}`}>
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="h-14 w-14 rounded-2xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 shrink-0">
                <Cpu size={24} />
              </div>
              <div className="space-y-1.5">
                <h3 className="text-3xl font-black text-white">OpenAI Engine</h3>
                <div className="flex flex-wrap items-center gap-x-4 text-xs font-mono text-gray-500">
                  <div>Override Status: {openaiStatus.connected ? <span className="text-green-400 font-bold">ACTIVE OVERRIDE</span> : <span className="text-gray-500">INHERITING WORKSPACE</span>}</div>
                </div>
              </div>
            </div>
            <a href={providerMeta.openai.link} target="_blank" rel="noreferrer" className="rounded-xl border border-white/10 p-2.5 text-zinc-400 hover:bg-white/5 transition-colors"><ExternalLink size={16} /></a>
          </div>

          {openaiStatus.connected && (
            <div className="mt-6 font-sans flex items-center justify-between p-4 bg-black rounded-xl border border-slate-800/60 text-xs text-zinc-400">
              <div className="font-mono text-[11px] bg-slate-900 px-2 py-1 rounded text-zinc-300 border border-slate-800/40">{openaiStatus.masked_key}</div>
              <div className="flex items-center gap-1"><Calendar size={12} /> Sync: {openaiStatus.last_updated}</div>
            </div>
          )}

          {/* DYNAMIC DEPENDENT dropdown selector */}
          <div className="mt-6 space-y-2 font-sans text-xs">
            <p className="text-zinc-400 font-medium">Model Variant Execution Target:</p>
            <select
              value={selectedOpenAIModel}
              onChange={(e) => setSelectedOpenAIModel(e.target.value)}
              className="w-full bg-black border border-slate-800 rounded-xl h-12 px-4 outline-none text-zinc-200 text-xs focus:border-cyan-500/30 font-sans transition-colors"
            >
              {providerMeta.openai.models.map((model) => (
                <option key={model} value={model}>{model}</option>
              ))}
            </select>
          </div>

          <div className="mt-6 flex gap-3 font-sans text-xs font-bold">
            <button 
              type="button" 
              onClick={() => { setActiveProviderForm("openai"); setInputKey(""); }} 
              className="flex-1 bg-cyan-400 hover:bg-cyan-300 text-black py-4 rounded-xl transition-all"
            >
              {openaiStatus.connected ? "Update Keys" : "Connect Private Override"}
            </button>
            {openaiStatus.connected && (
              <button 
                type="button" 
                onClick={() => handleRemoveAgentOverride("openai")} 
                className="px-4 bg-red-500/10 border border-red-500/20 hover:bg-red-500/20 text-red-400 rounded-xl transition-all flex items-center justify-center"
              >
                <Trash2 size={16} />
              </button>
            )}
          </div>
        </div>

      </div>

      {/* COLLAPSIBLE ENCRYPTED TRANSACTION TERMINAL INPUT BOX */}
      {activeProviderForm && (
        <form onSubmit={handleConnectAgentKey} className="p-8 bg-[#040c18] border border-cyan-500/20 rounded-3xl flex flex-col sm:flex-row gap-4 font-mono text-xs items-center animate-fadeIn">
          <div className="relative flex-1 w-full flex items-center">
            <input
              type={hideTokenInput ? "password" : "text"}
              value={inputKey}
              onChange={(e) => setInputKey(e.target.value)}
              placeholder={providerMeta[activeProviderForm].placeholder}
              className="w-full bg-black border border-slate-800 rounded-2xl h-14 px-5 pr-14 text-white outline-none focus:border-cyan-500/50 text-sm font-sans tracking-wide"
            />
            <button
              type="button"
              onClick={() => setHideTokenInput(!hideTokenInput)}
              className="absolute right-5 text-zinc-500 hover:text-zinc-300 transition-colors"
            >
              {hideTokenInput ? <Eye size={18} /> : <EyeOff size={18} />}
            </button>
          </div>
          
          <div className="flex gap-3 font-sans text-sm font-bold w-full sm:w-auto shrink-0">
            <button
              type="submit"
              disabled={submittingKey || !inputKey.trim()}
              className="w-full sm:w-auto bg-cyan-400 hover:bg-cyan-300 text-black px-6 h-14 rounded-2xl transition-all disabled:opacity-40 whitespace-nowrap"
            >
              {submittingKey ? "Encrypting Token..." : `Save ${providerMeta[activeProviderForm].name} Override`}
            </button>
            <button
              type="button"
              onClick={() => {
                setActiveProviderForm(null);
                setInputKey("");
              }}
              className="w-full sm:w-auto bg-transparent border border-slate-800 text-zinc-400 px-5 h-14 rounded-2xl hover:bg-zinc-900 transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

    </div>
  );
}