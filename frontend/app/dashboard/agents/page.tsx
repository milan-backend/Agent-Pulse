"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { 
  ChevronRight, 
  Plus, 
  Copy, 
  X,
  Sliders,
  ChevronDown,
  ChevronUp
} from "lucide-react";
import { toast } from "sonner";
import { createAgent, getDashboardAgents } from "@/components/api";

interface Agent {
  id: string;
  name: string;
}

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [agentName, setAgentName] = useState("");
  const [creating, setCreating] = useState(false);
  const [newApiKey, setNewApiKey] = useState("");
  const [newAgentName, setNewAgentName] = useState("");
  const [role, setRole] = useState("");

  // New states to handle multi-tier provider key generation immediately on create
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [apiProvider, setApiProvider] = useState<"gemini" | "openai">("gemini");
  const [agentApiKey, setAgentApiKey] = useState("");
  const [modelVersion, setModelVersion] = useState("gemini-2.5-flash-lite");

  const modelOptions = {
    gemini: ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro", "gemini-1.5-pro"],
    openai: ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "o1-mini"]
  };

  useEffect(() => {
    fetchAgents();
  }, []);

  // Sync state model variants when provider selection is toggled
  useEffect(() => {
    setModelVersion(modelOptions[apiProvider][0]);
  }, [apiProvider]);

  async function fetchAgents() {
    try {
      const data = await getDashboardAgents();
      setAgents(data?.agents || data || []);
      setRole(data?.role || "viewer");
    } catch (error) {
      console.error(error);
      toast.error("Failed to fetch agents");
    } finally {
      setLoading(false);
    }
  }

  async function createNewAgent() {
    try {
      setCreating(true);

      const payload: any = {
        name: agentName
      };

      // Only pass integration tokens if the user expanded advanced mode and input values
      if (showAdvanced && agentApiKey.trim()) {
        payload.api_provider = apiProvider;
        payload.agent_api_key = agentApiKey.trim();
        payload.model_version = modelVersion;
      }

      const data = await createAgent(payload);

      setNewApiKey(data?.api_key || "");
      setNewAgentName(data?.agent_name || agentName);

      toast.success("Agent created successfully");
      
      // Reset variables cleanly
      setAgentName("");
      setAgentApiKey("");
      setShowAdvanced(false);
      setApiProvider("gemini");

      fetchAgents();
    } catch (error: any) {
      console.error(error);
      toast.error(error.message || "Failed to create agent");
    } finally {
      setCreating(false);
    }
  }

  async function copyApiKey() {
    await navigator.clipboard.writeText(newApiKey);
    toast.success("API Key copied");
  }

  return (
    <main className="min-h-screen bg-[#050816] text-white p-10">
      
      {/* HEADER */}
      <div className="mb-10 flex items-center justify-between flex-wrap gap-6">
        <div>
          <h1 className="text-6xl font-black tracking-tight">Agents</h1>
          <p className="mt-3 text-zinc-400 text-lg">Runtime agent infrastructure overview.</p>
        </div>

        <div className="flex items-center gap-4 flex-wrap">
          {/* CREATE AGENT */}
          {["admin", "operator"].includes(role?.toLowerCase?.() || "") && (
            <button
              onClick={() => setShowModal(true)}
              className="flex items-center gap-3 rounded-2xl border border-cyan-500/20 bg-cyan-500/10 px-6 py-4 text-cyan-300 transition hover:bg-cyan-500/20"
            >
              <Plus size={20} />
              <span className="font-bold">Create Agent</span>
            </button>
          )}

          {/* TOTAL */}
          <div className="rounded-3xl border border-cyan-500/20 bg-cyan-500/10 px-8 py-6">
            <p className="text-sm text-zinc-400">Total Agents</p>
            <h2 className="mt-2 text-5xl font-black text-cyan-300">{agents.length}</h2>
          </div>
        </div>
      </div>

      {/* LOADING */}
      {loading ? (
        <div className="rounded-3xl border border-cyan-500/10 bg-[#08111f] p-10 text-zinc-400">
          Loading agents...
        </div>
      ) : agents.length === 0 ? (
        <div className="flex h-[400px] items-center justify-center rounded-3xl border border-cyan-500/10 bg-[#08111f]">
          <div className="text-center">
            <h2 className="text-4xl font-black text-zinc-300">No Agents Found</h2>
            <p className="mt-4 text-zinc-500">Create your first runtime agent.</p>
          </div>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
          {agents.map((agent) => (
            <Link key={agent.id} href={`/agent/${agent.id}`}>
              <div className="group rounded-3xl border border-cyan-500/10 bg-[#08111f] p-8 transition-all hover:border-cyan-400/40 hover:bg-cyan-500/5">
                <div className="flex items-start justify-between">
                  <div>
                    <h2 className="text-3xl font-black text-cyan-300">{agent.name}</h2>
                    <p className="mt-4 break-all text-sm text-zinc-500">{agent.id}</p>
                  </div>
                  <div className="rounded-2xl border border-cyan-500/20 bg-cyan-500/10 p-3 text-cyan-300 transition-all group-hover:translate-x-1">
                    <ChevronRight />
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}

      {/* MODAL */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-6 overflow-y-auto">
          <div className="w-full max-w-xl rounded-3xl border border-cyan-500/20 bg-[#08111f] p-8 my-8 transition-all duration-300">
            
            {/* HEADER */}
            <div className="mb-6 flex items-center justify-between">
              <h2 className="text-4xl font-black">Create Agent</h2>
              <button
                disabled={creating}
                onClick={() => {
                  setShowModal(false);
                  setNewApiKey("");
                  setNewAgentName("");
                  setAgentName("");
                  setAgentApiKey("");
                  setShowAdvanced(false);
                }}
                className="rounded-xl border border-white/10 p-2 text-zinc-400 hover:bg-white/5"
              >
                <X />
              </button>
            </div>

            {/* FORM */}
            {!newApiKey ? (
              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-mono text-zinc-400 uppercase tracking-wider mb-2">Agent Name</label>
                  <input
                    value={agentName}
                    onChange={(e) => setAgentName(e.target.value)}
                    placeholder="E.g., Research-Bot"
                    className="w-full rounded-2xl border border-cyan-500/20 bg-black/30 px-5 py-4 text-lg outline-none focus:border-cyan-500/50 transition-colors text-white"
                  />
                </div>

                {/* ADVANCED ROUTING OVERRIDES DROPDOWN SLIDER */}
                <div className="pt-2">
                  <button
                    type="button"
                    onClick={() => setShowAdvanced(!showAdvanced)}
                    className="flex items-center justify-between w-full p-4 rounded-xl border border-slate-800 bg-slate-950/40 hover:bg-slate-950 text-zinc-400 hover:text-white transition-all font-sans text-xs font-semibold"
                  >
                    <div className="flex items-center gap-2">
                      <Sliders size={14} className="text-cyan-400" />
                      <span>Configure Private Credentials Override (Optional)</span>
                    </div>
                    {showAdvanced ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                  </button>

                  {showAdvanced && (
                    <div className="mt-3 p-4 rounded-2xl border border-slate-800 bg-black/20 space-y-4 animate-fadeIn">
                      
                      {/* PROVIDER ENGINE SWITCHER */}
                      <div>
                        <label className="block text-[11px] font-mono text-zinc-500 uppercase tracking-wider mb-1.5">API Provider</label>
                        <div className="grid grid-cols-2 gap-2 text-xs font-sans font-bold">
                          <button
                            type="button"
                            onClick={() => setApiProvider("gemini")}
                            className={`h-10 rounded-xl border transition-all ${apiProvider === "gemini" ? "bg-cyan-500/10 border-cyan-400 text-cyan-300" : "bg-transparent border-slate-800 text-zinc-500 hover:text-zinc-300"}`}
                          >
                            Google Gemini
                          </button>
                          <button
                            type="button"
                            onClick={() => setApiProvider("openai")}
                            className={`h-10 rounded-xl border transition-all ${apiProvider === "openai" ? "bg-purple-500/10 border-purple-400 text-purple-300" : "bg-transparent border-slate-800 text-zinc-500 hover:text-zinc-300"}`}
                          >
                            OpenAI Core
                          </button>
                        </div>
                      </div>

                      {/* PRIVATE TOKEN INPUT FIELD */}
                      <div>
                        <label className="block text-[11px] font-mono text-zinc-500 uppercase tracking-wider mb-1.5">Private Provider Token</label>
                        <input
                          type="password"
                          value={agentApiKey}
                          onChange={(e) => setAgentApiKey(e.target.value)}
                          placeholder={apiProvider === "gemini" ? "Enter AI Studio key (AIzaSy...)" : "Enter OpenAI key (sk-proj-...)"}
                          className="w-full bg-slate-950 border border-slate-800 rounded-xl h-11 px-4 text-white outline-none focus:border-cyan-500/30 text-xs font-sans"
                        />
                      </div>

                      {/* MODEL SELECTION DROPDOWN FIELD */}
                      <div>
                        <label className="block text-[11px] font-mono text-zinc-500 uppercase tracking-wider mb-1.5">Model Dropdown Variant</label>
                        <select
                          value={modelVersion}
                          onChange={(e) => setModelVersion(e.target.value)}
                          className="w-full bg-slate-950 border border-slate-800 text-zinc-300 rounded-xl h-11 px-4 text-xs outline-none focus:border-cyan-500/30 font-sans transition-colors"
                        >
                          {modelOptions[apiProvider].map((model) => (
                            <option key={model} value={model}>{model}</option>
                          ))}
                        </select>
                      </div>

                    </div>
                  )}
                </div>

                <button
                  onClick={createNewAgent}
                  disabled={creating || !agentName.trim()}
                  className="w-full rounded-2xl bg-cyan-500 px-6 py-4 text-lg font-black text-black transition hover:bg-cyan-400 disabled:opacity-50"
                >
                  {creating ? "Creating..." : "Create Agent"}
                </button>
              </div>
            ) : (
              <div className="space-y-4 animate-fadeIn">
                <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/10 p-6">
                  <h3 className="text-2xl font-black text-emerald-300">Agent Created</h3>
                  <p className="mt-3 text-cyan-300 font-bold">{newAgentName}</p>
                  <p className="mt-2 text-zinc-400 text-xs font-sans">
                    Save this API key now. You will not be able to see it again.
                  </p>
                  <div className="mt-6 rounded-2xl border border-white/10 bg-black/30 p-5 break-all text-sm font-mono">
                    {newApiKey}
                  </div>
                  <button
                    onClick={copyApiKey}
                    className="mt-5 flex items-center gap-3 rounded-2xl border border-cyan-500/20 bg-cyan-500/10 px-5 py-3 text-cyan-300 font-sans font-bold text-xs"
                  >
                    <Copy size={18} />
                    Copy API Key
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </main>
  );
}