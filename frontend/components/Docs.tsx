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

    pro_and_enterprise: `import time
import requests
import uuid

BACKEND_URL = "https://api.agentpulseai.dev"
AGENT_API_KEY = "ap_agent_xxxxxxxxxxxxxxxxx"

def fetch_ai_response(user_prompt):
    headers = {
        "X-API-Key": AGENT_API_KEY,
        "Content-Type": "application/json"
    }

    # Step 1: Send request to AgentPulse to get a unique step_id
    init_payload = {
        "tool": "execute_task",
        "arguments": {
            "task_name": "Production-Worker-Job",
            "input_data": { "prompt": user_prompt },
            "idempotency_key": str(uuid.uuid4())
        }
    }

    init_res = requests.post(f"{BACKEND_URL}/mcp/execute", json=init_payload, headers=headers)
    step_id = init_res.json().get("step_id")
    if not step_id:
        return "Initialization Error"

    # Step 2: Poll status endpoint until the task completes
    status_payload = {
        "tool": "get_step_status",
        "arguments": { "step_id": stepId }
    }

    while True:
        time.sleep(1.5) # Delay interval between polling cycles
        status_res = requests.post(f"{BACKEND_URL}/mcp/execute", json=status_payload, headers=headers)
        
        if status_res.status_code == 200:
            status_data = status_res.json()
            
            if status_data.get("status") == "completed" or "output_data" in status_data:
                output_data = status_data.get("output_data", {})
                
                # Extract the AI response text from AgentPulse
                return output_data.get("result")

# Example integration execution call:
# clean_answer = fetch_ai_response("Your custom prompt query here")
# print(clean_answer)`
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

      {/* 📊 INTEGRATION REQUEST FLOW ARCHITECTURE */}
      <div className="max-w-6xl mx-auto mb-16 p-6 md:p-8 rounded-3xl border border-slate-900 bg-slate-950/20 backdrop-blur-md font-mono text-xs text-slate-300">
        <div className="flex items-center gap-2 text-xs font-mono text-cyan-400 font-bold uppercase tracking-wider mb-6">
          <Play size={14} /> Integration Flow Architecture
        </div>
        <div className="flex flex-col space-y-1.5 overflow-x-auto pb-4 text-slate-400">
          <div>Application ──► Send Request to AgentPulse ──► Authenticate Agent API Key</div>
          <div>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│</div>
          <div>Display Response in Application ◄── Receive Final AI Response ◄── Poll Status Endpoint ◄── Return step_id</div>
        </div>

        {/* STEP BY STEP BREAKDOWN */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6 pt-6 border-t border-slate-900/60 font-sans">
          <div>
            <span className="text-cyan-400 font-mono font-bold block mb-1">Steps 1 & 2</span>
            <p className="text-xs text-slate-400">Send request using your Agent API Key for authentication.</p>
          </div>
          <div>
            <span className="text-cyan-400 font-mono font-bold block mb-1">Steps 3, 4 & 5</span>
            <p className="text-xs text-slate-400">Platform retrieves configuration, executes the task, and returns a step_id.</p>
          </div>
          <div>
            <span className="text-cyan-400 font-mono font-bold block mb-1">Steps 6 & 7</span>
            <p className="text-xs text-slate-400">Poll the status endpoint until the task is complete, then read output_data.result.</p>
          </div>
          <div>
            <span className="text-cyan-400 font-mono font-bold block mb-1">Step 8</span>
            <p className="text-xs text-slate-400">Isolate and securely display the clean response string in your application frontend.</p>
          </div>
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
              <RefreshCw size={13} className="text-cyan-400" /> How to Display the Response
            </div>
            <p className="text-xs text-slate-400 font-sans leading-relaxed">
              The AI response is returned by AgentPulse through the API. Your application is responsible for displaying that response to the end user. AgentPulse manages execution, monitoring, and runtime protection, while your frontend determines how the response is presented.
            </p>
          </div>
        </div>

        {/* RIGHT COMPONENT: INTERACTIVE SHELL CODE CONSOLE WINDOW */}
        <div className="lg:col-span-3 border border-slate-800 rounded-2xl bg-slate-950 overflow-hidden flex flex-col h-[480px] shadow-2xl">
          <div className="bg-slate-900/80 px-4 py-3 flex items-center justify-between border-b border-slate-800/80">
            <span className="text-[10px] font-mono uppercase tracking-widest text-slate-500 flex items-center gap-2">
              <Terminal size={12} />
              {activeTab === "free" ? "POST /steps/execute" : "POST /mcp/execute"}
            </span>

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