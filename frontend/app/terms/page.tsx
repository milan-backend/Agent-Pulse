"use client";

import React from "react";
import MatrixBg from "@/components/MatrixBg"; // Safely imports your matrix rain effect
import Navbar from "@/components/Navbar";     // Safely imports your top navbar header
import Footer from "@/components/Footer";     // Safely imports your footer navigation layout

export default function TermsOfService() {
  return (
    <div className="min-h-screen bg-black text-slate-100 font-sans selection:bg-cyan-500/30 relative overflow-x-hidden">
      {/* 1. Matrix Animation & Background Glows Context Layer */}
      <MatrixBg />
      
      {/* 2. Top Header Navigation Bar */}
      <Navbar />

      {/* 3. Main Centered Legal Content Shell */}
      <main className="max-w-4xl mx-auto px-6 relative z-10 pt-36 pb-20 font-sans">
        <div className="border-b border-slate-900 pb-6 mb-10">
          <span className="text-xs font-mono text-cyan-400 font-bold uppercase tracking-widest">
            Legal Operations Core
          </span>
          <h1 className="text-3xl md:text-5xl font-black text-white mt-1">
            Terms of Service
          </h1>
          <p className="text-xs text-slate-500 font-mono mt-2">
            LAST MODIFIED: JUNE 16, 2026
          </p>
        </div>

        <div className="space-y-8 text-sm leading-relaxed text-slate-400">
          <section>
            <h2 className="text-lg font-bold text-white mb-3 font-sans">
              1. Acceptance of Terms
            </h2>
            <p>
              By establishing an account structure, accessing our control panels, or querying our ingestion system endpoints at <span className="text-slate-200 font-mono text-xs">https://agentpulseai.dev</span> (collectively, the &quot;Service&quot;), you acknowledge that you have read, understood, and bind your operating identity to these formal Terms of Service. If operating on behalf of an enterprise entity, you warrant that you hold explicit legal authority to bind that entity to these conditions.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-white mb-3 font-sans">
              2. Account Management & Credentials Security
            </h2>
            <p>
              To consume our telemetry-rich monitoring pipelines, users must maintain valid, verified accounts. You assume complete liability for all activities executed under your authentication parameters. You are explicitly responsible for enforcing access constraints across your workspace tokens, API keys, and personnel roles. Notify <span className="text-cyan-400 font-mono text-xs">milancharan847@gmail.com</span> immediately upon any signature compromise.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-white mb-3 font-sans">
              3. Acceptable Use & Prohibited Activities
            </h2>
            <p>You warrant that your autonomous AI execution runs will not be routed to engage in:</p>
            <ul className="list-disc pl-6 mt-2 space-y-1.5 text-slate-400 font-sans">
              <li>Malicious script injection, denial of service attacks, or probing framework vulnerabilities.</li>
              <li>Sourcing, synthesizing, or preparing structural details for hazardous payloads, solid rocket propellants, or improvised explosives devices.</li>
              <li>Deploying hydrocodes or modeling optimization algorithms designed to streamline conventional weapons development.</li>
              <li>Circumventing model safety flags, automating credential brute-forcing, or operating deceptive scraping bots.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-bold text-white mb-3 font-sans">
              4. AI-Generated Content Disclaimer
            </h2>
            <p>
              AgentPulse operates purely as an observability middleware layer and runtime loop safeguard. The automated content, text vectors, script executions, and API function returns produced by your agent systems are generated entirely by external third-party Large Language Models. AgentPulse makes zero assertions regarding the absolute correctness, legal copyright compliance, or semantic safety of your agents&apos; outputs.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-white mb-3 font-sans">
              5. Service Availability & High-Risk Caveats
            </h2>
            <p>
              Our infrastructure is provided on an &quot;AS IS&quot; and &quot;AS AVAILABLE&quot; operational standard. While we deploy real-time telemetry filters, live budget ceiling blocks, and state-machine loop detection mechanisms, you acknowledge that network packet latency, system timeouts, or upstream vendor failures can impact real-time tracking accuracy. AgentPulse is not a fault-tolerant engine and is not designed for deployment in safety-critical environments.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-white mb-3 font-sans">
              6. Subscription Billing, Fees, & Gateways
            </h2>
            <p>
              Access to our Pro Stack and Enterprise planes is governed by recurring subscription tiers. Fees are billed in advance on a recurring monthly or annual processing track. By mapping a corporate card or digital wallet provider through our compliant checkout gateways, you authorize AgentPulse and its Merchant of Record infrastructure to process automated payments until you submit an explicit cancellation request inside your billing sub-dashboard.
            </p>
            {/* 💡 CRITICAL ADDITION: BYOK LEGAL DISCLOSURE CLAUSE */}
            <p className="mt-3 border-l-2 border-cyan-500/30 pl-4 bg-slate-950/40 p-3 rounded-r-xl text-slate-300">
              <strong>6a. Bring Your Own Key (BYOK) Responsibility:</strong> AgentPulse provisions orchestrational middleware, live dashboard webhooks, security guardrails, and concurrency metrics. Subscription fees do <strong>not</strong> include Large Language Model (LLM) tokens or API generation usage charges. Users are strictly required to supply their own proprietary API keys (OpenAI, Anthropic, Gemini, etc.). All backend token consumption costs are billed directly to the user by their respective AI model vendors and remain completely independent of AgentPulse invoicing.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-white mb-3 font-sans">
              7. Account Termination Right
            </h2>
            <p>
              We reserve the absolute right, without prior liability or notice, to suspend or terminate account access instances instantly if we detect violations of our acceptable use covenants, abnormal API endpoint flooding, or fraudulent billing indicators.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-white mb-3 font-sans">
              8. Limitation of Liability
            </h2>
            <p className="bg-slate-950/80 border border-slate-900 p-4 rounded-xl text-xs font-mono text-slate-400 leading-relaxed">
              IN NO EVENT SHALL AGENTPULSE, ITS DIRECTORS, OR ENGINE DEVELOPMENT PARTNERS BE HELD LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES, INCLUDING WITHOUT LIMITATION LOSS OF PROFITS, DATA ASSETS, THIRD-PARTY TOKEN COST INFLATION, OR RUNTIME EXHAUSTION ARISING OUT OF OR IN CONNECTION WITH THE DISPATCH OF AGENT WORKFLOWS.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-white mb-3 font-sans">
              9. Governing Law & Contact Core
            </h2>
            <p>
              These operating terms shall be construed and regulated under the laws of India, without regard to conflicts of law principles. All legal arbitration workflows shall remain under the jurisdiction of local courts within Rajasthan, India. Address all legal inquiries to <span className="text-cyan-400 font-mono text-xs">milancharan847@gmail.com</span>.
            </p>
          </section>
        </div>
      </main>

      {/* 4. Bottom Retention Banner & Footer Links Grid */}
      <Footer />
    </div>
  );
}