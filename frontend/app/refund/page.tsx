import React from "react";

export const metadata = {
  title: "Refund Policy | AgentPulse Observability",
  description: "Review our clear parameters for subscription cancelations, refund eligibility rules, and third-party API fee exceptions.",
};

export default function RefundPolicy() {
  return (
    <div className="min-h-screen bg-black text-slate-300 font-sans relative pt-28 pb-20">
      <div className="absolute bottom-[5%] left-[5%] h-[350px] w-[350px] rounded-full bg-cyan-500/5 blur-[100px] pointer-events-none" />

      <main className="max-w-4xl mx-auto px-6 relative z-10">
        <div className="border-b border-slate-900 pb-6 mb-10">
          <span className="text-xs font-mono text-cyan-400 font-bold uppercase tracking-widest">Financial Policy</span>
          <h1 className="text-3xl md:text-5xl font-black text-white mt-1">Refund & Cancelation Policy</h1>
          <p className="text-xs text-slate-500 font-mono mt-2">LAST MODIFIED: JUNE 15, 2026</p>
        </div>

        <div className="space-y-8 text-sm leading-relaxed text-slate-400 font-sans">
          <section>
            <h2 className="text-lg font-bold text-white mb-3">1. Subscription Cancelation Rules</h2>
            <p>
              You may cancel your recurring AgentPulse subscription plan at any moment through your dashboard settings page. Upon submission of a cancellation request, your workspace privileges will remain active until the end of your current paid billing period, and no further automatic renewals will process.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-white mb-3">2. Refund Eligibility Criteria</h2>
            <p>
              If you are dissatisfied with our tracking system or encounter technical integration blocks during your initial rollout, you can request a full refund within **7 days** of your initial transaction. Refund requests submitted after this 7-day period are not eligible for compensation.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-white mb-3 text-amber-400">3. Absolute Exclusion of Third-Party Model Costs</h2>
            <p className="bg-slate-950/80 border border-slate-900 p-4 rounded-xl text-xs font-mono text-slate-300 leading-relaxed">
              ⚠️ EXCLUSION CRITERIA: AgentPulse tracks and manages your agent executions, but we do not issue refunds for any model tokens consumed through your own API credentials (BYOK). Any expenditure incurred via OpenAI, Anthropic, or external inference engines due to loop script failures or retry triggers is your exclusive financial responsibility.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-white mb-3">4. Request Pipeline & Settlement Times</h2>
            <p>
              To initiate an official refund evaluation, dispatch an email explicitly outlining your workspace ID tracking context to <span className="text-cyan-400 font-mono text-xs">milancharan847@gmail.com</span>. Eligible refund requests are processed within 5 to 10 business days and are credited back through the payment method used during checkout.
            </p>
          </section>
        </div>
      </main>
    </div>
  );
}