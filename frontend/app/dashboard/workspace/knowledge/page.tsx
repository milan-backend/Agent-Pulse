"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { 
  FileText, 
  UploadCloud, 
  ChevronLeft, 
  Loader2, 
  CheckCircle2, 
  AlertCircle, 
  RefreshCw,
  Clock
} from "lucide-react";
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

export default function WorkspaceKnowledgePage() {
  const [documents, setDocuments] = useState<DocumentStub[]>([]);
  const [loadingList, setLoadingList] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [errorLog, setErrorLog] = useState<string | null>(null);
  const [successLog, setSuccessLog] = useState<string | null>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 1. Fetch File Inventory tracked inside Postgres tenant boundaries
  async function fetchInventory(silent = false) {
    try {
      if (!silent) setLoadingList(true);
      const data = await documentsApi.listDocuments();
      if (Array.isArray(data)) {
        setDocuments(data);
      } else {
        setDocuments([]);
      }
    } catch (err: any) {
      console.error("Failed to parse workspace file list data:", err);
      setErrorLog(err?.message || "Operational layer cross-handshake failure.");
    } finally {
      if (!silent) setLoadingList(false);
    }
  }

  // 2. Continuous pooling interceptor loop to track background Celery worker processing changes
  useEffect(() => {
    fetchInventory();
  }, []);

  useEffect(() => {
    const hasProcessingFiles = documents.some(doc => doc.status === "processing");
    if (!hasProcessingFiles) return;

    const poolTimer = setInterval(() => {
      fetchInventory(true);
    }, 4000);

    return () => clearInterval(poolTimer);
  }, [documents]);

  // 3. Handle Drag Events inside the Browser Window viewport dropzone boundary 
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  // 4. File Processing Ingestion Pipeline Core Core Execution Gateway
  const executeIngestion = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    
    const targetFile = files[0];
    setErrorLog(null);
    setSuccessLog(null);
    setUploading(true);

    try {
      await documentsApi.uploadDocument(targetFile);
      setSuccessLog(`'${targetFile.name}' secure transmission complete. Background ingestion extraction pipeline initiated.`);
      await fetchInventory(true);
    } catch (err: any) {
      console.error("Ingestion gateway dropped transaction:", err);
      setErrorLog(err?.message || "Transmission boundary anomaly. Verify subscription premium limits.");
    } finally {
      setUploading(false);
      setDragActive(false);
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

  // Helper calculation to convert baseline bytes counters to human scannable storage labels
  const formatBytes = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  return (
    <div className="w-full space-y-6 animate-fadeIn font-sans pb-12">
      
      {/* ACTION TOP HEADER BAR COMPONENT */}
      <div className="flex items-center justify-between gap-4 border-b border-slate-800/60 pb-5 w-full">
        <div className="space-y-1">
          <Link href="/dashboard/workspace" className="text-xs font-mono text-cyan-400 hover:text-cyan-300 flex items-center gap-1.5 transition-colors group mb-1 font-bold uppercase tracking-wider">
            <ChevronLeft size={14} className="group-hover:-translate-x-0.5 transition-transform" /> Back to Grid Overview
          </Link>
          <h1 className="text-3xl font-black tracking-tight text-white flex items-center gap-3">
            <FileText className="text-emerald-400" size={28} />
            Workspace Ingestion Vault
          </h1>
          <p className="text-xs text-zinc-400 max-w-2xl">
            Centralized document shielding terminal. Injected assets are split, masked via two-tier cryptographic keys, and mapped inside multi-tenant isolated vector structures.
          </p>
        </div>
        
        <button 
          onClick={() => fetchInventory(false)}
          disabled={loadingList || uploading}
          className="p-3 rounded-xl border border-slate-800/80 bg-[#090f1c]/40 text-zinc-400 hover:text-white hover:bg-[#090f1c]/80 transition-all disabled:opacity-30"
          title="Refresh Ingestion Inventory"
        >
          <RefreshCw size={16} className={loadingList ? "animate-spin text-cyan-400" : ""} />
        </button>
      </div>

      {/* FEEDBACK ANNOUNCEMENTS WARNING DIALOG CONTROL LOOPS */}
      {errorLog && (
        <div className="p-4 rounded-xl border border-red-500/20 bg-red-500/5 text-red-400 text-xs flex items-start gap-3 shadow-sm animate-shake">
          <AlertCircle size={16} className="shrink-0 mt-0.5" />
          <div className="font-mono">{errorLog}</div>
        </div>
      )}

      {successLog && (
        <div className="p-4 rounded-xl border border-emerald-500/20 bg-emerald-500/5 text-emerald-400 text-xs flex items-start gap-3 shadow-sm">
          <CheckCircle2 size={16} className="shrink-0 mt-0.5" />
          <div>{successLog}</div>
        </div>
      )}

      {/* DRAG AND DROP INGESTION TERMINAL DROP ZONE INTERACTIVE MODULE */}
      <div 
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`w-full border-2 border-dashed rounded-2xl p-12 text-center flex flex-col items-center justify-center gap-4 transition-all duration-200 cursor-pointer ${
          dragActive 
            ? "border-emerald-400 bg-emerald-500/5 shadow-[0_0_20px_rgba(16,185,129,0.05)]" 
            : "border-slate-800 bg-[#090f1c]/20 hover:border-slate-700 hover:bg-[#090f1c]/40"
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
        
        <div className={`h-14 w-14 rounded-2xl border flex items-center justify-center transition-all ${
          uploading 
            ? "bg-cyan-500/10 border-cyan-500/20 text-cyan-400 animate-pulse" 
            : dragActive ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400 scale-105" : "bg-[#090f1c]/60 border-slate-800 text-zinc-500"
        }`}>
          {uploading ? (
            <Loader2 className="animate-spin" size={26} />
          ) : (
            <UploadCloud size={26} />
          )}
        </div>

        <div className="space-y-1">
          <h3 className="text-sm font-bold text-zinc-200">
            {uploading ? "STREAMING BINARY PAYLOAD TO GATEWAY..." : "Drop operational documentation files here"}
          </h3>
          <p className="text-xs text-zinc-500 max-w-md font-sans">
            Drag plain text (`.txt`) or multi-page documentation (`.pdf`) files up to 10MB to initialize background text slicing and matching.
          </p>
        </div>
      </div>

      {/* TRACKED FILE INVENTORY INGESTION MATRIX PANEL TABLE */}
      <div className="w-full rounded-2xl border border-slate-800/80 bg-[#090f1c]/20 overflow-hidden">
        <div className="p-5 border-b border-slate-800/80 bg-[#090f1c]/40">
          <h2 className="text-sm font-mono tracking-wider text-zinc-400 uppercase font-bold">Workspace Vector Ingestion Ledger</h2>
        </div>

        {loadingList && documents.length === 0 ? (
          <div className="p-16 text-center text-zinc-500 font-mono text-xs flex items-center justify-center gap-2">
            <Loader2 className="animate-spin text-cyan-400" size={16} />
            <span>DECRYPTING INDEX POOL ENTRIES...</span>
          </div>
        ) : documents.length === 0 ? (
          <div className="p-16 text-center space-y-2">
            <FileText className="mx-auto text-zinc-700" size={32} />
            <h4 className="text-xs font-bold text-zinc-400 font-mono uppercase tracking-wider">No Documentation Vector Stubs Found</h4>
            <p className="text-xs text-zinc-500 max-w-sm mx-auto font-sans">Use the terminal hub drop-zone module above to upload knowledge base documentation assets.</p>
          </div>
        ) : (
          <div className="overflow-x-auto w-full">
            <table className="w-full text-left font-sans text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-zinc-500 font-mono tracking-widest uppercase font-bold bg-[#090f1c]/10">
                  <th className="p-4 font-semibold">Source Identifier Asset</th>
                  <th className="p-4 font-semibold">Format</th>
                  <th className="p-4 font-semibold">Payload Weight</th>
                  <th className="p-4 font-semibold">Uploader Profile</th>
                  <th className="p-4 font-semibold text-right">Extraction Sync Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-medium text-zinc-300">
                {documents.map((doc) => (
                  <tr key={doc.id} className="hover:bg-[#090f1c]/40 transition-colors">
                    <td className="p-4 font-semibold text-white max-w-xs truncate font-sans">
                      {doc.filename}
                    </td>
                    <td className="p-4 font-mono text-zinc-500 uppercase tracking-wider text-[10px]">
                      {doc.mime_type.split("/")[1] || "RAW"}
                    </td>
                    <td className="p-4 font-mono text-zinc-400">
                      {formatBytes(doc.file_size)}
                    </td>
                    <td className="p-4 text-zinc-400 font-mono text-[11px]">
                      {doc.uploaded_by_user}
                    </td>
                    <td className="p-4 text-right shrink-0">
                      <div className="flex items-center justify-end">
                        {doc.status === "ready" && (
                          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-mono text-[10px] uppercase font-bold tracking-wider">
                            <CheckCircle2 size={10} /> INDEXED READY
                          </span>
                        )}
                        {doc.status === "processing" && (
                          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 font-mono text-[10px] uppercase font-bold tracking-wider animate-pulse">
                            <Clock size={10} className="animate-spin" /> EXTRACTING SYNC
                          </span>
                        )}
                        {doc.status === "failed" && (
                          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-red-500/10 border border-red-500/20 text-red-400 font-mono text-[10px] uppercase font-bold tracking-wider">
                            <AlertCircle size={10} /> DISPATCH ERROR
                          </span>
                        )}
                      </div>
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