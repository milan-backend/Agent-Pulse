"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { 
  ChevronRight, 
  Plus, 
  Copy, 
  X,
  AlertTriangle,
  ArrowUpRight,
  Timer
} from "lucide-react";
import { toast } from "sonner";
import { createAgent, getDashboardAgents } from "@/components/api";

interface Agent {
  id: string;
  name: string;
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

  // 🟢 DYNAMIC BACKEND DATABASE TELEMETRY CONFIGURATION STATES
  const [workspaceRuntimeHours, setWorkspaceRuntimeHours] = useState(0);
  const [runtimeLimitHours, setRuntimeLimitHours] = useState(10.0); // Safe database fallback default
  const [planTier, setPlanTier] = useState("FREE");

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

      // 🟢 EXTRACT DYNAMIC BOUNDARY TELEMETRY RETURNED NATIVELY FROM THE POSTGRES CORES
      const parsedRuntimeMs = data?.workspace_total_runtime_ms ?? 0;
      const parsedLimitHours = data?.workspace_runtime_limit_hours ?? 10.0;
      const parsedTier = data?.plan_tier ?? "FREE";

      setWorkspaceRuntimeHours(parsedRuntimeMs / 3600000.0); // Exact mathematical transformation to hours
      setRuntimeLimitHours(Number(parsedLimitHours));
      setPlanTier(parsedTier.toUpperCase());

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

  // 🟢 LIVE EVALUATION OF RESTRICTION METRICS (NO FRONTEND HARDCODING)
  const isRuntimeExceeded = workspaceRuntimeHours >= runtimeLimitHours;
  const runtimePercentage = Math.min((workspaceRuntimeHours / runtimeLimitHours) * 100, 100);

  return (
    <main className="min-h-screen bg-[#050816] text-white p-10">
      
      {/* HEADER */}
      <div className="mb-10 flex items-center justify-between flex-wrap gap-6">
        <div>
          <h1 className="text-6xl font-black tracking-tight">Agents</h1>
          <p className="mt-3 text-zinc-400 text-lg">Runtime agent infrastructure overview.</p>
        </div>

        <div className="flex items-center gap-4 flex-wrap">
          {/* CREATE AGENT BUTTON (Natively locks down action if dynamic runtime quota is depleted) */}
          {["admin", "operator"].includes(role?.toLowerCase?.() || "") && (
            <button
              disabled={isRuntimeExceeded}
              onClick={() => setShowModal(true)}
              className="flex items-center gap-3 rounded-2xl border border-cyan-500/20 bg-cyan-500/10 px-6 py-4 text-cyan-300 transition hover:bg-cyan-500/20 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:bg-cyan-500/10"
            >
              <Plus size={20} />
              <span className="font-bold">{isRuntimeExceeded ? "Runtime Locked" : "Create Agent"}</span>
            </button>
          )}

          {/* TOTAL HUD COUNTER */}
          <div className="rounded-3xl border border-cyan-500/20 bg-cyan-500/10 px-8 py-6">
            <p className="text-sm text-zinc-400">Total Agents</p>
            <h2 className="mt-2 text-5xl font-black text-cyan-300">{agents.length}</h2>
          </div>
        </div>
      </div>

      {/* 💥 ADAPTIVE SYSTEM ALERTS BLOCK - TRIP LABELS DYNAMICALLY FOR THE EXACT DETECTED PLAN LEVEL */}
      {isRuntimeExceeded && (
        <div className="mb-6 w-full rounded-3xl border border-red-500/20 bg-gradient-to-r from-red-950/40 to-red-900/10 p-5 shadow-[0_0_30px_rgba(239,68,68,0.05)] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 animate-fade-in">
          <div className="flex items-start gap-4 min-w-0">
            <div className="h-12 w-12 rounded-2xl bg-red-500/10 border border-red-500/20 flex items-center justify-center shrink-0 text-red-400 shadow-[0_0_15px_rgba(239,68,68,0.1)]">
              <AlertTriangle size={22} className="animate-pulse" />
            </div>
            <div className="min-w-0">
              <h3 className="text-lg font-black tracking-tight text-red-200">
                Workspace Runtime Quota Exhausted ({planTier} PLAN)
              </h3>
              <p className="text-sm text-zinc-400 mt-0.5 font-medium leading-relaxed">
                Your background orchestration instances have registered a cumulative runtime of <span className="text-red-400 font-bold">{workspaceRuntimeHours.toFixed(1)} hours</span>, crossing your workspace's designated database limit of <span className="text-zinc-300 font-semibold">{runtimeLimitHours.toFixed(1)} hours</span>. Step loop tasks are safely put on hold until deployment scale updates.
              </p>
            </div>
          </div>
          
          <Link 
            href="/dashboard/billing"
            className="shrink-0 flex items-center gap-2 rounded-xl bg-red-500 px-5 py-3 text-sm font-bold text-white transition-all hover:bg-red-600 shadow-md active:scale-95"
          >
            <span>Upgrade Infrastructure</span>
            <ArrowUpRight size={16} />
          </Link>
        </div>
      )}

      {/* 📊 THE LIVE CYBERPUNK WORKSPACE RUNTIME PROGRESS BOX */}
      {!loading && (
        <div className="mb-10 w-full bg-[#08111f]/30 border border-cyan-500/5 p-6 rounded-3xl backdrop-blur-sm">
          <div className="space-y-3">
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2 text-zinc-400 font-medium">
                <Timer size={16} className="text-cyan-400" />
                <span>Cumulative Workspace Runtime Usage (<span className="text-cyan-300 font-mono text-xs tracking-wider">{planTier} ACCOUNT</span>)</span>
              </div>
              <span className={isRuntimeExceeded ? "text-red-400 font-bold text-base" : "text-cyan-300 font-bold text-base"}>
                {workspaceRuntimeHours.toFixed(1)} hrs / {runtimeLimitHours.toFixed(1)} hrs
              </span>
            </div>
            
            {/* Visual Fluid Progress Tracking Bar System */}
            <div className="w-full h-3 bg-black/40 rounded-full overflow-hidden border border-white/5">
              <div 
                className={`h-full rounded-full transition-all duration-500 ${isRuntimeExceeded ? "bg-red-500 shadow-[0_0_12px_#ef4444]" : "bg-cyan-500 shadow-[0_0_12px_#06b6d4]"}`}
                style={{ width: `${runtimePercentage}%` }}
              />
            </div>
          </div>
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