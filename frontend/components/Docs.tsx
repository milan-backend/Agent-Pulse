"use client";

import React, { useState } from "react";
import {
  Terminal,
  Cpu,
  Building2,
  Copy,
  Check,
  Key,
  ArrowRightLeft,
  RefreshCw,
  Play,
  RotateCcw
} from "lucide-react";

export default function Docs() {
  const [activeTab, setActiveTab] = useState("free");
  const [copied, setCopied] = useState(false);

  const codeSnippets = {
    free: `import requests
import uuid

BACKEND_URL = "https://api.agentpulseai.dev"
AGENT_API_KEY = "ap_agent_xxxxxxxxxxxxxxxxx"

# =========================================================================
# Example 1: Infrastructure Telemetry (no prompt)
# Use this configuration to trace background agent loops without AI model costs
# =========================================================================
infra_payload = {
    "task_name": "Telemetry-Sync-Run",
    "input_data": {},                     # Empty object skips model execution and logs raw trace
    "idempotency_key": str(uuid.uuid4())  # Unique identifier token to avoid duplicate retries
}

# =========================================================================
# Example 2: AI Inference (with prompt)
# Use this configuration to trigger active AI model processing via your BYOK keys
# =========================================================================
inference_payload = {
    "task_name": "Market-Analysis-Stream",
    "input_data": {
        "prompt": "Analyze high-throughput real-time AI cluster workloads"
    },
    "idempotency_key": str(uuid.uuid4())
}

# Dispatch request to the Free Tier REST gateway
response = requests.post(
    f"{BACKEND_URL}/steps/execute",
    headers={
        "X-API-Key": AGENT_API_KEY,
        "Content-Type": "application/json"
    },
    json=infra_payload # Swap with inference_payload to execute active AI model processing
)

print(response.json())`,

    pro_and_enterprise: `# =========================================================================
# 1. DISCOVER AVAILABLE TOOLS (GET /mcp/tools)
# Dynamically requests the array of system capability schemas supported by your workspace node
# =========================================================================
# Method: GET https://api.agentpulseai.dev/mcp/tools

# =========================================================================
# 2. DISPATCH WRAPPED TOOL EVENT (POST /mcp/execute)
# Handles multi-tenant background execution mapping through the Model Context Protocol
# =========================================================================

# Example 1: Infrastructure Telemetry (no prompt)
# Sends an empty arguments data package to log pipelines while completely bypassing AI inference fees
infra_mcp_payload = {
  "tool": "execute_task",
  "arguments": {
    "task_name": "MCP-Telemetry-Sync",
    "input_data": {},                     
    "idempotency_key": str(uuid.uuid4())
  }
}

# Example 2: AI Inference (with prompt)
# Pass structural text parameters inside the tool arguments to activate runtime model generation loops
inference_mcp_payload = {
  "tool": "execute_task",
  "arguments": {
    "task_name": "MCP-Market-Analysis",
    "input_data": { 
        "prompt": "Analyze AI metrics and system execution anomalies" 
    },
    "idempotency_key": str(uuid.uuid4())
  }
}

# Response Body format received asynchronously (Job drops directly into queue):
# {
#   "message": "Step scheduled",
#   "step_id": "647127bb-fc97-4955-83d2-b9b303fc4e91",
#   "status": "pending"
# }`
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const currentSnippet = activeTab === "free" ? codeSnippets.free : codeSnippets.pro_and_enterprise;

  return (
    <section id="docs" className="max-w-7xl mx-auto px-6 pt-32 relative z-10">
      
      {/* SECTION HEADER BLOCK */}
      <div className="text-center mb-12">
        <h2 className="text-3xl md:text-5xl font-black text-white mb-4 font-sans">
          Developer Documentation
        </h2>
        <p className="text-slate-400 text-sm md:text-base max-w-2xl mx-auto font-sans">
          Create an agent, copy its API key, configure your AI provider if needed, and follow the examples below to integrate AgentPulse into your application.
        </p>
      </div>

      {/* 🚀 QUICK START ROADMAP MAP PANEL */}
      <div className="max-w-6xl mx-auto mb-16 p-6 md:p-8 rounded-3xl border border-slate-900 bg-slate-950/20 backdrop-blur-md">
        <div className="flex items-center gap-2 text-xs font-mono text-cyan-400 font-bold uppercase tracking-wider mb-6">
          <Play size={14} /> System Quick Start Guide
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 relative">
          {[
            { step: "01", title: "Create an Agent", desc: "Build a persistent virtual system tracking profile in your workspace." },
            { step: "02", title: "Copy Agent API Key", desc: "Secure the unique cryptographic signature generated for target stream validation." },
            { step: "03", title: "Configure AI Provider", desc: "Link your custom OpenAI, Anthropic, or Gemini tokens safely within settings." },
            { step: "04", title: "Dispatch Tasks", desc: "Fire high-throughput network executions using our sample request templates below." }
          ].map((item, idx) => (
            <div key={idx} className="relative group">
              <div className="text-2xl font-mono font-black text-slate-800 mb-1 group-hover:text-cyan-950 transition-colors">{item.step}</div>
              <h4 className="text-sm font-bold text-slate-200 mb-1 font-sans">{item.title}</h4>
              <p className="text-xs text-slate-400 leading-relaxed font-sans">{item.desc}</p>
            </div>
          ))}
        </div>

        {/* 🔑 API RECOVERY SECURITY ALERT NOTIFICATION STRIP */}
        <div className="mt-8 pt-4 border-t border-slate-900/60 flex items-center gap-3 text-xs text-slate-400 font-sans">
          <RotateCcw size={14} className="text-amber-500 shrink-0" />
          <span>
            Lost track of your production token details? If you forget your active API key credentials, you can safely reset or regenerate it at any time directly inside <code className="text-slate-200 font-mono text-[11px] bg-slate-900 px-1 rounded">Agent Settings → Regenerate API Key</code>.
          </span>
        </div>
      </div>

      {/* ROUTING GATEWAY INFRASTRUCTURE STRIP ADVISORY */}
      <div className="max-w-3xl mx-auto mb-8 text-center p-3.5 rounded-xl border border-cyan-500/10 bg-cyan-500/5 text-xs text-slate-300 font-mono">
        {activeTab === "free" ? (
          <span>💡 <span className="text-cyan-400 font-bold">Free Tier Operations:</span> Utilize the light REST parameters configuration by dispatching to <span className="text-white font-bold">POST /steps/execute</span>.</span>
        ) : (
          <span>💡 <span className="text-purple-400 font-bold">Pro & Enterprise Operations:</span> Utilize standardized native Model Context Protocol schemas by dispatching to <span className="text-white font-bold">POST /mcp/execute</span>.</span>
        )}
      </div>

      {/* ENVIRONMENT NAVIGATION SELECTION MENUS */}
      <div className="flex flex-wrap justify-center gap-4 mb-10 max-w-3xl mx-auto">
        <button
          onClick={() => { setActiveTab("free"); setCopied(false); }}
          className={`flex items-center gap-2 px-5 py-3 rounded-xl text-xs font-mono font-bold border transition-all ${
            activeTab === "free"
              ? "bg-cyan-500/10 border-cyan-500/40 text-cyan-300"
              : "bg-slate-950/40 border-slate-800 text-slate-400 hover:text-slate-200"
          }`}
        >
          <Cpu size={14} /> Free Tier: Step API
        </button>

        <button
          onClick={() => { setActiveTab("pro"); setCopied(false); }}
          className={`flex items-center gap-2 px-5 py-3 rounded-xl text-xs font-mono font-bold border transition-all ${
            activeTab === "pro"
              ? "bg-purple-500/10 border-purple-500/40 text-purple-300"
              : "bg-slate-950/40 border-slate-800 text-slate-400 hover:text-slate-200"
          }`}
        >
          <ArrowRightLeft size={14} /> Pro Plan: Connected MCP Layer
        </button>

        <button
          onClick={() => { setActiveTab("enterprise"); setCopied(false); }}
          className={`flex items-center gap-2 px-5 py-3 rounded-xl text-xs font-mono font-bold border transition-all ${
            activeTab === "enterprise"
              ? "bg-emerald-500/10 border-emerald-500/40 text-emerald-300"
              : "bg-slate-950/40 border-slate-800 text-slate-400 hover:text-slate-200"
          }`}
        >
          <Building2 size={14} /> Enterprise Plan: Dedicated MCP
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-8 items-start max-w-6xl mx-auto">

        {/* LEFT COMPONENT: STICKY CORE PARAMETER REQUIREMENTS */}
        <div className="lg:col-span-2 space-y-4">
          <div className="p-5 rounded-xl border border-slate-800 bg-slate-950/40 backdrop-blur-md relative overflow-hidden group">
            <div className="absolute top-0 left-0 w-1 h-full bg-cyan-400" />
            <div className="flex items-center gap-2 text-xs font-mono text-cyan-400 font-bold mb-2">
              <Key size={14} /> Required Authentication Header
            </div>
            <p className="text-xs text-slate-400 leading-relaxed font-sans mb-3">
              Every incoming request payload requires your unique validation string map to be authorized by the telemetry gateway:
            </p>
            <div className="p-2.5 rounded-lg bg-black/60 border border-slate-900 text-xs font-mono text-slate-200 select-all">
              X-API-Key: <span className="text-cyan-400">&lt;your_agent_api_key&gt;</span>
            </div>
          </div>

          <div className="p-5 rounded-xl border border-slate-800 bg-slate-950/40 backdrop-blur-md font-mono text-[11px] space-y-3">
            <div className="text-xs font-sans font-bold text-slate-300 border-b border-slate-900 pb-1.5 uppercase flex items-center gap-2">
              <RefreshCw size={13} className="text-cyan-400" /> Parameter Validation Specs
            </div>

            <div>
              <span className="text-cyan-400 font-bold">idempotency_key (String):</span>
              <p className="text-slate-400 text-xs mt-0.5 font-sans">
                A unique session hash (UUIDv4) passed per execution block step to ensure structural integrity and block duplicate tracking logs.
              </p>
            </div>

            <div>
              <span className="text-cyan-400 font-bold">task_name (String):</span>
              <p className="text-slate-400 text-xs mt-0.5 font-sans">
                The logging profile name for your active runtime session. Consecutive identical names trigger our systemic cooldown buffers to prevent runaway loops.
              </p>
            </div>

            <div>
              <span className="text-cyan-400 font-bold">input_data (Object):</span>
              <p className="text-slate-400 text-xs mt-0.5 font-sans">
                Unstructured parameter map block. Keep empty <code className="text-cyan-300 font-mono">{}</code> for zero-prompt telemetry traces. Include a <code className="text-cyan-300 font-mono">&quot;prompt&quot;</code> key context string to execute active model processing.
              </p>
            </div>
          </div>
        </div>

        {/* RIGHT COMPONENT: INTERACTIVE SHELL CODE CONSOLE WINDOW */}
        <div className="lg:col-span-3 border border-slate-800 rounded-2xl bg-slate-950 overflow-hidden flex flex-col h-[480px] shadow-2xl">
          <div className="bg-slate-900/80 px-4 py-3 flex items-center justify-between border-b border-slate-800/80">
            <span className="text-[10px] font-mono uppercase tracking-widest text-slate-500 flex items-center gap-2">
              <Terminal size={12} />
              {activeTab === "free" ? "POST /steps/execute" : "POST /mcp/execute"}
            </span>

            {/* ✅ ALWAYS VISIBLE AND INTERACTIVE COPY CODE COMPONENT TRIGGER */}
            <button
              onClick={() => copyToClipboard(currentSnippet)}
              className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800/60 border border-transparent hover:border-slate-700/50 bg-slate-950/40 transition-all flex items-center gap-1.5 text-[11px] font-mono font-bold"
              title="Copy code to clipboard"
            >
              {copied ? (
                <>
                  <Check size={13} className="text-emerald-400" />
                  <span className="text-emerald-400">COPIED</span>
                </>
              ) : (
                <>
                  <Copy size={13} />
                  <span>COPY</span>
                </>
              )}
            </button>
          </div>

          <div className="p-5 flex-1 bg-black/40 overflow-y-auto font-mono text-[11px] text-slate-300 leading-relaxed scrollbar-thin scrollbar-thumb-slate-800 scrollbar-track-transparent">
            <pre className="whitespace-pre">
              {currentSnippet}
            </pre>
          </div>
        </div>

      </div>
    </section>
  );
}