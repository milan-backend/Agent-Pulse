"use client";

import React, { useState, useEffect } from "react";
import { useParams} from "next/navigation";
import Link from "next/link";
import { 
  Cpu, 
  Database, 
  BrainCircuit, 
  Terminal, 
  CheckCircle2, 
  XCircle, 
  Search, 
  Activity, 
  Clock, 
  ArrowLeft,
  Loader2,
  SlidersHorizontal,
  ChevronRight,
  AlertCircle,
  Pause,
  Settings,
  KeyRound,
  FileText
} from "lucide-react";
import { getAgentPipelineHistory, getAgent, pauseAgentMission } from "@/components/api";
import { toast } from "sonner";

interface Agent {
  id: string;
  name: string;
  is_active: boolean;
  total_cost: number;
}

interface PipelineStep {
  step_id: string;
  task_name: string;
  status: string;
  error_message: string | null;
  created_at: string | null;
  execution_time_ms: number;
}

export default function AgentMonitorControlRoom() {
  const params = useParams();
  const agentId = params?.agent_id as string;

  // Agent Global States (Preserved from original page.tsx)
  const [agent, setAgent] = useState<Agent | null>(null);
  const [pausing, setPausing] = useState(false);
  const [loadingAgent, setLoadingAgent] = useState(true);

  // Pipeline Monitor Layout States
  const [pipelines, setPipelines] = useState<PipelineStep[]>([]);
  const [loadingPipelines, setLoadingPipelines] = useState(true);
  
  // Filtering Controllers State
  const [statusFilter, setStatusFilter] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");

  const [selectedPipelineId, setSelectedPipelineId] = useState<string | null>(null);
  const [activePipeline, setActivePipeline] = useState<PipelineStep | null>(null);

  // Debounce search inputs
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearch(searchQuery), 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Sync Agent Data for the Roster Sidebar
  async function fetchAgentData() {
    try {
      setLoadingAgent(true);
      const response = await getAgent(agentId);
      const agentData = response?.agent || response;
      setAgent({
        id: agentData?.id || "",
        name: agentData?.name || "Unknown Agent",
        is_active: agentData?.is_active ?? false,
        total_cost: Number(response?.total_cost || 0),
      });
    } catch (error) {
      console.error(error);
      toast.error("Failed to load agent metrics");
    } finally {
      setLoadingAgent(false);
    }
  }

  // Sync Pipeline Data List
  async function syncPipelineFeeds() {
    try {
      if (!agentId) return;
      const data = await getAgentPipelineHistory(agentId, {
        status: statusFilter,
        search: debouncedSearch
      });
      const items = data?.pipelines || [];
      setPipelines(items);

      if (selectedPipelineId) {
        const currentMatch = items.find((p: PipelineStep) => p.step_id === selectedPipelineId);
        if (currentMatch) setActivePipeline(currentMatch);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingPipelines(false);
    }
  }

  useEffect(() => {
    if (agentId) {
      fetchAgentData();
    }
  }, [agentId]);

  useEffect(() => {
    syncPipelineFeeds();
  }, [agentId, statusFilter, debouncedSearch, selectedPipelineId]);

  // Pause Handler (Preserved from original page.tsx)
  async function pauseAgent() {
    try {
      setPausing(true);
      await pauseAgentMission(agentId);
      toast.success("Agent paused");
      if (agent) setAgent({ ...agent, is_active: false });
    } catch (error) {
      console.error(error);
      toast.error("Failed to pause agent");
    } finally {
      setPausing(false);
    }
  }

  const handleInspectNode = (pipe: PipelineStep) => {
    setActivePipeline(pipe);
    setSelectedPipelineId(pipe.step_id);
  };

  const COST_THRESHOLD = 5.0; //
  const isLimitExceeded = agent ? agent.total_cost >= COST_THRESHOLD : false; //

  if (loadingAgent || !agent) {
    return (
      <div className="min-h-screen bg-[#020817] text-white flex items-center justify-center">
        <div className="rounded-3xl border border-cyan-500/10 bg-[#08111f] px-10 py-8 text-zinc-400 font-mono text-xs animate-pulse">
          SYNCING SIDEBAR PERMISSIONS...
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen w-screen bg-[#020817] text-white flex overflow-hidden select-none">
      
      {/* 🟢 FIXED AGENT SIDEBAR: Preserved perfectly from your page.tsx */}
      <aside className="w-[300px] shrink-0 border-r border-cyan-500/10 bg-[#040b18] p-6 flex flex-col justify-between h-full sticky top-0 overflow-y-auto scrollbar-none">
        <div className="space-y-10">
          <div>
            <h1 className="text-5xl font-black">
              <span className="text-cyan-400">Agent</span>
              <span className="text-white">Pulse</span>
            </h1>
            <p className="mt-2 text-zinc-400 text-sm">Runtime Agent Control</p>
          </div>

          <div className="flex flex-col gap-3">  
            <Link href="/dashboard/agents" className="flex items-center gap-3 rounded-2xl bg-[#0b1628] border border-cyan-500/5 px-5 py-4 font-bold transition-all hover:bg-cyan-500/10">  
              <ArrowLeft size={18} className="text-zinc-400" /> 
              <span>Back To Agents</span>  
            </Link>  
            
            <button 
              onClick={pauseAgent} 
              disabled={pausing || isLimitExceeded} 
              className="w-full flex items-center gap-3 rounded-2xl bg-green-500/10 border border-green-500/20 px-5 py-4 font-bold text-green-400 transition-all hover:bg-green-500/20 disabled:opacity-40 disabled:cursor-not-allowed text-left"
            >  
              <Pause size={18} /> 
              <span>{pausing ? "Pausing..." : "Pause Agent"}</span>  
            </button>  
            
            <Link href={`/agent/${agent.id}/settings`} className="flex items-center gap-3 rounded-2xl bg-[#0b1628] border border-cyan-500/5 px-5 py-4 font-bold text-zinc-300 transition-all hover:text-cyan-300 hover:border-cyan-500/20 hover:bg-cyan-500/5">  
              <Settings size={18} className="text-zinc-500" /> 
              <span>Agent Settings</span>  
            </Link>  

            <Link href={`/agent/${agent.id}/provider`} className="flex items-center gap-3 rounded-2xl bg-[#0b1628] border border-cyan-500/5 px-5 py-4 font-bold text-zinc-300 transition-all hover:text-cyan-300 hover:border-cyan-500/20 hover:bg-cyan-500/5">  
              <KeyRound size={18} className="text-zinc-500" /> 
              <span>API Provider</span>  
            </Link>  

            <Link href={`/agent/${agent.id}/knowledge`} className="flex items-center gap-3 rounded-2xl bg-[#0b1628] border border-cyan-500/5 px-5 py-4 font-bold text-zinc-300 transition-all hover:text-emerald-400 hover:border-emerald-500/20 hover:bg-emerald-500/5">  
              <FileText size={18} className="text-zinc-500" /> 
              <span>Agent Knowledge</span>  
            </Link>  
            
            <Link href={`/agent/${agent.id}/tasks`} className="flex items-center gap-3 rounded-2xl bg-[#0b1628] border border-cyan-500/5 px-5 py-4 font-bold text-zinc-300 transition-all hover:text-purple-300 hover:border-purple-500/20 hover:bg-purple-500/5">  
              <Activity size={18} className="text-zinc-500" /> 
              <span>Agent Tasks</span>  
            </Link>

            {/* 🎯 Highlighted active indicator styling matching your core layout */}
            <Link href={`/agent/${agent.id}/monitor`} className="flex items-center gap-3 rounded-2xl bg-cyan-500/15 border border-cyan-400/30 px-5 py-4 font-bold text-cyan-400 shadow-[0_0_20px_rgba(34,211,238,0.1)]">  
              <Cpu size={18} /> 
              <span>Pipeline Monitor</span>  
            </Link>  
          </div>  
        </div>

        <div className="mt-8 mb-2 rounded-3xl border border-cyan-500/20 bg-cyan-500/10 p-6 flex-shrink-0">  
          <p className="text-zinc-400 text-sm">Runtime Status</p>  
          <div className="mt-4 flex items-center justify-between gap-2">  
            <h2 className={`text-3xl xl:text-4xl font-black ${agent.is_active && !isLimitExceeded ? "text-green-300" : "text-red-300"}`}>
              {isLimitExceeded ? "LOCKED" : agent.is_active ? "ACTIVE" : "PAUSED"}
            </h2>  
            <div className={`h-4 w-4 rounded-full shrink-0 ${agent.is_active && !isLimitExceeded ? "bg-green-400 shadow-[0_0_20px_#4ade80]" : "bg-red-400 shadow-[0_0_20px_#f87171]"}`} />  
          </div>  
        </div>  
      </aside>

      {/* MAIN CONTENT VIEWPORT */}
      <main className="flex-1 p-8 overflow-y-auto h-full flex flex-col min-w-0 bg-[#020817] scrollbar-thin scrollbar-thumb-zinc-900">
        <div className="space-y-6">
          
          {/* CONTROL ROOM UPPER PANEL */}
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-[#08111f]/30 border border-cyan-500/5 p-6 rounded-3xl">
            <div className="space-y-1">
              <p className="text-cyan-400 font-mono text-xs tracking-widest font-bold uppercase flex items-center gap-2">
                <Activity size={12} className="animate-pulse" /> Telemetry Control Room
              </p>
              <h1 className="text-3xl font-black tracking-tight">{agent.name.toUpperCase()} • PIPELINES</h1>
            </div>

            {selectedPipelineId && (
              <button
                onClick={() => { setSelectedPipelineId(null); setActivePipeline(null); }}
                className="inline-flex items-center gap-2 px-4 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-xs font-bold text-slate-300 hover:text-white transition-all active:scale-95"
              >
                <ArrowLeft size={14} /> Back to History Search
              </button>
            )}
          </div>

          {/* ------------------------------------------------------------- */}
          {/* VIEW MODE A: VERTICAL TOP-TO-DOWN TRANSPARENT PC HARDWARE VIEW */}
          {/* ------------------------------------------------------------- */}
          {selectedPipelineId && activePipeline ? (
            <div className="relative bg-gradient-to-b from-[#061124]/40 to-[#030914]/40 border-2 border-cyan-500/10 rounded-[32px] p-6 md:p-12 shadow-[0_0_50px_rgba(6,17,40,0.4)] backdrop-blur-xl overflow-hidden animate-fadeIn">
              
              {/* Glass Chassis Aesthetic Overlay Matrices */}
              <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:4rem_4rem] opacity-10 pointer-events-none" />
              <div className="absolute top-0 right-0 left-0 h-[250px] bg-gradient-to-b from-white/[0.02] to-transparent -skew-y-3 origin-top-left pointer-events-none" />
              
              <div className="max-w-md mx-auto flex flex-col items-center space-y-12 relative z-10">
                
                {/* INGESTION BAR NODES BOX */}
                <div className={`w-full flex items-center justify-between gap-4 p-5 rounded-2xl border bg-slate-950/60 ${
                  activePipeline.status !== "pending" ? "border-emerald-500/20 text-emerald-400" : "border-cyan-500/20 text-cyan-400 animate-pulse"
                }`}>
                  <div className="flex items-center gap-4">
                    <Terminal size={20} className={activePipeline.status !== "pending" ? "text-emerald-400" : "text-cyan-400"} />
                    <div>
                      <h4 className="text-xs font-bold font-mono tracking-widest text-white">01 / INGESTION RECEPTOR</h4>
                      <p className="text-[10px] text-zinc-500 font-sans mt-0.5">Payload structures safely parsed into cache maps.</p>
                    </div>
                  </div>
                  <CheckCircle2 size={16} className={activePipeline.status !== "pending" ? "text-emerald-400" : "text-slate-800"} />
                </div>

                {/* Vertical Bus neon line 1 */}
                <div className="w-[2px] h-12 bg-slate-900 relative overflow-hidden">
                  <div className={`absolute top-0 left-0 right-0 h-5 bg-gradient-to-b from-transparent to-cyan-400 rounded animate-marquee-vertical ${
                    activePipeline.status === "running" || activePipeline.status === "completed" ? "block" : "hidden"
                  }`} />
                </div>

                {/* CENTRAL CPU PROCESSOR ENG CORE SOCKET */}
                <div className={`w-full flex items-center justify-between gap-4 p-5 rounded-2xl border bg-slate-950/90 shadow-2xl relative ${
                  activePipeline.status === "completed" ? "border-emerald-500/20 text-emerald-400" :
                  activePipeline.status === "failed" ? "border-rose-500/30 text-rose-400 bg-rose-950/5" :
                  "border-purple-500 text-purple-400 bg-purple-950/5 shadow-[0_0_20px_rgba(168,85,247,0.15)]"
                }`}>
                  <div className="flex items-center gap-4">
                    {activePipeline.status === "running" ? (
                      <BrainCircuit size={20} className="animate-pulse text-purple-400" />
                    ) : activePipeline.status === "failed" ? (
                      <XCircle size={20} className="text-rose-400" />
                    ) : (
                      <Cpu size={20} className={activePipeline.status === "completed" ? "text-emerald-400" : "text-slate-500"} />
                    )}
                    <div>
                      <h4 className="text-xs font-bold font-mono tracking-widest text-white">02 / COGNITIVE ENGINE CORE</h4>
                      <p className="text-[10px] text-zinc-500 font-sans mt-0.5">
                        {activePipeline.status === "completed" ? "Vector embeddings and LLM responses compiled cleanly." :
                         activePipeline.status === "failed" ? "Process execution halted due to worker exception tracking." :
                         "Streaming tokens payload inputs through neural weights..."}
                      </p>
                    </div>
                  </div>
                  {activePipeline.status === "completed" ? <CheckCircle2 size={16} /> :
                   activePipeline.status === "failed" ? <AlertCircle size={16} className="text-rose-400" /> :
                   <Loader2 size={14} className="animate-spin text-purple-400" />}
                </div>

                {/* Vertical Bus neon line 2 */}
                <div className="w-[2px] h-12 bg-slate-900 relative overflow-hidden">
                  <div className={`absolute top-0 left-0 right-0 h-5 bg-gradient-to-b from-transparent to-purple-400 rounded animate-marquee-vertical ${
                    activePipeline.status === "completed" ? "block" : "hidden"
                  }`} />
                </div>

                {/* TRANSIT OUTPUT CONSOLE LOG LINE */}
                <div className={`w-full flex items-center justify-between gap-4 p-5 rounded-2xl border bg-slate-950/60 ${
                  activePipeline.status === "completed" ? "border-emerald-500/30 text-emerald-400 shadow-[0_0_25px_rgba(16,185,129,0.15)]" : "border-slate-800 text-slate-600"
                }`}>
                  <div className="flex items-center gap-4">
                    <Database size={20} className={activePipeline.status === "completed" ? "text-emerald-400" : "text-slate-600"} />
                    <div>
                      <h4 className="text-xs font-bold font-mono tracking-widest text-white">03 / METRIC OUTPUT MANIFOLD</h4>
                      <p className="text-[10px] text-zinc-500 font-sans mt-0.5">Usage costs committed and streaming events dispatched back to disk layouts.</p>
                    </div>
                  </div>
                  <CheckCircle2 size={16} className={activePipeline.status === "completed" ? "text-emerald-400" : "text-slate-800"} />
                </div>

              </div>

              {/* HALT STACK DIAGNOSTIC CONSOLE ERROR REASON PANEL */}
              {activePipeline.error_message && (
                <div className="mt-8 max-w-md mx-auto p-4 bg-rose-500/5 border border-rose-500/20 rounded-xl text-left font-mono text-[11px] text-rose-400">
                  <span className="font-black text-[9px] tracking-widest text-rose-300 block uppercase mb-1">Hardware Crash Halt Trace:</span>
                  {activePipeline.error_message}
                </div>
              )}

            </div>
          ) : (
            
            /* ------------------------------------------------------------- */
            /* VIEW MODE B: HISTORY DATASET DATA MATRIX WITH FILTER CONTROLS */
            /* ------------------------------------------------------------- */
            <div className="space-y-4 animate-fadeIn">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                
                {/* SEARCH INPUT */}
                <div className="md:col-span-2 relative flex items-center">
                  <Search className="absolute left-4 text-zinc-600" size={16} />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search past pipelines by typing task name (e.g. Workspace-Copilot-Query)..."
                    className="w-full h-11 bg-[#090f1c]/50 border border-slate-800 rounded-xl pl-12 pr-4 text-xs outline-none focus:border-cyan-500/40 font-mono transition-colors text-white placeholder-zinc-600"
                  />
                </div>

                {/* CONTROL FILTERS SLOTS */}
                <div className="md:col-span-2 flex bg-slate-950 p-1 rounded-xl border border-slate-900 font-mono text-[11px] font-bold">
                  {["all", "completed", "failed", "running"].map((tab) => (
                    <button 
                      key={tab} 
                      onClick={() => setStatusFilter(tab)} 
                      className={`flex-1 h-9 rounded-lg capitalize transition-all ${
                        statusFilter === tab 
                          ? "bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shadow-md" 
                          : "text-zinc-500 hover:text-zinc-300"
                      }`}
                    >
                      {tab}
                    </button>
                  ))}
                </div>
              </div>

              {/* FEED DATA TABLE COMPONENT */}
              <div className="bg-[#090f1c]/30 border border-slate-800/60 rounded-2xl overflow-hidden shadow-2xl">
                <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/20">
                  <h3 className="text-xs font-bold font-mono text-zinc-400 uppercase tracking-widest flex items-center gap-2">
                    <SlidersHorizontal size={12} className="text-cyan-400" /> Compiled Agent Operational Execution Feeds
                  </h3>
                </div>

                <div className="overflow-x-auto w-full">
                  <table className="w-full text-left text-xs font-mono border-collapse">
                    <thead>
                      <tr className="border-b border-slate-800 bg-slate-950/40 text-zinc-500 uppercase text-[10px] tracking-wider">
                        <th className="py-4 px-6 font-bold">Pipeline ID Reference</th>
                        <th className="py-4 px-6 font-bold">Task Operation Event</th>
                        <th className="py-4 px-6 font-bold">Clearance State</th>
                        <th className="py-4 px-6 font-bold">Execution Clock</th>
                        <th className="py-4 px-6 font-bold text-right">Telemetry Link</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/40">
                      {loadingPipelines ? (
                        <tr><td colSpan={5} className="py-12 text-center text-zinc-500 animate-pulse tracking-widest">LOADING HISTORICAL CHANNELS MATRIX...</td></tr>
                      ) : pipelines.length === 0 ? (
                        <tr><td colSpan={5} className="py-12 text-center text-zinc-600 tracking-wider">NO LOGGED RUNTIME FLOWS DETECTED WITHIN SEARCH BOUNDS.</td></tr>
                      ) : (
                        pipelines.map((pipe) => {
                          const isPipeRunning = pipe.status === "pending" || pipe.status === "running";
                          return (
                            <tr key={pipe.step_id} className="hover:bg-slate-900/10 transition-all group">
                              
                              <td className="py-4 px-6 text-cyan-400 font-bold tracking-tight">
                                {pipe.step_id.slice(0, 8)}...{pipe.step_id.slice(-6)}
                              </td>

                              <td className="py-4 px-6 font-bold text-slate-200">
                                {pipe.task_name}
                              </td>

                              <td className="py-4 px-6">
                                <span className={`px-2.5 py-0.5 rounded-md text-[9px] font-black tracking-widest border uppercase ${
                                  pipe.status === "completed" ? "bg-emerald-500/5 border-emerald-500/20 text-emerald-400" :
                                  isPipeRunning ? "bg-purple-500/5 border-purple-500/20 text-purple-400 animate-pulse" :
                                  "bg-rose-500/5 border-rose-500/20 text-rose-400"
                                }`}>
                                  {pipe.status}
                                </span>
                              </td>

                              <td className="py-4 px-6 text-zinc-500 text-[10px]">
                                {pipe.created_at ? (
                                  <span className="flex items-center gap-1 font-sans">
                                    <Clock size={11} className="text-zinc-600" />
                                    {new Date(pipe.created_at).toLocaleTimeString(undefined, { hour12: true })}
                                  </span>
                                ) : "—"}
                              </td>

                              <td className="py-4 px-6 text-right">
                                <button 
                                  onClick={() => handleInspectNode(pipe)} 
                                  className="h-8 px-3 rounded-xl border border-slate-800 bg-slate-950/40 text-[10px] text-slate-400 hover:text-white hover:border-cyan-500/30 transition-all inline-flex items-center gap-1"
                                >
                                  <span>Inspect Blueprint</span>
                                  <ChevronRight size={12} className="group-hover:translate-x-0.5 transition-transform" />
                                </button>
                              </td>

                            </tr>
                          );
                        })
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

        </div>
      </main>

      {/* Global CSS Injection Engine for Vertical Neon Bus Line Pulses */}
      <style jsx global>{`
        @keyframes marqueeVertical { 
          0% { transform: translateY(-100%); } 
          100% { transform: translateY(300%); } 
        }
        .animate-marquee-vertical { 
          animation: marqueeVertical 1.2s linear infinite; 
        }
      `}</style>
    </div>
  );
}