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
  KeyRound // Imported for your new API Provider link icon
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
      toast.error("Failed to load agent"); // No sugarcoat, real time logging
    } finally {  
      setLoading(false);  
    }
  }

  useEffect(() => {
    if (agentId) {
      fetchAgent();
    }
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
    <div className="min-h-screen bg-[#020817] text-white flex">
      
      {/* SIDEBAR CONTAINER */}
      <aside className="w-[300px] shrink-0 border-r border-cyan-500/10 bg-[#040b18] p-6">
        <div>
          <h1 className="text-5xl font-black">
            <span className="text-cyan-400">Agent</span>
            <span className="text-white">Pulse</span>
          </h1>
          <p className="mt-2 text-zinc-400">Runtime Agent Control</p>
        </div>

        <div className="mt-10 space-y-4">  
          <Link href="/dashboard/agents" className="flex items-center gap-3 rounded-2xl bg-[#0b1628] px-5 py-4 font-bold transition-all hover:bg-cyan-500/10">  
            <ArrowLeft size={18} /> Back To Agents  
          </Link>  
          
          <button onClick={pauseAgent} disabled={pausing} className="w-full flex items-center gap-3 rounded-2xl bg-green-500/20 border border-green-500/30 px-5 py-4 font-bold text-green-300 transition-all hover:bg-green-500/30 disabled:opacity-50">  
            <Pause size={18} /> {pausing ? "Pausing..." : "Pause Agent"}  
          </button>  
          
          <Link href={`/agent/${agent.id}/settings`} className="flex items-center gap-3 rounded-2xl bg-cyan-500/20 border border-cyan-500/30 px-5 py-4 font-bold text-cyan-300 transition-all hover:bg-cyan-500/30">  
            <Settings size={18} /> Agent Settings  
          </Link>  

          {/* ADDED: DEDICATED PRIVATE PROVIDER INTEGRATION LINK (YOUR AWESOME IDEA!) */}
          <Link href={`/agent/${agent.id}/provider`} className="flex items-center gap-3 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 px-5 py-4 font-bold text-cyan-400 transition-all hover:bg-cyan-500/20">  
            <KeyRound size={18} /> API Provider  
          </Link>  
          
          <Link href={`/agent/${agent.id}/tasks`} className="flex items-center gap-3 rounded-2xl bg-purple-500/20 border border-purple-500/30 px-5 py-4 font-bold text-purple-300 transition-all hover:bg-purple-500/30">  
            <Activity size={18} /> Agent Tasks  
          </Link>  
        </div>  

        <div className="mt-10 rounded-3xl border border-cyan-500/20 bg-cyan-500/10 p-6">  
          <p className="text-zinc-400">Runtime Status</p>  
          <div className="mt-4 flex items-center justify-between">  
            <h2 className={`text-4xl font-black ${agent.is_active ? "text-green-300" : "text-red-300"}`}>{agent.is_active ? "ACTIVE" : "PAUSED"}</h2>  
            <div className={`h-4 w-4 rounded-full ${agent.is_active ? "bg-green-400 shadow-[0_0_20px_#4ade80]" : "bg-red-400 shadow-[0_0_20px_#f87171]"}`} />  
          </div>  
        </div>  
      </aside>  

      {/* MAIN CONTAINER */}  
      <main className="flex-1 p-8 overflow-y-auto">  
        <div className="flex items-center justify-between gap-6 flex-wrap">  
          <div className="flex items-center gap-6">  
            <div className="h-24 w-24 rounded-3xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center shadow-[0_0_35px_rgba(34,211,238,0.15)]">  
              <Cpu size={48} className="text-cyan-300" />  
            </div>  
            <div>  
              <h1 className="text-6xl xl:text-7xl font-black tracking-tight break-words">{agent.name}</h1>  
              <p className="mt-2 text-zinc-400 text-xl">AI Runtime Agent</p>  
            </div>  
          </div>  

          <div className={`rounded-3xl border px-10 py-6 ${agent.is_active ? "border-green-500/20 bg-green-500/10" : "border-red-500/20 bg-red-500/10"}`}>  
            <p className="text-zinc-400">Runtime Status</p>  
            <div className="mt-3 flex items-center gap-3">  
              <ShieldCheck className={agent.is_active ? "text-green-300" : "text-red-300"} />  
              <span className={`text-5xl font-black ${agent.is_active ? "text-green-300" : "text-red-300"}`}>{agent.is_active ? "ACTIVE" : "PAUSED"}</span>  
            </div>  
          </div>  
        </div>  

        {/* METRICS CARD GRID */}  
        <div className="mt-10 grid gap-6 grid-cols-1 md:grid-cols-2 2xl:grid-cols-4">  
          <Card title="Missions" value={Number(agent.mission_count || 0).toLocaleString()} icon={<Activity size={22} strokeWidth={2.5} />} />  
          <Card title="Total Cost" value={`$${Number(agent.total_cost || 0).toLocaleString()}`} icon={<DollarSign size={22} strokeWidth={2.5} />} />  
          <Card title="Max Cost" value={`$${Number(agent.max_cost || 0).toLocaleString()}`} icon={<DollarSign size={22} strokeWidth={2.5} />} />  
          <Card title="Max Steps" value={Number(agent.max_steps || 0).toLocaleString()} icon={<Cpu size={22} strokeWidth={2.5} />} />  
          <Card title="Max Retries" value={Number(agent.max_retries || 0).toLocaleString()} icon={<RotateCcw size={22} strokeWidth={2.5} />} />  
          <Card title="Max Repeated Tasks" value={Number(agent.max_repeated_tasks || 0).toLocaleString()} icon={<Repeat size={22} strokeWidth={2.5} />} />  
          <Card title="Runtime State" value={agent.is_active ? "Running" : "Paused"} icon={<Timer size={22} strokeWidth={2.5} />} />  
        </div>  

        {/* METADATA TIMESTAMPS BAR */}  
        <div className="mt-8 grid gap-6 md:grid-cols-2">  
          <div className="rounded-3xl border border-cyan-500/10 bg-[#08111f] p-8">  
            <p className="text-zinc-400">Agent ID</p>  
            <h2 className="mt-4 text-2xl font-black break-all text-cyan-300">{agent.id}</h2>  
          </div>  

          <div className="rounded-3xl border border-cyan-500/10 bg-[#08111f] p-8">  
            <p className="text-zinc-400">Agent Created</p>  
            <h2 className="mt-4 text-2xl font-black">  
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
    <div className="rounded-3xl border border-cyan-500/10 bg-[#08111f] p-6 transition-all hover:border-cyan-400/30 hover:bg-[#0b1728] overflow-hidden min-w-0">
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