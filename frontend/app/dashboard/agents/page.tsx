"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { 
  ChevronRight, 
  Plus, 
  Copy, 
  X,
  AlertTriangle,
  ArrowUpRight
} from "lucide-react";
import { toast } from "sonner";
import { createAgent, getDashboardAgents } from "@/components/api";

interface Agent {
  id: string;
  name: string;
  // If your endpoint yields individual costs or runtimes, we map them optionally
  total_cost?: number; 
  execution_time_ms?: number;
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

  // 🟢 SUBSCRIPTION TELEMETRY STATE (Calculated dynamically on the fly)
  const [workspaceCost, setWorkspaceCost] = useState(0);
  const [workspaceRuntimeHours, setWorkspaceRuntimeHours] = useState(0);

  useEffect(() => {
    fetchAgents();
  }, []);

  async function fetchAgents() {
    try {
      setLoading(true);
      const data = await getDashboardAgents();
      const agentList: Agent[] = data?.agents || data || [];
      setAgents(agentList);
      setRole(data?.role || "viewer");

      // 🟢 COMPUTE LIMITS DIRECTLY FROM DATA TO REUSE EXISTING ENDPOINT PIPELINES
      // If the dashboard array provides metadata loops, we parse them automatically.
      // For your active forced backend database simulation row, your database handles validation out-of-band!
      // We read the global simulation variables cleanly or catch them on pings.
      const parsedCost = data?.workspace_total_cost ?? data?.total_cost ?? 0;
      const parsedRuntimeMs = data?.workspace_total_runtime_ms ?? 0;

      setWorkspaceCost(Number(parsedCost));
      setWorkspaceRuntimeHours(parsedRuntimeMs / 3600000.0);

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

      const data = await createAgent(payload);

      setNewApiKey(data?.api_key || "");
      setNewAgentName(data?.agent_name || agentName);

      toast.success("Agent created successfully");
      
      // Reset variables cleanly
      setAgentName("");

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

  // 🟢 FREE TIER LIMIT THRESHOLDS SETUP
  const COST_LIMIT = 5.0;
  const RUNTIME_LIMIT = 10.0;

  // Since you forced the live database simulation row to $6.00 / 11 hours, 
  // your backend will naturally pass or drop metrics into the view payload parameters.
  // We explicitly trigger flags based on data context:
  const isCostExceeded = workspaceCost >= COST_LIMIT;
  const isRuntimeExceeded = workspaceRuntimeHours >= RUNTIME_LIMIT;
  const isWorkspaceRestricted = isCostExceeded || isRuntimeExceeded;

  return (
    <main className="min-h-screen bg-[#050816] text-white p-10">
      
      {/* HEADER */}
      <div className="mb-10 flex items-center justify-between flex-wrap gap-6">
        <div>
          <h1 className="text-6xl font-black tracking-tight">Agents</h1>
          <p className="mt-3 text-zinc-400 text-lg">Runtime agent infrastructure overview.</p>
        </div>

        <div className="flex items-center gap-4 flex-wrap">
          {/* CREATE AGENT BUTTON (Auto-disabled if layout restriction flags trigger) */}
          {["admin", "operator"].includes(role?.toLowerCase?.() || "") && (
            <button
              disabled={isWorkspaceRestricted}
              onClick={() => setShowModal(true)}
              className="flex items-center gap-3 rounded-2xl border border-cyan-500/20 bg-cyan-500/10 px-6 py-4 text-cyan-300 transition hover:bg-cyan-500/20 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:bg-cyan-500/10"
            >
              <Plus size={20} />
              <span className="font-bold">{isWorkspaceRestricted ? "Creation Blocked" : "Create Agent"}</span>
            </button>
          )}

          {/* TOTAL */}
          <div className="rounded-3xl border border-cyan-500/20 bg-cyan-500/10 px-8 py-6">
            <p className="text-sm text-zinc-400">Total Agents</p>
            <h2 className="mt-2 text-5xl font-black text-cyan-300">{agents.length}</h2>
          </div>
        </div>
      </div>

      {/* 💥 THE PREMIUM GLOWING ALERTS BANNER BLOCK */}
      {isWorkspaceRestricted && (
        <div className="mb-10 w-full rounded-3xl border border-red-500/20 bg-gradient-to-r from-red-950/40 to-red-900/10 p-5 shadow-[0_0_30px_rgba(239,68,68,0.05)] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 animate-fade-in">
          <div className="flex items-start gap-4 min-w-0">
            <div className="h-12 w-12 rounded-2xl bg-red-500/10 border border-red-500/20 flex items-center justify-center shrink-0 text-red-400 shadow-[0_0_15px_rgba(239,68,68,0.1)]">
              <AlertTriangle size={22} className="animate-pulse" />
            </div>
            <div className="min-w-0">
              <h3 className="text-lg font-black tracking-tight text-red-200">
                {isRuntimeExceeded ? "Workspace Runtime Limit Exhausted" : "Free Tier Sandbox Wallet Exhausted"}
              </h3>
              <p className="text-sm text-zinc-400 mt-0.5 font-medium leading-relaxed">
                {isRuntimeExceeded ? (
                  <>Your background automation instances have registered a cumulative runtime of <span className="text-red-400 font-bold">{workspaceRuntimeHours.toFixed(1)} hours</span>, crossing your designated <span className="text-zinc-300 font-semibold">{RUNTIME_LIMIT} hr restriction</span>.</>
                ) : (
                  <>Your background automation instances have registered a cumulative cost of <span className="text-red-400 font-bold">${workspaceCost.toFixed(2)}</span>, crossing your designated <span className="text-zinc-300 font-semibold">${COST_LIMIT.toFixed(2)} sandbox restriction</span>.</>
                )}
                {" "}Task processing states have been temporarily locked across all active channels.
              </p>
            </div>
          </div>
          
          <Link 
            href="/dashboard/billing" // 🎯 Set cleanly to your production billing route!
            className="shrink-0 flex items-center gap-2 rounded-xl bg-red-500 px-5 py-3 text-sm font-bold text-white transition-all hover:bg-red-600 shadow-md active:scale-95"
          >
            <span>Upgrade Plan</span>
            <ArrowUpRight size={16} />
          </Link>
        </div>
      )}

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
                    <h2 className="text-3xl font-black text-cyan-300 transition-colors group-hover:text-cyan-400">{agent.name}</h2>
                    <p className="mt-4 break-all text-sm text-zinc-500 font-mono">{agent.id}</p>
                  </div>
                  <div className="rounded-2xl border border-cyan-500/20 bg-cyan-500/10 p-3 text-cyan-300 transition-all group-hover:translate-x-1 group-hover:border-cyan-400/40 group-hover:bg-cyan-500/20">
                    <ChevronRight size={18} />
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
                }}
                className="rounded-xl border border-white/10 p-2 text-zinc-400 hover:bg-white/5"
              >
                <X />
              </button>
            </div>

            {/* FORM */}
            {!newApiKey ? (
              <div className="space-y-6">
                <div>
                  <label className="block text-xs font-mono text-zinc-400 uppercase tracking-wider mb-2">Agent Name</label>
                  <input
                    value={agentName}
                    onChange={(e) => setAgentName(e.target.value)}
                    placeholder="E.g., Research-Bot"
                    className="w-full rounded-2xl border border-cyan-500/20 bg-black/30 px-5 py-4 text-lg outline-none focus:border-cyan-500/50 transition-colors text-white"
                  />
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