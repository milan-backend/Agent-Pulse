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
  SlidersHorizontal,
  X,
  FileText,
  Binary,
  Gauge,
  Sparkles,
  HelpCircle
} from "lucide-react";
import { toast } from "sonner";
// TEAMWORK frontend layer api hook added
import { getAgentTasks, agentTasksApi } from "@/components/api";

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

  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  // TELEMETRY SIDE OVER DRAWER DRAWER MODAL CONTROL LAYOUT STATES
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);
  const [telemetryData, setTelemetryData] = useState<any>(null);
  const [loadingTelemetry, setLoadingTelemetry] = useState(false);

  async function fetchTasks() {
    try {
      setLoading(true);
      const data = await getAgentTasks(agentId, searchQuery, statusFilter);
      
      //FIX: Adjusted array check directly to match new flat array signature
      const taskArray = Array.isArray(data) ? data : [];

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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [agentId, statusFilter]);

  // Dynamic Telemetry Request Worker Hub
  async function viewTelemetryTrace(stepId: string) {
    setSelectedTaskId(stepId);
    setTelemetryData(null);
    setLoadingTelemetry(true);
    try {
      const response = await agentTasksApi.getTaskTelemetry(stepId);
      setTelemetryData(response);
    } catch (error: any) {
      console.error("Failed to fetch vector analytics telemetry logs:", error);
      toast.error(error?.message || "Telemetry handshake failed.");
      setSelectedTaskId(null);
    } finally {
      setLoadingTelemetry(false);
    }
  }

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
    <main className="min-h-screen bg-[#020817] text-white p-8 relative overflow-x-hidden">
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

      {/* FILTER CONTROL BAR CONTAINER */}  
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
              <option value="" className="bg-[#08111f] text-white">All Statuses</option>  
              <option value="pending" className="bg-[#08111f] text-white">Pending</option>  
              <option value="running" className="bg-[#08111f] text-white">Running</option>  
              <option value="completed" className="bg-[#08111f] text-white">Completed</option>  
              <option value="failed" className="bg-[#08111f] text-white">Failed</option>  
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

      {/* TASKS MATRIX LIST */}  
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
            <div key={task.step_id} className="rounded-3xl border border-cyan-500/10 bg-[#08111f] p-8 relative overflow-hidden group">  
              <div className="flex items-start justify-between gap-6 flex-wrap">  
                <div>  
                  <h2 className="text-3xl font-black text-cyan-300">{task.task_name}</h2>  
                  <p className="mt-3 break-all text-sm text-zinc-500">{task.step_id}</p>  
                </div>  
                
                {/* RE-ARCHITECTED STATUS CONTAINER BAR ADDING TELEMETRY DRAWER LINK */}
                <div className="flex items-center gap-3 flex-wrap">
                  {/* NEW: PREMIUM OBSERVE ACCELERATOR TELEMETRY TRACE LAUNCH BUTTON ACTION */}
                  <button
                    onClick={() => viewTelemetryTrace(task.step_id)}
                    className="flex items-center gap-2 rounded-2xl border border-cyan-400/40 bg-cyan-950/40 hover:bg-cyan-400/20 px-5 py-3 font-bold text-sm text-cyan-400 transition-all shadow-[0_0_15px_rgba(34,211,238,0.02)]"
                  >
                    <Gauge size={14} />
                    <span>View More Information</span>
                  </button>

                  <div className={`flex items-center gap-3 rounded-2xl border px-5 py-3 font-bold ${getStatusColor(task.status)}`}>  
                    {task.status === "completed" ? <CheckCircle2 size={18} /> : task.status === "failed" ? <XCircle size={18} /> : <Clock3 size={18} />}  
                    {task.status}  
                  </div>  
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
                <pre className="mt-5 max-h-[400px] overflow-y-auto overflow-x-auto whitespace-pre-wrap break-all text-sm text-zinc-300 font-mono">  
                  {JSON.stringify(task.input_data || {}, null, 2).slice(0, 10000)}  
                </pre>  
              </div>  

              <div className="mt-6 rounded-3xl border border-white/10 bg-black/30 p-6">  
                <div className="flex items-center gap-3">  
                  <Cpu size={18} className="text-green-300" />  
                  <h3 className="text-xl font-black">Output Data</h3>  
                </div>  
                <pre className="mt-5 max-h-[400px] overflow-y-auto overflow-x-auto whitespace-pre-wrap break-all text-sm text-zinc-300 font-mono">  
                  {JSON.stringify(task.output_data || {}, null, 2).slice(0, 10000)}  
                </pre>  
              </div>  

              {task.error_message && (  
                <div className="mt-6 rounded-3xl border border-red-500/20 bg-red-500/10 p-6">  
                  <h3 className="text-xl font-black text-red-300">Error Message</h3>  
                  <p className="mt-4 text-red-200">{task.error_message}</p>  
                </div>  
              )}  

              {/* DYNAMIC BROWSER USER TIMESTAMPS GENERATION GRID */}  
              <div className="mt-8 grid gap-5 md:grid-cols-3">  
                <InfoCard   
                  title="Started At"   
                  value={task.started_at && task.started_at !== "None"   
                    ? new Date(task.started_at + "Z").toLocaleString(undefined, { hour12: true })   
                    : "N/A"}   
                />  
                <InfoCard   
                  title="Created At"   
                  value={task.created_at && task.created_at !== "None"   
                    ? new Date(task.created_at + "Z").toLocaleString(undefined, { hour12: true })   
                    : "N/A"}   
                />  
                <InfoCard   
                  title="Updated At"   
                  value={task.updated_at && task.updated_at !== "None"   
                    ? new Date(task.updated_at + "Z").toLocaleString(undefined, { hour12: true })   
                    : "N/A"}   
                />  
                </div>  
            </div>  
          ))}  
        </div>  
      )}  

      {/* =========================================================
         NEW: PREMIUM INTERACTIVE TELEMETRY SLIDE-OVER SIDE PANEL DRAWER MODULE
         ========================================================= */}
      {selectedTaskId && (
        <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-sm transition-all duration-300">
          {/* Backdrop Click Out Controller */}
          <div className="flex-1" onClick={() => setSelectedTaskId(null)} />
          
          <div className="w-full max-w-2xl bg-[#040b15] border-l border-cyan-500/20 h-screen overflow-y-auto p-8 shadow-[-10px_0_30px_rgba(0,0,0,0.5)] flex flex-col animate-slideLeft">
            
            {/* PANEL TITLE SUMMARY ROW */}
            <div className="flex items-center justify-between border-b border-cyan-500/10 pb-5 shrink-0">
              <div className="space-y-1">
                <div className="text-[10px] font-mono font-bold tracking-widest text-cyan-400 uppercase">Vector Trace Matrix Log</div>
                <h2 className="text-3xl font-black tracking-tight text-white flex items-center gap-2">
                  <Gauge size={22} className="text-cyan-400" /> Telemetry Audit
                </h2>
              </div>
              <button 
                onClick={() => setSelectedTaskId(null)}
                className="p-2.5 rounded-xl border border-slate-800 bg-[#09111f]/60 text-zinc-400 hover:text-white transition-colors"
              >
                <X size={16} />
              </button>
            </div>

            {/* DYNAMIC ASYNC CONTENT GATEWAY CONTAINER */}
            <div className="flex-1 py-6 space-y-8 font-sans">
              {loadingTelemetry ? (
                <div className="h-full flex flex-col items-center justify-center gap-3 text-zinc-500 font-mono text-xs">
                  <Loader2 className="animate-spin text-cyan-400" size={24} />
                  <span>EXTRACTING RUNTIME STEP GRAPHS...</span>
                </div>
              ) : !telemetryData ? (
                <div className="text-center p-8 border border-red-500/10 rounded-2xl bg-red-500/5 text-red-400 text-xs font-mono flex items-center gap-2">
                  <XCircle size={16} /> Bypassed telemetry handshake or tracking metrics expired.
                </div>
              ) : (
                <div className="space-y-8 animate-fadeIn">
                  
                  {/* META OVERVIEW ROW TILES */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 rounded-2xl bg-black/40 border border-slate-800">
                      <span className="text-[10px] font-mono uppercase tracking-wider text-zinc-500 block font-bold">Trace Target State</span>
                      <span className="text-xs font-mono font-black uppercase inline-block mt-2 bg-cyan-400/10 border border-cyan-400/20 text-cyan-300 px-2.5 py-1 rounded">
                        {telemetryData.last_executed_step}
                      </span>
                    </div>
                    <div className="p-4 rounded-2xl bg-black/40 border border-slate-800">
                      <span className="text-[10px] font-mono uppercase tracking-wider text-zinc-500 block font-bold">Query Active Length</span>
                      <span className="text-sm font-black text-white block mt-2 font-mono">
                        {telemetryData.query?.length || 0} Chars
                      </span>
                    </div>
                  </div>

                  {/* TELEMETRY LOOP PIPELINE TIMELINE STEP GRID */}
                  <div className="space-y-6">
                    <h3 className="text-xs font-mono uppercase tracking-widest text-zinc-400 font-bold">Internal Telemetry Execution Nodes</h3>
                    
                    {telemetryData.telemetry_timeline?.map((step: any) => (
                      <div key={step.step_index} className="relative pl-6 border-l-2 border-cyan-500/20 space-y-4">
                        
                        {/* Bullet Circle Tag */}
                        <div className={`absolute -left-[7px] top-1 h-3 w-3 rounded-full border ${
                          step.status === "SUCCESS" ? "bg-emerald-400 border-emerald-500/30 shadow-[0_0_10px_#10b981]" : "bg-zinc-800 border-slate-700"
                        }`} />

                        <div className="flex items-center justify-between gap-4 flex-wrap">
                          <h4 className="text-md font-bold text-white flex items-center gap-2">
                            <span className="font-mono text-xs text-zinc-500">0{step.step_index}.</span>
                            {step.event_name}
                          </h4>
                          <span className="text-xs font-mono text-zinc-400 bg-black/60 px-2 py-1 border border-slate-800/80 rounded">
                            ⏳ {step.latency_ms} ms
                          </span>
                        </div>

                        {/* STEP 1 SPECIFIC SUB COMPONENT LOGS: RETRIEVAL MATRIX DATA */}
                        {step.event_name === "KNOWLEDGE_RETRIEVAL" && step.meta && (
                          <div className="bg-[#09131f]/60 border border-cyan-500/10 rounded-2xl p-5 space-y-4 font-sans">
                            <div className="grid grid-cols-2 gap-4 border-b border-slate-800/60 pb-3 font-mono text-[11px]">
                              <div>
                                <span className="text-zinc-500 block">Total Chunks Extracted:</span>
                                <span className="text-white font-black text-xs">{step.meta.total_documents_found} Chunks</span>
                              </div>
                              <div>
                                <span className="text-zinc-500 block">Retrieval Similarity Hit Rate:</span>
                                <span className="text-emerald-400 font-black text-xs">{step.meta.retrieval_hit_rate_percent}%</span>
                              </div>
                            </div>

                            {/* Documents Nested Loop list layout mapping */}
                            <div className="space-y-3">
                              <span className="text-[11px] font-mono text-zinc-400 block font-bold">Source Context Reference Blocks utilized:</span>
                              {step.meta.documents?.length === 0 ? (
                                <p className="text-xs text-zinc-500 italic">No document segments matched cosine threshold criteria paths.</p>
                              ) : (
                                step.meta.documents?.map((doc: any, dIdx: number) => (
                                  <div key={dIdx} className="p-4 rounded-xl bg-black/40 border border-slate-800/80 space-y-2 text-xs">
                                    <div className="flex items-center justify-between gap-2 flex-wrap text-[11px] font-mono">
                                      <span className="text-white font-bold flex items-center gap-1.5 truncate max-w-[240px]">
                                        <FileText size={12} className="text-cyan-400 shrink-0" /> {doc.source_file}
                                      </span>
                                      <div className="flex items-center gap-2 shrink-0">
                                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                          doc.document_scope.includes("Sandbox") ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" : "bg-purple-500/10 text-purple-400 border border-purple-500/20"
                                        }`}>
                                          {doc.document_scope}
                                        </span>
                                        <span className="text-zinc-500">
                                          Dist: <span className="text-cyan-400">{doc.semantic_distance}</span>
                                        </span>
                                      </div>
                                    </div>
                                    <p className="text-zinc-400 leading-relaxed font-sans bg-black/20 p-2.5 border border-slate-900 rounded italic break-all max-h-32 overflow-y-auto">
                                      "{doc.content_snippet}"
                                    </p>
                                  </div>
                                ))
                              )}
                            </div>
                          </div>
                        )}

                        {/* STEP 2 SPECIFIC SUB COMPONENT LOGS: LLM TOKEN USAGE MATRIX DATA */}
                        {step.event_name.includes("Response Generation") && step.meta && (
                          <div className="bg-[#09131f]/60 border border-cyan-500/10 rounded-2xl p-5 space-y-4 font-sans">
                            <div className="flex items-center justify-between gap-4 border-b border-slate-800/60 pb-3 flex-wrap">
                              <div className="flex items-center gap-2">
                                <Sparkles size={14} className="text-purple-400" />
                                <span className="text-xs font-mono text-zinc-400">Target Model Engine Token:</span>
                              </div>
                              <span className="font-mono text-xs font-black text-purple-300 uppercase tracking-wider bg-purple-500/10 border border-purple-500/20 px-2.5 py-0.5 rounded">
                                {step.meta.model_utilized}
                              </span>
                            </div>

                            {/* Token usage chips counts */}
                            <div className="grid grid-cols-3 gap-2 font-mono text-center text-[11px]">
                              <div className="bg-black/30 p-2 rounded-xl border border-slate-800">
                                <span className="text-zinc-500 block">Prompt</span>
                                <span className="text-white font-bold">{step.meta.prompt_tokens_consumed}</span>
                              </div>
                              <div className="bg-black/30 p-2 rounded-xl border border-slate-800">
                                <span className="text-zinc-500 block">Completion</span>
                                <span className="text-white font-bold">{step.meta.completion_tokens_consumed}</span>
                              </div>
                              <div className="bg-black/30 p-2 rounded-xl border border-slate-800">
                                <span className="text-zinc-500 block">Total Weight</span>
                                <span className="text-cyan-400 font-bold">{step.meta.total_tokens_consumed}</span>
                              </div>
                            </div>
                            
                            {/* Chunks that actually influenced answer arrays */}
                            {step.meta.documents_influencing_final_answer && (
                              <div className="space-y-2">
                                <span className="text-[11px] font-mono text-zinc-400 block font-bold">Context Chunks Influencing Final Answer:</span>
                                {step.meta.documents_influencing_final_answer.length === 0 ? (
                                  <p className="text-xs text-zinc-500 italic">No document slices met execution response integration boundaries.</p>
                                ) : (
                                  step.meta.documents_influencing_final_answer.map((snip: string, sIdx: number) => (
                                    <div key={sIdx} className="p-3 bg-black/40 border border-slate-800 rounded-xl text-xs text-zinc-300 font-sans leading-relaxed max-h-24 overflow-y-auto">
                                      {snip}
                                    </div>
                                  ))
                                )}
                              </div>
                            )}
                          </div>
                        )}

                      </div>
                    ))}
                  </div>

                </div>
              )}
            </div>

          </div>
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

// Added Loader icon helper manually to ensure rendering fallback robustness
function Loader2({ className, size }: { className?: string; size?: number; }) {
  return (
    <svg 
      className={`animate-spin ${className || ""}`} 
      xmlns="http://www.w3.org/2000/svg" 
      fill="none" 
      viewBox="0 0 24 24"
      width={size || 16}
      height={size || 16}
    >
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
    </svg>
  );
}