"use client";

import Link from "next/link";
import { 
  Cpu, 
  Activity, 
  DollarSign, 
  RotateCcw, 
  ShieldCheck, 
  ArrowLeft, 
  Pause, 
  Settings, 
  Repeat, 
  Timer,
  KeyRound,
  FileText
} from "lucide-react";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { toast } from "sonner";
import { getAgent, pauseAgentMission } from "@/components/api";

interface Agent {
  id: string;
  name: string;
  is_active: boolean;
  is_killed: boolean;
  max_cost: number;
  max_steps: number;
  max_retries: number;
  max_repeated_tasks: number;
  mission_count: number;
  total_cost: number;
  created_at: string | null;
}

export default function AgentRuntimePage() {
  const params = useParams();
  const agentId = params?.agent_id as string;

  const [agent, setAgent] = useState<Agent | null>(null);
  const [loading, setLoading] = useState(true);
  const [pausing, setPausing] = useState(false);

  async function fetchAgent() {
    try {
      setLoading(true);
      const response = await getAgent(agentId);
      const agentData = response?.agent || response;
      const policy = response?.policy || {};

      const normalizedAgent = {  
        id: agentData?.id || "",  
        name: agentData?.name || "Unknown Agent",  
        is_active: agentData?.is_active ?? false,  
        is_killed: agentData?.is_killed ?? false,  
        max_cost: Number(policy?.max_cost ?? 0),  
        max_steps: Number(policy?.max_steps ?? 0),  
        max_retries: Number(policy?.max_retries ?? 0),  
        max_repeated_tasks: Number(policy?.max_repeated_tasks ?? 0),  
        mission_count: Number(response?.mission_count ?? 0),  
        total_cost: Number(response?.total_cost ?? 0),  
        created_at: agentData?.created_at || null,  
      };  

      setAgent(normalizedAgent);  
    } catch (error) {  
      console.error(error);  
      toast.error("Failed to load agent");
    } finally {
      setLoading(false);  
    }
  }

  useEffect(() => {
    if (agentId) {
      fetchAgent();
    }
    //eslint-disable-next-line react-hooks/exhaustive-deps
  }, [agentId]);

  async function pauseAgent() {
    try {
      setPausing(true);
      await pauseAgentMission(agentId);
      toast.success("Agent paused");
      if (agent) {
        setAgent({
          ...agent,
          is_active: false,
        });
      }
    } catch (error) {
      console.error(error);
      toast.error("Failed to pause agent");
    } finally {
      setPausing(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[#020817] text-white flex items-center justify-center">
        <div className="rounded-3xl border border-cyan-500/10 bg-[#08111f] px-10 py-8 text-zinc-400">
          Loading agent...
        </div>
      </div>
    );
  }

  if (!agent) {
    return (
      <div className="min-h-screen bg-[#020817] text-white flex items-center justify-center">
        Agent not found.
      </div>
    );
  }

  return (
    /* 🎯 FIX 1: Locked down screen layout viewport from breaking layout sizes under heavy content stacks */
    <div className="h-screen w-screen bg-[#020817] text-white flex overflow-hidden select-none">
      
      {/* =====================================================================
          FIXED SIDEBAR: REMOVED GHOST BOX OVERLAPS & ALIGNED UI PATTERNS
          ===================================================================== */}
      <aside className="w-[300px] shrink-0 border-r border-cyan-500/10 bg-[#040b18] p-6 flex flex-col justify-between h-full sticky top-0 overflow-y-auto scrollbar-none">
        <div className="space-y-10">
          <div>
            <h1 className="text-5xl font-black">
              <span className="text-cyan-400">Agent</span>
              <span className="text-white">Pulse</span>
            </h1>
            <p className="mt-2 text-zinc-400 text-sm">Runtime Agent Control</p>
          </div>

          {/* UNIFORM NAV BUTTON SYSTEM - GHOST BOX PURGED CLEANLY */}
          <div className="flex flex-col gap-3">  
            <Link href="/dashboard/agents" className="flex items-center gap-3 rounded-2xl bg-[#0b1628] border border-cyan-500/5 px-5 py-4 font-bold transition-all hover:bg-cyan-500/10">  
              <ArrowLeft size={18} className="text-zinc-400" /> 
              <span>Back To Agents</span>  
            </Link>  
            
            <button onClick={pauseAgent} disabled={pausing} className="w-full flex items-center gap-3 rounded-2xl bg-green-500/10 border border-green-500/20 px-5 py-4 font-bold text-green-400 transition-all hover:bg-green-500/20 disabled:opacity-50 text-left">  
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
          </div>  
        </div>

        <div className="mt-8 mb-2 rounded-3xl border border-cyan-500/20 bg-cyan-500/10 p-6 flex-shrink-0">  
          <p className="text-zinc-400 text-sm">Runtime Status</p>  
          <div className="mt-4 flex items-center justify-between gap-2">  
            <h2 className={`text-3xl xl:text-4xl font-black ${agent.is_active ? "text-green-300" : "text-red-300"}`}>{agent.is_active ? "ACTIVE" : "PAUSED"}</h2>  
            <div className={`h-4 w-4 rounded-full shrink-0 ${agent.is_active ? "bg-green-400 shadow-[0_0_20px_#4ade80]" : "bg-red-400 shadow-[0_0_20px_#f87171]"}`} />  
          </div>  
        </div>  
      </aside>  

      {/* MAIN CONTAINER */}  
      {/* 🎯 FIX 2: Isolated right-side scroll layout workspace with flex flex-col and min-w-0 to block column compression bugs */}
      <main className="flex-1 p-8 overflow-y-auto h-full flex flex-col min-w-0 bg-[#020817] scrollbar-thin scrollbar-thumb-zinc-900">  
        
        {/* TOP AGENT TITLE CONTAINER BOX */}
        {/* 🎯 FIX 3: Added flex-shrink-0 so the main agent description header container box doesn't collapse horizontally on low display resolutions */}
        <div className="flex items-center justify-between gap-6 flex-wrap flex-shrink-0 w-full bg-[#08111f]/30 border border-cyan-500/5 p-6 rounded-3xl">  
          <div className="flex items-center gap-6 min-w-0">  
            <div className="h-24 w-24 rounded-3xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center shadow-[0_0_35px_rgba(34,211,238,0.15)] shrink-0">  
              <Cpu size={48} className="text-cyan-300" />  
            </div>  
            <div className="min-w-0">  
              <h1 className="text-4xl md:text-5xl xl:text-6xl font-black tracking-tight text-white truncate max-w-full" title={agent.name}>{agent.name}</h1>  
              <p className="mt-2 text-zinc-400 text-xl font-medium">AI Runtime Agent</p>  
            </div>  
          </div>  

          <div className={`rounded-3xl border px-10 py-6 shrink-0 ${agent.is_active ? "border-green-500/20 bg-green-500/10" : "border-red-500/20 bg-red-500/10"}`}>  
            <p className="text-zinc-400 text-sm">Runtime Status</p>  
            <div className="mt-3 flex items-center gap-3">  
              <ShieldCheck className={agent.is_active ? "text-green-300" : "text-red-300"} />  
              <span className={`text-4xl font-black ${agent.is_active ? "text-green-300" : "text-red-300"}`}>{agent.is_active ? "ACTIVE" : "PAUSED"}</span>  
            </div>  
          </div>  
        </div>  

        {/* METRICS CARD GRID */}  
        {/* 🎯 FIX 4: Implemented explicit grid flow boundaries with flex-shrink-0 to prevent boxes from hiding under other panels */}
        <div className="mt-10 grid gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4 flex-shrink-0 w-full">  
          <Card title="Missions" value={Number(agent.mission_count || 0).toLocaleString()} icon={<Activity size={22} strokeWidth={2.5} />} />  
          <Card title="Total Cost" value={`$${Number(agent.total_cost || 0).toLocaleString()}`} icon={<DollarSign size={22} strokeWidth={2.5} />} />  
          <Card title="Max Cost" value={`$${Number(agent.max_cost || 0).toLocaleString()}`} icon={<DollarSign size={22} strokeWidth={2.5} />} />  
          <Card title="Max Steps" value={Number(agent.max_steps || 0).toLocaleString()} icon={<Cpu size={22} strokeWidth={2.5} />} />  
          <Card title="Max Retries" value={Number(agent.max_retries || 0).toLocaleString()} icon={<RotateCcw size={22} strokeWidth={2.5} />} />  
          <Card title="Max Repeated Tasks" value={Number(agent.max_repeated_tasks || 0).toLocaleString()} icon={<Repeat size={22} strokeWidth={2.5} />} />  
          <Card title="Runtime State" value={agent.is_active ? "Running" : "Paused"} icon={<Timer size={22} strokeWidth={2.5} />} />  
        </div>  

        {/* METADATA TIMESTAMPS BAR */}  
        {/* 🎯 FIX 5: Locked the bottom telemetry boxes from squishing on scroll actions */}
        <div className="mt-8 grid gap-6 md:grid-cols-2 flex-shrink-0 w-full mb-4">  
          <div className="rounded-3xl border border-cyan-500/10 bg-[#08111f] p-8 min-w-0">  
            <p className="text-zinc-400 text-sm">Agent ID</p>  
            <h2 className="mt-4 text-2xl font-black break-all text-cyan-300 font-mono tracking-tight">{agent.id}</h2>  
          </div>  

          <div className="rounded-3xl border border-cyan-500/10 bg-[#08111f] p-8 min-w-0">  
            <p className="text-zinc-400 text-sm">Agent Created</p>  
            <h2 className="mt-4 text-2xl font-black tracking-tight">  
              {agent.created_at  
                ? new Date(agent.created_at + "Z").toLocaleString(undefined, { hour12: true })  
                : "Not Available"}  
            </h2>  
          </div>  
        </div>  
      </main>  
    </div>
  );
}

function Card({ title, value, icon }: { title: string; value: string | number; icon: React.ReactNode; }) {
  return (
    <div className="rounded-3xl border border-cyan-500/10 bg-[#08111f] p-6 transition-all hover:border-cyan-400/30 hover:bg-[#0b1728] overflow-hidden min-w-0 shadow-lg">
      <div className="flex items-start justify-between gap-5">
        <div className="flex-1 min-w-0 overflow-hidden">
          <p className="text-sm font-medium tracking-wide text-zinc-400 truncate">{title}</p>
          <h2 className="mt-4 text-2xl md:text-3xl xl:text-[34px] font-black leading-none tracking-tight text-white whitespace-nowrap overflow-hidden text-ellipsis max-w-full" title={String(value)}>{value}</h2>
        </div>
        <div className="shrink-0 flex h-14 w-14 min-h-[56px] min-w-[56px] items-center justify-center rounded-2xl border border-cyan-400/20 bg-cyan-500/10 text-cyan-300 shadow-[0_0_20px_rgba(34,211,238,0.15)]">
          {icon}
        </div>
      </div>
    </div>
  );
}