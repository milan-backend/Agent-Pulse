"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { 
  FileText, 
  UploadCloud, 
  ChevronLeft, 
  Loader2, 
  CheckCircle2, 
  AlertCircle, 
  RefreshCw,
  Clock,
  Trash2
} from "lucide-react";
import { toast } from "sonner";
import { documentsApi } from "@/components/api";

interface DocumentStub {
  id: string;
  filename: string;
  file_size: number;
  mime_type: string;
  status: "processing" | "ready" | "failed";
  uploaded_by_user: string;
  created_at: string | null;
}

export default function AgentKnowledgePage() {
  const params = useParams();
  const agentId = params?.agent_id as string;

  const [documents, setDocuments] = useState<DocumentStub[]>([]);
  const [loadingList, setLoadingList] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [errorLog, setErrorLog] = useState<string | null>(null);
  const [successLog, setSuccessLog] = useState<string | null>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 1. Fetch File Inventory assigned to this specific Agent Sandbox
  async function fetchInventory(silent = false) {
    if (!agentId) return;
    try {
      if (!silent) setLoadingList(true);
      const data = await documentsApi.listDocuments(agentId);
      if (Array.isArray(data)) {
        setDocuments(data);
      } else {
        setDocuments([]);
      }
    } catch (err: any) {
      console.error("Failed to parse agent file list data:", err);
      setErrorLog(err?.message || "Operational layer sandbox data handshake failure.");
    } finally {
      if (!silent) setLoadingList(false);
    }
  }

  useEffect(() => {
    if (agentId) {
      fetchInventory();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [agentId]);

  // 2. Continuous 4-second polling loops if background worker extraction is active
  useEffect(() => {
    const hasProcessingFiles = documents.some(doc => doc.status === "processing");
    if (!hasProcessingFiles) return;

    const poolTimer = setInterval(() => {
      fetchInventory(true);
    }, 4000);

    return () => clearInterval(poolTimer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [documents]);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  // 3. File Processing Ingestion matching Agent Id scoping rules
  const executeIngestion = async (files: FileList | null) => {
    if (!files || files.length === 0 || !agentId) return;
    
    const targetFile = files[0];
    setErrorLog(null);
    setSuccessLog(null);
    setUploading(true);

    try {
      await documentsApi.uploadDocument(targetFile, agentId);
      setSuccessLog(`'${targetFile.name}' loaded to Sandbox. Background slicing initiated.`);
      await fetchInventory(true);
    } catch (err: any) {
      console.error("Sandbox ingestion gateway dropped transaction:", err);
      setErrorLog(err?.message || "Transmission boundary anomaly. Verify operational scope context.");
    } finally {
      setUploading(false);
      setDragActive(false);
    }
  };

  // 4. NEW METHOD: Synchronized Document Purging Cluster Call Execution Trigger
  const executePurge = async (documentId: string, fileName: string) => {
    if (!window.confirm(`Are you sure you want to permanently purge '${fileName}' from storage matrix environments?`)) {
      return;
    }

    setDeletingId(documentId);
    setErrorLog(null);
    setSuccessLog(null);

    try {
      // Connects cleanly to your database extraction layer endpoint
      await documentsApi.deleteDocument(documentId);
      toast.success("Document purged successfully");
      setSuccessLog(`Document '${fileName}' has been cleanly un-indexed from all backend vector buckets.`);
      await fetchInventory(true);
    } catch (err: any) {
      console.error("Storage network boundary dropped deletion workflow:", err);
      setErrorLog(err?.message || "Purge protocol aborted. Security contextual access verification mismatch.");
      toast.error("Failed to delete document");
    } finally {
      setDeletingId(null);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      executeIngestion(e.dataTransfer.files);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      executeIngestion(e.target.files);
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  return (
    /* FIXED: Adjusted page background tint seamlessly to rich dark blue option theme */
    <div className="min-h-screen bg-[#020817] text-white p-8 space-y-10 font-sans animate-fadeIn">
      
      {/* HEADER MATRIX ALIGNED WITH SYSTEM COMPONENT ACTIONS LAYOUT */}
      <div className="flex items-center justify-between gap-6 flex-wrap border-b border-cyan-500/10 pb-6 w-full">
        <div>
          <h1 className="text-6xl font-black text-cyan-400 tracking-tight flex items-center gap-3">
            <FileText className="text-emerald-400" size={44} />
            Agent Knowledge Vault
          </h1>
          <p className="mt-3 text-gray-400 max-w-3xl text-md leading-relaxed">
            Inject contextual documentation strictly locked to this individual agent's private sandbox scope. Assets uploaded here stay isolated from other processes.
          </p>
        </div>
        
        {/* FIXED: Repositioned uniform styled box controllers rightward to match design patterns */}
        <div className="flex items-center gap-4 flex-wrap shrink-0">
          <button 
            onClick={() => fetchInventory(false)}
            disabled={loadingList || uploading}
            className="rounded-2xl border border-cyan-500/20 bg-cyan-500/10 px-5 py-3 font-bold text-cyan-300 hover:bg-cyan-500/20 transition-all disabled:opacity-30 inline-flex items-center gap-2"
          >
            <RefreshCw size={16} className={loadingList ? "animate-spin text-cyan-400" : ""} />
            <span>Refresh Base</span>
          </button>

          <Link 
            href={`/agent/${agentId}`} 
            className="rounded-2xl border border-cyan-500/20 bg-cyan-500/10 px-5 py-3 font-bold text-cyan-300 hover:bg-cyan-500/20 transition-all inline-flex items-center gap-1.5"
          >
            <ChevronLeft size={16} />
            <span>Back To Agent</span>
          </Link>
        </div>
      </div>

      {/* EMERGENCY ERROR & FEEDBACK ALERTS */}
      {errorLog && (
        <div className="p-5 rounded-2xl border border-red-500/30 bg-[#1a0507] text-red-300 text-sm flex items-start gap-3 shadow-md animate-fadeIn">
          <AlertCircle size={18} className="shrink-0 mt-0.5 text-red-400" />
          <div className="font-mono">{errorLog}</div>
        </div>
      )}

      {successLog && (
        <div className="p-5 rounded-2xl border border-emerald-500/20 bg-emerald-500/5 text-emerald-300 text-sm flex items-start gap-3 shadow-md animate-fadeIn">
          <CheckCircle2 size={18} className="shrink-0 mt-0.5 text-emerald-400" />
          <div>{successLog}</div>
        </div>
      )}

      {/* DYNAMIC DRAG AND DROP HUBS */}
      <div 
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`w-full border-2 border-dashed rounded-3xl p-14 text-center flex flex-col items-center justify-center gap-4 transition-all duration-200 cursor-pointer ${
          dragActive 
            ? "border-emerald-400 bg-emerald-500/5 shadow-[0_0_25px_rgba(16,185,129,0.05)]" 
            : "border-cyan-500/20 bg-[#08111f] hover:border-cyan-400/30"
        }`}
      >
        <input 
          ref={fileInputRef}
          type="file" 
          accept=".txt,.pdf"
          onChange={handleFileChange}
          className="hidden" 
          disabled={uploading}
        />
        
        <div className={`h-16 w-16 rounded-2xl border flex items-center justify-center transition-all ${
          uploading 
            ? "bg-cyan-500/20 border-cyan-500/30 text-cyan-300 animate-pulse" 
            : dragActive ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400 scale-105" : "bg-black/40 border-cyan-500/10 text-zinc-500"
        }`}>
          {uploading ? (
            <Loader2 className="animate-spin" size={28} />
          ) : (
            <UploadCloud size={28} />
          )}
        </div>

        <div className="space-y-1">
          <h3 className="text-xl font-black text-zinc-200">
            {uploading ? "STREAMING TO PRIVATE SANDBOX..." : "Drop sandbox documentation files here"}
          </h3>
          <p className="text-sm text-gray-400 max-w-xl font-sans">
            Drag plain text (`.txt`) or multi-page documentation (`.pdf`) up to 10MB to bind records directly to this agent's dynamic context array.
          </p>
        </div>
      </div>

      {/* LEDGER CONTENT MATRIX */}
      <div className="w-full rounded-3xl border border-cyan-500/10 bg-[#08111f] overflow-hidden">
        <div className="p-6 border-b border-cyan-500/10 bg-black/20">
          <h2 className="text-lg font-mono tracking-wider text-cyan-400 uppercase font-black">Private Knowledge Base Ledger</h2>
        </div>

        {loadingList && documents.length === 0 ? (
          <div className="p-20 text-center text-zinc-500 font-mono text-xs flex items-center justify-center gap-2">
            <Loader2 className="animate-spin text-cyan-400" size={16} />
            <span>PARSING ISOLATED STREAM LEDGER...</span>
          </div>
        ) : documents.length === 0 ? (
          <div className="p-20 text-center space-y-3">
            <FileText className="mx-auto text-zinc-700" size={40} />
            <h4 className="text-sm font-black text-zinc-400 font-mono uppercase tracking-wider">No Isolated Records Mapped</h4>
            <p className="text-xs text-gray-500 max-w-sm mx-auto font-sans">Initialize the ingestion gateway cluster module above to append files strictly to this workspace agent context window.</p>
          </div>
        ) : (
          <div className="overflow-x-auto w-full">
            <table className="w-full text-left font-sans text-sm border-collapse">
              <thead>
                <tr className="border-b border-cyan-500/10 text-zinc-400 font-mono tracking-widest uppercase font-black bg-black/20 text-xs">
                  <th className="p-5">Asset Descriptor String</th>
                  <th className="p-5">Mime Target</th>
                  <th className="p-5">Memory Allocation</th>
                  <th className="p-5">Operator Clearances</th>
                  <th className="p-5">Cluster Status</th>
                  {/* Action row column matching delete system updates */}
                  <th className="p-5 text-center">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-cyan-500/10 font-medium text-zinc-300">
                {documents.map((doc) => (
                  <tr key={doc.id} className="hover:bg-black/10 transition-colors">
                    <td className="p-5 font-bold text-white max-w-xs truncate">
                      {doc.filename}
                    </td>
                    <td className="p-5 font-mono text-cyan-400 text-xs tracking-wider uppercase">
                      {doc.mime_type.split("/")[1] || "RAW"}
                    </td>
                    <td className="p-5 font-mono text-zinc-400">
                      {formatBytes(doc.file_size)}
                    </td>
                    <td className="p-5 text-zinc-400 font-mono text-xs max-w-[180px] truncate" title={doc.uploaded_by_user}>
                      {doc.uploaded_by_user}
                    </td>
                    <td className="p-5">
                      <div className="flex items-center">
                        {doc.status === "ready" && (
                          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-green-500/10 border border-green-500/20 text-green-400 font-mono text-xs uppercase font-bold tracking-wider">
                            <CheckCircle2 size={12} /> SECURED READY
                          </span>
                        )}
                        {doc.status === "processing" && (
                          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 font-mono text-xs uppercase font-bold tracking-wider animate-pulse">
                            <Clock size={12} className="animate-spin text-cyan-400" /> RUNNING VECTOR SYNC
                          </span>
                        )}
                        {doc.status === "failed" && (
                          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-red-500/10 border border-red-500/20 text-red-400 font-mono text-xs uppercase font-bold tracking-wider">
                            <AlertCircle size={12} /> SYNC ABORTED
                          </span>
                        )}
                      </div>
                    </td>
                    {/* FIXED/ADDED: Integrated explicit document destruction trash link row layout */}
                    <td className="p-5 text-center">
                      <button
                        onClick={() => executePurge(doc.id, doc.filename)}
                        disabled={deletingId === doc.id || doc.status === "processing"}
                        className="p-2 rounded-xl border border-red-500/20 bg-red-500/10 text-red-400 hover:bg-red-500/20 hover:text-red-300 transition-all disabled:opacity-30 disabled:cursor-not-allowed"
                        title="Purge record from cluster"
                      >
                        {deletingId === doc.id ? (
                          <Loader2 size={14} className="animate-spin text-red-400" />
                        ) : (
                          <Trash2 size={14} />
                        )}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

    </div>
  );
}