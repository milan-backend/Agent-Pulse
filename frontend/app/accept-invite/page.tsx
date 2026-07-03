"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { Loader2, ShieldAlert, ShieldCheck, ArrowRight, Activity } from "lucide-react";
import { acceptWorkspaceInvitation } from "@/components/api";

function AcceptInviteContent() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  
  const [status, setStatus] = useState<"verifying" | "success" | "error">("verifying");
  const [message, setMessage] = useState("Verifying token credentials...");

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setMessage("Invitation verification token parameter is missing from the URL string.");
      return;
    }

    async function processInvitation() {
      try {
        const response = await acceptWorkspaceInvitation(token!);
        setStatus("success");
        setMessage(response?.message || "Successfully joined the team cluster container!");
      } catch (err: any) {
        setStatus("error");
        setMessage(err?.message || "Failed to validate invitation token. It may be expired or already used.");
      }
    }
    
    processInvitation();
  }, [token]);

  return (
    <div className="relative z-10 w-full max-w-md rounded-[40px] border border-cyan-500/20 bg-[linear-gradient(180deg,#071120_0%,#091525_100%)] p-10 text-center shadow-2xl">
      <div className="flex justify-center mb-6">
        <div className="h-16 w-16 rounded-2xl border border-cyan-500/20 bg-cyan-500/10 flex items-center justify-center">
          <Activity className="text-cyan-300" size={28} />
        </div>
      </div>

      {status === "verifying" && (
        <div className="space-y-4 font-mono text-xs text-cyan-400 tracking-widest py-6">
          <Loader2 className="animate-spin mx-auto text-cyan-400" size={32} />
          <p>{message.toUpperCase()}</p>
        </div>
      )}

      {status === "success" && (
        <div className="space-y-6">
          <div className="mx-auto h-16 w-16 rounded-full bg-green-500/25 flex items-center justify-center">
            <ShieldCheck className="text-green-400" size={32} />
          </div>
          <h2 className="text-2xl font-black text-white">Clearance Granted</h2>
          <p className="text-sm text-slate-400 font-medium leading-relaxed">{message}</p>
          <button
            onClick={() => window.location.href = "/dashboard"}
            className="w-full h-12 bg-cyan-500 hover:bg-cyan-400 text-black font-sans font-black text-xs uppercase rounded-xl tracking-wider transition-all flex items-center justify-center gap-2"
          >
            Enter Mission Control <ArrowRight size={16} />
          </button>
        </div>
      )}

      {status === "error" && (
        <div className="space-y-6">
          <div className="mx-auto h-16 w-16 rounded-full bg-red-500/25 flex items-center justify-center">
            <ShieldAlert className="text-red-400" size={32} />
          </div>
          <h2 className="text-2xl font-black text-white">Handshake Failure</h2>
          <p className="text-sm text-slate-400 font-medium leading-relaxed font-sans">{message}</p>
          <Link 
            href="/login" 
            className="w-full h-12 bg-slate-900 border border-slate-800 hover:bg-slate-800 text-white font-sans font-bold text-xs uppercase rounded-xl tracking-wider transition-all flex items-center justify-center gap-2"
          >
            Return to Login
          </Link>
        </div>
      )}
    </div>
  );
}

export default function AcceptInvitePage() {
  return (
    <div className="min-h-screen bg-[#020817] flex items-center justify-center px-6 relative overflow-hidden">
      <div className="absolute top-0 left-0 h-[500px] w-[500px] rounded-full bg-cyan-500/5 blur-3xl" />
      <div className="absolute bottom-0 right-0 h-[500px] w-[500px] rounded-full bg-purple-500/5 blur-3xl" />
      
      {/* Next.js requires search parameters lookups to be isolated inside Suspense components to prevent static assembly build errors */}
      <Suspense fallback={
        <div className="font-mono text-xs text-cyan-400 flex items-center gap-2 tracking-widest">
          <Loader2 className="animate-spin" size={16} /> INITIALIZING OVERLAY RUNTIME...
        </div>
      }>
        <AcceptInviteContent />
      </Suspense>
    </div>
  );
}