import React from "react";

export const metadata = {
  title: "Privacy Policy | AgentPulse Observability",
  description: "Review our strict handling methods regarding cryptographic API key isolation, trace log retention, and vector security profiles.",
};

export default function PrivacyPolicy() {
  return (
    <div className="min-h-screen bg-black text-slate-300 font-sans relative pt-28 pb-20">
      <div className="absolute top-[-5%] right-[10%] h-[400px] w-[400px] rounded-full bg-purple-500/5 blur-[120px] pointer-events-none" />

      <main className="max-w-4xl mx-auto px-6 relative z-10">
        <div className="border-b border-slate-900 pb-6 mb-10">
          <span className="text-xs font-mono text-purple-400 font-bold uppercase tracking-widest">Compliance Node</span>
          <h1 className="text-3xl md:text-5xl font-black text-white mt-1">Privacy Policy</h1>
          <p className="text-xs text-slate-500 font-mono mt-2">LAST MODIFIED: JUNE 15, 2026</p>
        </div>

        <div className="space-y-8 text-sm leading-relaxed text-slate-400">
          <section>
            <h2 className="text-lg font-bold text-white mb-3 font-sans">1. Scope of Information Collected</h2>
            <p>
              To maintain absolute execution transparency, AgentPulse collects explicit data arrays directly linked to the performance of your systems at <span className="text-slate-200 font-mono text-xs">https://agentpulseai.dev</span>. This includes account creation signatures, user profile strings, and transactional billing events.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-white mb-3 font-sans">2. Ingestion of Workspace & Telemetry Data</h2>
            <p>
              Our telemetry nodes capture agent step execution logs, token counts, error states, and latency metrics. This raw data stream is handled purely to populate your analytical dashboards, trigger user-defined ceiling budget controls, and fuel our real-time state machine loop guards.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-white mb-3 font-sans">3. RAG Source Attribution Data Processing</h2>
            <p>
              When utilizing our **RAG Source Attribution** engine, your agent systems stream raw document vector citations and reference text snapshots to our backend. These text elements are isolated inside your designated tenant workspace database partition and are used strictly to provide trace visibility for your developers. We never scrape, evaluate, or utilize your proprietary RAG documents to train any internal machine learning models.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-white mb-3 font-sans">4. Bring Your Own Key (BYOK) Cryptographic Handling</h2>
            <p className="border-l-2 border-cyan-400 pl-4 font-mono text-xs text-slate-400 bg-slate-950/60 p-4 rounded-r-xl">
              SECURITY PROTOCOL MANDATE: Any third-party model provider credentials or API keys you inject into our system are instantly encrypted at rest using AES-256 standard encryption keys before being committed to our secure key vault. These strings are decrypted only in memory during live runtime executions.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-white mb-3 font-sans">5. Cookies & Core Analytical Trackers</h2>
            <p>
              We deploy strict, secure tracking cookies to maintain authenticated session contexts and capture general application traffic trends via privacy-respecting analytics engines. We do not integrate data brokers or sell user tracking behaviors to ad networks.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-white mb-3 font-sans">6. Retention Framework & User Rights</h2>
            <p>
              Your execution traces and audit trails remain cached based on your chosen billing tier parameters (Free, Pro, or Enterprise). Users retain full authority to request complete deletion of account structures, historical trace records, and cached encrypted key vault keys by contacting our response line at <span className="text-cyan-400 font-mono text-xs">milancharan847@gmail.com</span>.
            </p>
          </section>
        </div>
      </main>
    </div>
  );
}