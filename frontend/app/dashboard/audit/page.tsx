"use client";

import React, { useState, useEffect } from "react";
import { fetchAuditLogs, AuditLogFilters } from "@/components/api";
import { Shield, ShieldAlert, CheckCircle2, XCircle, Search, Eye } from "lucide-react";

// Local user authentication context resolver hook
function useAuthUser() {
  const [activeUser, setActiveUser] = useState<{ id: string; name: string; role: string } | null>(null);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const savedUserId = localStorage.getItem("user_id") || "usr_dev";
      const savedUserRole = localStorage.getItem("user_role") || "ADMIN"; // Toggle matrix: ADMIN | OPERATOR | VIEWER
      setActiveUser({
        id: savedUserId,
        name: "User",
        role: savedUserRole.toUpperCase()
      });
    }
  }, []);

  return { user: activeUser };
}

export default function AuditLogsPage() {
  const { user } = useAuthUser();
  
  const [logs, setLogs] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [actionFilter, setActionFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [selectedLog, setSelectedLog] = useState<any | null>(null);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearch(search), 300);
    return () => clearTimeout(timer);
  }, [search]);

  useEffect(() => {
    async function syncAuditTrails() {
      setLoading(true);
      try {
        const queryParams: AuditLogFilters = {
          page,
          limit: 15,
          search: debouncedSearch,
          action: actionFilter,
          status: statusFilter,
        };
        const data = await fetchAuditLogs(queryParams);
        
        // 🔒 🟢 COMPLETE ROLE-BASED VISIBILITY GUARD FOR OPERATORS (CASE INSENSITIVE)
        if (user?.role?.toUpperCase() === "OPERATOR") {
          const sanitizedLogs = (data.results || []).filter((log: any) => {
            const directRole = (log.user_role || "").toUpperCase();
            const legacyFallbackRole = (log.output_data?.controlled_by) ? "ADMIN" : "OPERATOR";
            
            // Strictly exclude all rows belonging to ADMIN roles from the Operator view
            return directRole !== "ADMIN" && legacyFallbackRole !== "ADMIN";
          });
          setLogs(sanitizedLogs);
        } else {
          setLogs(data.results || []);
        }
        
        setTotal(data.total || 0);
      } catch (err) {
        console.error("Telemetry link sync interrupted:", err);
      } finally {
        setLoading(false);
      }
    }
    if (user && user.role !== "VIEWER") syncAuditTrails();
  }, [page, debouncedSearch, actionFilter, statusFilter, user]);

  // 🛡️ ROLE BLOCK LAYOUT FOR VIEWER SUBSCRIPTIONS
  if (user && user.role === "VIEWER") {
    return (
      <div className="min-h-screen bg-[#020817] text-white flex flex-col items-center justify-center p-8 text-center">
        <div className="h-16 w-16 bg-red-500/10 border border-red-500/30 rounded-2xl flex items-center justify-center mb-4">
          <ShieldAlert className="text-red-400" size={32} />
        </div>
        <h1 className="text-3xl font-black tracking-tight text-red-500">Access Restrained</h1>
        <p className="text-slate-400 max-w-sm mt-2 text-sm">Viewer roles do not possess authorization clearings to view workspace event trails.</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#020817] text-white p-8">
      <div className="max-w-6xl mx-auto">
        
        {/* Header Block Panel */}
        <div className="rounded-3xl border border-cyan-500/20 bg-[#091525] p-8 mb-8">
          <div className="flex items-center gap-4">
            <div className="h-16 w-16 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center">
              <Shield className="text-cyan-400" size={32} />
            </div>
            <div>
              <p className="text-cyan-400 text-xs tracking-widest font-bold uppercase">Security & Compliance Logs</p>
              <h1 className="text-4xl font-black tracking-tight">WORKSPACE AUDITING</h1>
              <p className="text-slate-400 text-sm mt-1">Immutable monitoring tracking user actions and deployment exceptions.</p>
            </div>
          </div>
        </div>

        {/* Filter Bar Controls Deck */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="relative flex items-center">
            <Search className="absolute left-4 text-slate-500" size={18} />
            <input
              type="text"
              placeholder="Filter by operator name, email or ID..."
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
              className="w-full bg-[#091525] border border-cyan-500/10 rounded-2xl pl-12 pr-4 py-3 text-sm focus:outline-none focus:border-cyan-500/50 transition-colors placeholder-slate-500 text-white"
            />
          </div>

          <select
            value={actionFilter}
            onChange={(e) => { setActionFilter(e.target.value); setPage(1); }}
            className="w-full bg-[#091525] border border-cyan-500/10 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:border-cyan-500/50 text-slate-300"
          >
            <option value="">All Action Mutators</option>
            <option value="POST_AGENTS">POST CREATE AGENT</option>
            <option value="POST_PAUSE">POST PAUSE AGENT</option>
            <option value="POST_RESUME">POST RESUME AGENT</option>
            <option value="POST_KILL">POST KILL MISSION</option>
            <option value="DELETE_MEMBER">DELETE WORKSPACE MEMBER</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
            className="w-full bg-[#091525] border border-cyan-500/10 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:border-cyan-500/50 text-slate-300"
          >
            <option value="">All System Statuses</option>
            <option value="SUCCESS">Success Execution</option>
            <option value="FAILURE">Halted Exceptions</option>
          </select>
        </div>

        {/* Data Table Panel Grid Layout */}
        <div className="rounded-3xl border border-cyan-500/20 bg-[#091525] overflow-hidden">
          {loading ? (
            <div className="p-16 text-center text-slate-500 text-sm animate-pulse tracking-widest font-mono">RETRIEVING SECURITY MATRIX TRAILS...</div>
          ) : logs.length === 0 ? (
            <div className="p-16 text-center text-slate-400 text-sm font-medium">No system operation logs captured within scope variables.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 text-xs uppercase bg-slate-900/40 tracking-wider">
                    <th className="p-5 font-bold">Execution Date</th>
                    <th className="p-5 font-bold">User Context</th>
                    <th className="p-5 font-bold">Authorization Level</th>
                    <th className="p-5 font-bold">Action Event Command</th>
                    <th className="p-5 font-bold">Trace Status</th>
                    <th className="p-5 font-bold text-right">Data Payload</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-sm">
                  {logs.map((log) => {
                    // Extract safe contextual fallback string wrappers for legacy records
                    const fallbackEmail = log.user_email || log.output_data?.controlled_by || log.output_data?.email || "user@agentpulse.ai";
                    const fallbackName = fallbackEmail.includes("@") 
                      ? fallbackEmail.split('@')[0].charAt(0).toUpperCase() + fallbackEmail.split('@')[0].slice(1)
                      : "Workspace Operator";
                    
                    const determinedRole = log.user_role?.toUpperCase() || "OPERATOR";

                    return (
                      <tr key={log.id} className="hover:bg-cyan-500/[0.02] transition-colors">
                        <td className="p-5 text-slate-400 font-mono text-xs">
                          {new Date(log.timestamp).toLocaleString()}
                        </td>
                        
                        {/* 🟢 OPERATOR PROFILE (PRIORITIZES TRUE SIGNUP VALUE) */}
                        <td className="p-5">
                          <div className="font-bold text-slate-200">
                            {log.user_name || fallbackName}
                          </div>
                          <div className="text-xs text-slate-500 font-mono mt-0.5">
                            {log.user_email || fallbackEmail}
                          </div>
                        </td>

                        {/* 🟢 MULTI-ROLE SECURITY ACCREDITATION BADGES MATRIX */}
                        <td className="p-5">
                          <span className={`text-[10px] font-bold px-2.5 py-1 rounded-md font-mono border ${
                            determinedRole === "ADMIN" 
                              ? "bg-red-500/10 text-red-400 border-red-500/20" 
                              : determinedRole === "OPERATOR"
                              ? "bg-blue-500/10 text-blue-400 border-blue-500/20"
                              : "bg-amber-500/10 text-amber-400 border-amber-500/20"
                          }`}>
                            {determinedRole}
                          </span>
                        </td>

                        <td className="p-5 text-cyan-400 font-mono text-xs font-semibold tracking-tight">
                          {log.action}
                        </td>
                        <td className="p-5">
                          {log.status === "SUCCESS" ? (
                            <span className="inline-flex items-center gap-1.5 text-xs text-emerald-400 bg-emerald-500/5 px-2.5 py-1 rounded-full border border-emerald-500/10">
                              <CheckCircle2 size={12} /> Success
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1.5 text-xs text-rose-400 bg-rose-500/5 px-2.5 py-1 rounded-full border border-rose-500/10">
                              <XCircle size={12} /> Exception
                            </span>
                          )}
                        </td>
                        <td className="p-5 text-right">
                          <button
                            onClick={() => setSelectedLog(log)}
                            className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white border border-slate-800 rounded-xl px-3 py-1.5 transition-all hover:bg-slate-800 bg-[#020817]/40"
                          >
                            <Eye size={12} /> Inspect
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}

          {/* Pagination Navigation Footer */}
          <div className="p-4 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400 bg-slate-900/20">
            <div>Displaying logs chain batch length: <span className="text-cyan-400 font-bold">{logs.length}</span> entries</div>
            <div className="flex gap-2">
              <button
                disabled={page === 1}
                onClick={() => setPage(p => Math.max(p - 1, 1))}
                className="px-4 py-2 bg-[#020817] border border-cyan-500/10 rounded-xl text-white disabled:opacity-30 hover:bg-slate-900 font-bold transition-all"
              >
                Back
              </button>
              <button
                disabled={page * 15 >= total}
                onClick={() => setPage(p => p + 1)}
                className="px-4 py-2 bg-[#020817] border border-cyan-500/10 rounded-xl text-white disabled:opacity-30 hover:bg-slate-900 font-bold transition-all"
              >
                Forward
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* JSON Inspection Modal */}
      {selectedLog && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-md flex items-center justify-center p-4 z-50">
          <div className="bg-[#091525] border border-cyan-500/20 rounded-3xl max-w-2xl w-full max-h-[80vh] flex flex-col shadow-2xl overflow-hidden">
            <div className="p-5 border-b border-slate-800 flex justify-between items-center bg-slate-900/40">
              <div>
                <h2 className="text-sm font-bold font-mono text-cyan-400">{selectedLog.action} Parameter Context</h2>
                <p className="text-[11px] text-slate-500 font-mono mt-0.5">Log Node ID: {selectedLog.id}</p>
              </div>
              <button onClick={() => setSelectedLog(null)} className="text-slate-400 hover:text-white text-lg font-bold">✕</button>
            </div>
            <div className="p-6 overflow-y-auto space-y-4 font-mono text-xs">
              {selectedLog.error_message && (
                <div className="p-4 bg-rose-500/5 border border-rose-500/20 rounded-2xl text-rose-400">
                  <div className="font-bold text-[10px] tracking-widest text-rose-300 uppercase mb-1">Crash Trace Reason:</div>
                  {selectedLog.error_message}
                </div>
              )}
              <div>
                <div className="text-slate-500 text-[10px] tracking-widest font-bold uppercase mb-1">Incoming Input State Request Stream:</div>
                <pre className="p-4 bg-[#020817] rounded-2xl text-slate-300 border border-slate-800 overflow-x-auto max-h-44">
                  {JSON.stringify(selectedLog.input_data, null, 2)}
                </pre>
              </div>
              <div>
                <div className="text-slate-500 text-[10px] tracking-widest font-bold uppercase mb-1">Returned Output Execution State Response:</div>
                <pre className="p-4 bg-[#020817] rounded-2xl text-slate-300 border border-slate-800 overflow-x-auto max-h-44">
                  {JSON.stringify(selectedLog.output_data, null, 2)}
                </pre>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}