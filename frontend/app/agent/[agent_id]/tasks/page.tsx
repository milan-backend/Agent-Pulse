"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import {
  ArrowLeft,
  CheckCircle2,
  XCircle,
  Clock3,
  Database,
  Cpu,
  Activity,
  Search,
  SlidersHorizontal
} from "lucide-react";
import { toast } from "sonner";
import { getAgentTasks } from "@/components/api";

interface Task {
  step_id: string;
  task_name: string;
  status: string;
  input_data: any;
  output_data: any;
  error_message: string | null;
  retry_count: number;
  cache_hit: boolean;
  event_type: string | null;
  started_at: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export default function AgentTasksPage() {
  const params = useParams();
  const agentId = params?.agent_id as string;

  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Tasks Specific Search States Hooks Mapping
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  async function fetchTasks() {
    try {
      setLoading(true);
      // Calls your modified core function with active query filters
      const data = await getAgentTasks(agentId, searchQuery, statusFilter);
      const taskArray = Array.isArray(data)
        ? data
        : Array.isArray(data?.tasks)
        ? data.tasks
        : [];

      const sortedTasks = [...taskArray].sort(
        (a, b) => new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime()
      );
      setTasks(sortedTasks);
    } catch (error) {
      console.error(error);
      toast.error("Failed to load agent tasks");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (agentId) {
      fetchTasks();
    }
  }, [agentId, statusFilter]); // Re-fires whenever dropdown option runs or switches

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      fetchTasks();
    }
  }

  function getStatusColor(status: string) {
    switch (status?.toLowerCase()) {
      case "completed": return "border-green-500/20 bg-green-500/10 text-green-300";
      case "failed": return "border-red-500/20 bg-red-500/10 text-red-300";
      case "running": return "border-yellow-500/20 bg-yellow-500/10 text-yellow-300";
      default: return "border-cyan-500/20 bg-cyan-500/10 text-cyan-300";
    }
  }

  return (
    <main className="min-h-screen bg-[#020817] text-white p-8">
      {/* HEADER */}
      <div className="flex items-center justify-between gap-6 flex-wrap">
        <div>
          <Link href={`/agent/${agentId}`} className="inline-flex items-center gap-2 rounded-2xl border border-cyan-500/20 bg-cyan-500/10 px-5 py-3 text-cyan-300 transition hover:bg-cyan-500/20">
            <ArrowLeft size={18} /> Back To Agent
          </Link>
          <div className="mt-6 flex items-center gap-5">
            <div className="h-20 w-20 rounded-3xl border border-cyan-500/20 bg-cyan-500/10 flex items-center justify-center">
              <Activity size={40} className="text-cyan-300" />
            </div>
            <div>
              <h1 className="text-6xl font-black">Agent Tasks</h1>
              <p className="mt-3 text-lg text-zinc-400">Runtime execution history and telemetry.</p>
            </div>
          </div>
        </div>

        {/* METRICS DATA VIEW BLOCK */}
        <div className="flex items-center gap-4 flex-wrap">
          <button onClick={fetchTasks} className="rounded-2xl border border-cyan-500/20 bg-cyan-500/10 px-6 py-4 text-cyan-300 font-bold transition-all hover:bg-cyan-500/20">
            Refresh Tasks
          </button>
          <div className="rounded-3xl border border-cyan-500/20 bg-cyan-500/10 px-8 py-6">
            <p className="text-sm text-zinc-400">Total Tasks</p>
            <h2 className="mt-2 text-5xl font-black text-cyan-300">{tasks.length}</h2>
          </div>
        </div>
      </div>

      {/* FILTER CONTROL WRAPPER STRIP CONTAINER PANEL */}
      <div className="flex flex-col md:flex-row items-center gap-4 bg-[#08111f] border border-cyan-500/10 p-4 rounded-3xl mt-10">
        <div className="relative flex-1 w-full">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-500" size={18} />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Search tasks by execution prompt descriptions..."
            className="w-full bg-black/40 border border-cyan-500/10 rounded-2xl pl-12 pr-4 py-3 text-sm focus:outline-none focus:border-cyan-400/50 transition-colors text-white placeholder-zinc-600"
          />
        </div>
        <div className="flex items-center gap-3 w-full md:w-auto shrink-0">
          <div className="relative w-full md:w-48">
            <SlidersHorizontal className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-500" size={14} />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full bg-black/40 border border-cyan-500/10 rounded-2xl pl-10 pr-4 py-3 text-sm focus:outline-none focus:border-cyan-400/50 transition-colors text-zinc-400 appearance-none cursor-pointer"
            >
              <option value="">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="running">Running</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
            </select>
          </div>
          <button
            onClick={fetchTasks}
            className="px-6 py-3 bg-cyan-500 text-black hover:bg-cyan-400 transition-colors font-bold rounded-2xl text-sm w-full md:w-auto"
          >
            Search
          </button>
        </div>
      </div>

      {/* CONDITIONAL COMPONENT TREE DISPLAY LOOPS */}
      {loading ? (
        <div className="mt-6 rounded-3xl border border-cyan-500/10 bg-[#08111f] p-10 text-zinc-400">
          Loading tasks...
        </div>
      ) : tasks.length === 0 ? (
        <div className="mt-6 flex h-[400px] items-center justify-center rounded-3xl border border-cyan-500/10 bg-[#08111f]">
          <div className="text-center">
            <Cpu size={48} className="mx-auto text-zinc-600" />
            <h2 className="mt-6 text-4xl font-black">No Tasks Found</h2>
            <p className="mt-3 text-zinc-500">No telemetry steps align against active query filter contexts.</p>
          </div>
        </div>
      ) : (
        <div className="mt-6 space-y-6">
          {tasks.map((task) => (
            <div key={task.step_id} className="rounded-3xl border border-cyan-500/10 bg-[#08111f] p-8">
              <div className="flex items-start justify-between gap-6 flex-wrap">
                <div>
                  <h2 className="text-3xl font-black text-cyan-300">{task.task_name}</h2>
                  <p className="mt-3 break-all text-sm text-zinc-500">{task.step_id}</p>
                </div>
                <div className={`flex items-center gap-3 rounded-2xl border px-5 py-3 font-bold ${getStatusColor(task.status)}`}>
                  {task.status === "completed" ? <CheckCircle2 size={18} /> : task.status === "failed" ? <XCircle size={18} /> : <Clock3 size={18} />}
                  {task.status}
                </div>
              </div>

              <div className="mt-8 grid gap-5 md:grid-cols-3">
                <InfoCard title="Retry Count" value={task.retry_count} />
                <InfoCard title="Cache Hit" value={task.cache_hit ? "YES" : "NO"} />
                <InfoCard title="Event Type" value={task.event_type || "N/A"} />
              </div>

              <div className="mt-8 rounded-3xl border border-white/10 bg-black/30 p-6">
                <div className="flex items-center gap-3">
                  <Database size={18} className="text-cyan-300" />
                  <h3 className="text-xl font-black">Input Data</h3>
                </div>
                <pre className="mt-5 max-h-[400px] overflow-y-auto overflow-x-auto whitespace-pre-wrap break-all text-sm text-zinc-300">
                  {JSON.stringify(task.input_data || {}, null, 2).slice(0, 10000)}
                </pre>
              </div>

              <div className="mt-6 rounded-3xl border border-white/10 bg-black/30 p-6">
                <div className="flex items-center gap-3">
                  <Cpu size={18} className="text-green-300" />
                  <h3 className="text-xl font-black">Output Data</h3>
                </div>
                <pre className="mt-5 max-h-[400px] overflow-y-auto overflow-x-auto whitespace-pre-wrap break-all text-sm text-zinc-300">
                  {JSON.stringify(task.output_data || {}, null, 2).slice(0, 10000)}
                </pre>
              </div>

              {task.error_message && (
                <div className="mt-6 rounded-3xl border border-red-500/20 bg-red-500/10 p-6">
                  <h3 className="text-xl font-black text-red-300">Error Message</h3>
                  <p className="mt-4 text-red-200">{task.error_message}</p>
                </div>
              )}

              <div className="mt-8 grid gap-5 md:grid-cols-3">
                <InfoCard title="Started At" value={task.started_at ? new Date(task.started_at).toLocaleString() : "N/A"} />
                <InfoCard title="Created At" value={task.created_at ? new Date(task.created_at).toLocaleString() : "N/A"} />
                <InfoCard title="Updated At" value={task.updated_at ? new Date(task.updated_at).toLocaleString() : "N/A"} />
              </div>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}

function InfoCard({ title, value }: { title: string; value: string | number; }) {
  return (
    <div className="rounded-2xl border border-cyan-500/10 bg-cyan-500/5 p-5">
      <p className="text-sm text-zinc-400">{title}</p>
      <h3 className="mt-3 text-xl font-black break-all">{value}</h3>
    </div>
  );
}
