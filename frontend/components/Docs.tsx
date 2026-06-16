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
  RefreshCw
} from "lucide-react";

export default function Docs() {
  const [activeTab, setActiveTab] = useState("free");
  const [copied, setCopied] = useState(false);

  const codeSnippets = {
    free: `import requests
import uuid

BACKEND_URL = "https://api.agentpulseai.dev"
AGENT_API_KEY = "ap_agent_xxxxxxxxxxxxxxxxx"

# CONFIGURATION A: TELEMETRY & INFRASTRUCTURE TRACING (NO AI PROMPT)
# Leaves input_data empty to log agent loops without calling external AI models
infra_payload = {
    "task_name": "Telemetry-Sync-Run",
    "input_data": {},                     # Empty = skips model processing, logs trace
    "idempotency_key": str(uuid.uuid4())  # Unique UUIDv4 identifier
}

# CONFIGURATION B: ACTIVE AI INFERENCE (WITH PROMPT)
inference_payload = {
    "task_name": "Market-Analysis-Stream",
    "input_data": {
        "prompt": "Analyze high-throughput real-time AI cluster workloads"
    },
    "idempotency_key": str(uuid.uuid4())
}

response = requests.post(
    f"{BACKEND_URL}/steps/execute",
    headers={
        "X-API-Key": AGENT_API_KEY,
        "Content-Type": "application/json"
    },
    json=infra_payload # Swap with inference_payload depending on your target
)

print(response.json())`,

    pro_and_enterprise: `# 1. DISCOVER AVAILABLE TOOLS (GET /mcp/tools)
# RESPONSE BODY:
{
  "tools": [
    {
      "name": "execute_task",
      "description": "Execute a durable task with reliability",
      "input_schema": {
        "type": "object",
        "properties": {
          "task_name": { "type": "string" },
          "input_data": { "type": "object" },
          "idempotency_key": { "type": "string" }
        },
        "required": ["task_name", "idempotency_key"]
      }
    }
  ]
}

# 2. DISPATCH WRAPPED TOOL EVENT (POST /mcp/execute)
# CONFIGURATION A: INFRASTRUCTURE TRACING ONLY (NO AI PROMPT)
{
  "tool": "execute_task",
  "arguments": {
    "task_name": "MCP-Telemetry-Sync",
    "input_data": {},                     # Empty object = logs pipeline, skips model costs
    "idempotency_key": "mcp-infra-uuid-001"
  }
}

# CONFIGURATION B: ACTIVE INFERENCE WORKFLOW (WITH PROMPT)
# {
#   "tool": "execute_task",
#   "arguments": {
#     "task_name": "MCP-Market-Analysis",
#     "input_data": { "prompt": "Analyze AI metrics and anomalies" },
#     "idempotency_key": "mcp-inference-uuid-002"
#   }
# }

# SERVER RESPONSE (Async Telemetry Queue Handle):
{
  "message": "Step scheduled",
  "step_id": "647127bb-fc97-4955-83d2-b9b303fc4e91",
  "status": "pending"
}`
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Safe mapping variable targeting unified code payloads
  const currentSnippet = activeTab === "free" ? codeSnippets.free : codeSnippets.pro_and_enterprise;

  return (
    <section id="docs" className="max-w-7xl mx-auto px-6 pt-32 relative z-10">
      <div className="text-center mb-16">
        <h2 className="text-3xl md:text-5xl font-black text-white mb-4 font-sans">
          Developer Documentation
        </h2>
        <p className="text-slate-400 text-base md:text-lg max-w-2xl mx-auto">
          Integrate the AgentPulse observability routing framework seamlessly into your custom agent workflows.
        </p>
      </div>

      {/* STRIPPED & UNIFIED SELECTOR STRIP */}
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

        {/* LEFT COMPONENT: STICKY SCHEMA PARAMETER SPECIFICATIONS */}
        <div className="lg:col-span-2 space-y-4">
          <div className="p-5 rounded-xl border border-slate-800 bg-slate-950/40 backdrop-blur-md">
            <div className="flex items-center gap-2 text-xs font-mono text-cyan-400 font-bold mb-2">
              <Key size={14} /> Authentication Header
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Every incoming HTTP request requires your workspace token map passed into the <code className="text-slate-200 font-mono text-[11px] bg-slate-900 px-1 rounded">X-API-Key</code> request header.
            </p>
          </div>

          <div className="p-5 rounded-xl border border-slate-800 bg-slate-950/40 backdrop-blur-md font-mono text-[11px] space-y-3">
            <div className="text-xs font-sans font-bold text-slate-300 border-b border-slate-900 pb-1.5 uppercase flex items-center gap-2">
              <RefreshCw size={13} className="text-cyan-400" /> Validation Protocols
            </div>

            <div>
              <span className="text-cyan-400 font-bold">idempotency_key (String):</span>
              <p className="text-slate-400 text-xs mt-0.5 font-sans">
                A strictly unique tracking token hash (UUIDv4) passed per individual runtime step to prevent dirty state data replication or processing duplicate retries.
              </p>
            </div>

            <div>
              <span className="text-cyan-400 font-bold">task_name (String):</span>
              <p className="text-slate-400 text-xs mt-0.5 font-sans">
                The identifier for your current agent run loop execution tracking session context.
              </p>
            </div>

            <div>
              <span className="text-cyan-400 font-bold">input_data (Object):</span>
              <p className="text-slate-400 text-xs mt-0.5 font-sans">
                A dynamic dictionary container context. Send an empty object shell <code className="text-cyan-300 font-mono">{}</code> to run basic telemetry or workflow tracing logs without prompt costs. Include a <code className="text-cyan-300 font-mono">&quot;prompt&quot;</code> key value to enable active AI inference execution.
              </p>
            </div>
          </div>
        </div>

        {/* RIGHT COMPONENT: INTEGRATION SHELL CONSOLE */}
        <div className="lg:col-span-3 border border-slate-800 rounded-2xl bg-slate-950 overflow-hidden flex flex-col h-[460px]">
          <div className="bg-slate-900/80 px-4 py-3 flex items-center justify-between border-b border-slate-800/80">
            <span className="text-[10px] font-mono uppercase tracking-widest text-slate-500 flex items-center gap-2">
              <Terminal size={12} />
              {activeTab === "free" ? "POST /steps/execute" : "POST /mcp/execute"}
            </span>

            <button
              onClick={() => copyToClipboard(currentSnippet)}
              className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800/60 transition-colors"
            >
              {copied ? <Check size={14} className="text-emerald-400" /> : <Copy size={14} />}
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