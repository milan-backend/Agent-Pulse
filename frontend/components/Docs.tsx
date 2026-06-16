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
  ServerCrash
} from "lucide-react";

export default function Docs() {
  const [activeTab, setActiveTab] = useState("free");
  const [copied, setCopied] = useState(false);

  // Both pro and enterprise map straight to your verified live MCP endpoints from swagger!
  const codeSnippets = {
    free: `import requests
import uuid

BACKEND_URL = "https://api.agentpulseai.dev"
AGENT_API_KEY = "ap_agent_xxxxxxxxxxxxxxxxx"

# =========================================================
# MODE A: INFRASTRUCTURE TRACING LOGS ONLY (NO AI PROMPT)
# Leaves input_data empty to bypass external AI rate limits
# =========================================================
infra_payload = {
    "task_name": "Telemetry-Sync-Run-01",  # Cooldown applied on duplicate task names
    "input_data": {},                     # Empty object = tracing active, model skipped!
    "idempotency_key": str(uuid.uuid4())  # Strictly unique UUID per individual call step
}

# =========================================================
# MODE B: ACTIVE INFERENCE WORKFLOW (WITH AI PROMPT)
# Triggers your dynamic model loops using your backend BYOK keys
# =========================================================
inference_payload = {
    "task_name": "Market-Analysis-Stream",
    "input_data": {
        "prompt": "Analyze high-throughput real-time AI cluster workloads"
    },
    "idempotency_key": str(uuid.uuid4())
}

# ✅ CORRECTION: Headers fixed to use production "X-API-Key" parameter mapping
response = requests.post(
    f"{BACKEND_URL}/steps/execute",
    headers={
        "X-API-Key": AGENT_API_KEY,
        "Content-Type": "application/json"
    },
    json=infra_payload # Swap with inference_payload depending on operational targets
)

print(response.json())`,

    pro: `# 1. GET https://api.agentpulseai.dev/mcp/tools
# RESPONSE BODY (Schema tool definitions mapping):
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

# 2. POST https://api.agentpulseai.dev/mcp/execute
# REQUEST BODY (Wrapped Tool Dispatch payload format):
{
  "tool": "execute_task",
  "arguments": {
    "task_name": "Market Research",
    "input_data": {
      "prompt": "Analyze AI observability platforms"
    },
    "idempotency_key": "errt"
  }
}

# RESPONSE BODY (Async Telemetry Queue tracking handle):
{
  "message": "Step scheduled",
  "step_id": "647127bb-fc97-4955-83d2-b9b303fc4e91",
  "status": "pending"
}`,

    enterprise: `# 1. GET https://api.agentpulseai.dev/mcp/tools
# RESPONSE BODY (Schema tool definitions mapping on Dedicated Node):
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

# 2. POST https://api.agentpulseai.dev/mcp/execute
# REQUEST BODY (Wrapped Tool Dispatch payload format on Dedicated Node):
{
  "tool": "execute_task",
  "arguments": {
    "task_name": "Enterprise Production Run",
    "input_data": {
      "prompt": "Execute high-throughput workflow cluster analysis"
    },
    "idempotency_key": "enterprise-secure-hash-01"
  }
}

# RESPONSE BODY (Async Telemetry Queue tracking handle):
{
  "message": "Step scheduled",
  "step_id": "893217cc-ad83-4211-92b1-c8c303fa4192",
  "status": "pending"
}`
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section id="docs" className="max-w-7xl mx-auto px-6 pt-32 relative z-10">
      <div className="text-center mb-16">
        <h2 className="text-3xl md:text-5xl font-black text-white mb-4 font-sans">
          Developer Documentation & Integration
        </h2>
        <p className="text-slate-400 text-base md:text-lg max-w-2xl mx-auto">
          Review production schemas and system protocols across our available workspace operational environments.
        </p>
      </div>

      {/* CORE SELECTOR STRIP */}
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
          <Building2 size={14} /> Enterprise Plan: Dedicated Ops
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-8 items-start max-w-6xl mx-auto">

        {/* LEFT COMPONENT: CONTENT EXPLANATIONS */}
        <div className="lg:col-span-2 space-y-4">

          {activeTab === "free" && (
            <>
              <div className="p-5 rounded-xl border border-slate-800 bg-slate-950/40 backdrop-blur-md">
                <div className="flex items-center gap-2 text-xs font-mono text-cyan-400 font-bold mb-2">
                  <Key size={14} /> API Key Management
                </div>
                <p className="text-xs text-slate-400 leading-relaxed">
                  When an agent is initialized, a unique API token signature generates instantly. Pass this string into the <code className="text-slate-200 font-mono text-[11px] bg-slate-900 px-1 rounded">X-API-Key</code> request header context to establish a secure database session hook.
                </p>
              </div>

              <div className="p-5 rounded-xl border border-slate-800 bg-slate-950/40 backdrop-blur-md font-mono text-[11px] space-y-3">
                <div className="text-xs font-sans font-bold text-slate-300 border-b border-slate-900 pb-1.5 uppercase flex items-center gap-2">
                  <RefreshCw size={13} className="text-cyan-400" /> Validation Parameters
                </div>

                <div>
                  <span className="text-cyan-400 font-bold">idempotency_key:</span>
                  <p className="text-slate-400 text-xs mt-0.5 font-sans">
                    Enforce a strictly unique runtime hash identifier (UUIDv4) per individual network request step to prevent dirty trace data or duplicate action logging.
                  </p>
                </div>

                <div>
                  <span className="text-cyan-400 font-bold">task_name:</span>
                  <p className="text-slate-400 text-xs mt-0.5 font-sans">
                    Consecutive identical task names trigger an intentional execution cooldown limit block to protect your processing buffers against infinite loops.
                  </p>
                </div>

                <div>
                  <span className="text-cyan-400 font-bold">input_data:</span>
                  <p className="text-slate-400 text-xs mt-0.5 font-sans">
                    Flexible schema catalog object. Leave empty <code className="text-cyan-300 font-mono">{}</code> for telemetry-only tracking runs. Add a <code className="text-cyan-300 font-mono">&quot;prompt&quot;: &quot;...&quot;</code> key string context to trigger active AI inference processing cycles.
                  </p>
                </div>
              </div>
            </>
          )}

          {activeTab === "pro" && (
            <>
              <div className="p-5 rounded-xl border border-slate-800 bg-slate-950/40 backdrop-blur-md">
                <div className="text-xs font-sans font-bold text-purple-400 mb-2">
                  Model Context Protocol (MCP) Core Integration
                </div>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Both Pro and Enterprise workspaces use this native protocol engine. Instead of writing custom step routes for every single unique function, LLM clusters programmatically discover tools and schedule stateful operations using standardized Anthropic envelopes.
                </p>
              </div>

              <div className="p-5 rounded-xl border border-slate-800 bg-slate-950/40 backdrop-blur-md font-mono text-[11px] space-y-1">
                <div className="text-xs font-sans font-bold text-slate-300 border-b border-slate-900 pb-1.5 uppercase mb-2">
                  Active Framework Endpoints
                </div>
                <div><span className="text-purple-400">GET</span> <span className="text-slate-400">/mcp/tools — Schema discovery array</span></div>
                <div><span className="text-purple-400">POST</span> <span className="text-slate-400">/mcp/execute — Task orchestration channel</span></div>
              </div>
            </>
          )}

          {activeTab === "enterprise" && (
            <>
              <div className="p-5 rounded-xl border border-slate-800 bg-slate-950/40 backdrop-blur-md">
                <div className="flex items-center gap-2 text-xs font-sans text-emerald-400 font-bold mb-2">
                  <ServerCrash size={14} /> Multi-Tenant vs Dedicated Compute
                </div>
                <p className="text-xs text-slate-400 leading-relaxed">
                  While the Pro tier processes your MCP workflows on standard shared cluster threads, the **Enterprise tier** takes your exact same MCP engine configuration and drops it onto completely isolated, single-tenant cloud node infrastructure for maximum throughput and isolation.
                </p>
              </div>

              <div className="p-5 rounded-xl border border-slate-800 bg-slate-950/40 backdrop-blur-md space-y-2 text-xs">
                <div className="font-bold text-slate-300 uppercase tracking-wide border-b border-slate-900 pb-1 mb-1">
                  Corporate Scaling Manifest
                </div>
                <div>⚡ <span className="text-slate-400">Identical MCP engine running on completely dedicated hardware</span></div>
                <div>🔒 <span className="text-slate-400">Isolated VPC perimeter routing boundary rules</span></div>
                <div>📊 <span className="text-slate-400">Infinite immutable logs retention for security compliance audits</span></div>
              </div>
            </>
          )}

        </div>

        {/* RIGHT COMPONENT: INTEGRATION SHELL CONSOLE */}
        <div className="lg:col-span-3 border border-slate-800 rounded-2xl bg-slate-950 overflow-hidden flex flex-col h-[460px]">

          <div className="bg-slate-900/80 px-4 py-3 flex items-center justify-between border-b border-slate-800/80">
            <span className="text-[10px] font-mono uppercase tracking-widest text-slate-500 flex items-center gap-2">
              <Terminal size={12} />
              {activeTab === "free" ? "POST /steps/execute" : "POST /mcp/execute"}
            </span>

            <button
              onClick={() => copyToClipboard(codeSnippets[activeTab as keyof typeof codeSnippets])}
              className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800/60 transition-colors"
            >
              {copied ? <Check size={14} className="text-emerald-400" /> : <Copy size={14} />}
            </button>
          </div>

          <div className="p-5 flex-1 bg-black/40 overflow-y-auto font-mono text-[11px] text-slate-300 leading-relaxed scrollbar-thin scrollbar-thumb-slate-800 scrollbar-track-transparent">
            <pre className="whitespace-pre">
              {codeSnippets[activeTab as keyof typeof codeSnippets]}
            </pre>
          </div>

        </div>

      </div>
    </section>
  );
}