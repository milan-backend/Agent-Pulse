"use client";

import React, { useState, useEffect } from "react";
import { CheckCircle2, Cpu, ChevronDown, Key, Globe } from "lucide-react";
import MatrixBg from "@/components/MatrixBg";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

interface FAQItem {
  question: string;
  answer: string;
}

export default function PricingPage() {
  const [isYearly, setIsYearly] = useState<boolean>(false);
  const [openFaq, setOpenFaq] = useState<number | null>(null);
  const [isIndia, setIsIndia] = useState<boolean>(true);
  const [detectingRegion, setDetectingRegion] = useState<boolean>(true);

  // Automatic locale tracking matrix context synchronization
  useEffect(() => {
    const locateUserRegion = async () => {
      try {
        const response = await fetch("https://ip-api.com/json/");
        const data = await response.json();
        if (data && data.countryCode) {
          setIsIndia(data.countryCode === "IN");
        }
      } catch (err) {
        setIsIndia(true); // Secure fallback constraint strategy
      } finally {
        setDetectingRegion(false);
      }
    };
    locateUserRegion();
  }, []);

  const toggleFaq = (index: number): void => {
    setOpenFaq(openFaq === index ? null : index);
  };

  const faqs: FAQItem[] = [
    {
      question: "Are LLM token generation fees included in the subscription plans?",
      answer: "No. AgentPulse runs on a strict Bring Your Own Key (BYOK) model. Your subscription handles infrastructure, concurrency mechanics, dashboard webhooks, analytics, and loop guardrails. The raw AI tokens consumed during agent runtimes are billed directly to your personal OpenAI, Anthropic, or Gemini API keys by those respective platforms.",
    },
    {
      question: "What happens when the Free Sandbox shared key hits a resource limit?",
      answer: "Since the Free Sandbox tier runs on a shared community API key, it is subject to global rate limits. If the shared tier resources are exhausted, the app will return a standard HTTP 429 error and instantly prompt you with a dashboard suggestion to add your own personal API key (BYOK) so your agents can keep running without interruptions.",
    },
    {
      question: "How does the Bring Your Own API Key (BYOK) model fix rate limits?",
      answer: "By plugging your own free or paid Gemini, OpenAI, or Anthropic keys directly into your AgentPulse settings, your workspace completely detaches from our shared infrastructure queue. Your agents will run on your personal key limits, ensuring 100% availability for your workflows.",
    }
  ];

  return (
    <div className="min-h-screen bg-black text-slate-100 font-sans selection:bg-cyan-500/30 relative overflow-x-hidden">
      <MatrixBg />
      <Navbar />

      <section className="max-w-7xl mx-auto px-6 pt-36 relative z-10">
        <div className="text-center max-w-3xl mx-auto mb-12">
          <span className="text-xs font-mono text-cyan-400 font-bold uppercase tracking-widest bg-cyan-500/5 px-3 py-1.5 rounded-full border border-cyan-500/10">
            Plans & Environments
          </span>
          <h1 className="text-4xl md:text-6xl font-black text-white mb-4 tracking-tight mt-4">
            Predictable <span className="bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">Runtime Pricing</span>
          </h1>
          <p className="text-slate-400 text-sm md:text-base font-sans max-w-xl mx-auto">
            Scale your autonomous agent fleets sustainably with our clean orchestration infrastructure. Connect your own custom model keys for complete workspace autonomy.
            {detectingRegion ? " (Sniffing locale...)" : isIndia ? " 🇮🇳 INR Tier Active" : " 🌐 USD Tier Active"}
          </p>

          {/* DISPLAY CONTROLS ROW */}
          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            {/* DYNAMIC MONTHLY / YEARLY TOGGLE */}
            <div className="inline-flex items-center gap-3 bg-slate-950 border border-slate-800 p-1.5 rounded-xl backdrop-blur-md">
              <button
                onClick={() => setIsYearly(false)}
                className={`px-4 py-2 rounded-lg text-xs font-mono font-bold transition-all ${
                  !isYearly ? "bg-cyan-500/10 text-cyan-300 border border-cyan-500/20" : "text-slate-400 hover:text-slate-200"
                }`}
              >
                MONTHLY
              </button>
              <button
                onClick={() => setIsYearly(true)}
                className={`px-4 py-2 rounded-lg text-xs font-mono font-bold transition-all flex items-center gap-1.5 ${
                  isYearly ? "bg-cyan-500/10 text-cyan-300 border border-cyan-500/20" : "text-slate-400 hover:text-slate-200"
                }`}
              >
                YEARLY <span className="text-[10px] bg-emerald-500/20 text-emerald-400 px-1.5 py-0.5 rounded font-sans font-black uppercase tracking-wide">SAVE 20%</span>
              </button>
            </div>

            {/* EXTERNAL CURRENCY FALLBACK TOGGLE */}
            <div className="bg-slate-950 border border-slate-800 p-1.5 rounded-xl flex items-center gap-2 backdrop-blur-md">
              <button 
                onClick={() => setIsIndia(true)} 
                className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold transition-all ${isIndia ? "bg-cyan-500/10 text-cyan-300 border border-cyan-500/20" : "text-slate-400 hover:text-slate-200"}`}
              >
                🇮🇳 INR
              </button>
              <button 
                onClick={() => setIsIndia(false)} 
                className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold transition-all flex items-center gap-1 ${!isIndia ? "bg-cyan-500/10 text-cyan-300 border border-cyan-500/20" : "text-slate-400 hover:text-slate-200"}`}
              >
                <Globe size={12} /> USD
              </button>
            </div>
          </div>
        </div>

        {/* 🔑 HIGH-VISIBILITY BYOK ARCHITECTURAL TRANSPARENCY NOTICE */}
        <div className="max-w-4xl mx-auto mb-16 rounded-3xl border border-amber-500/20 bg-gradient-to-r from-amber-500/5 to-transparent p-6 flex flex-col md:flex-row items-start md:items-center gap-5 backdrop-blur-md">
          <div className="h-12 w-12 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center shrink-0">
            <Key size={22} className="text-amber-400" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-amber-300 uppercase tracking-wide font-mono">Bring Your Own Key (BYOK) Operational Policy</h4>
            <p className="text-slate-400 text-xs mt-1 leading-relaxed">
              AgentPulse charges exclusively for running infrastructure coordination and loops. **Users link their own external keys** (OpenAI, Anthropic, or Gemini) inside settings. Any inference usage costs are paid directly to those respective AI key providers and are not included in subscription plan costs.
            </p>
          </div>
        </div>

        {/* CARDS MATRIX */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-stretch max-w-6xl mx-auto mb-28">
          
          {/* FREE PLAN */}
          <div className="rounded-3xl border border-slate-900 bg-slate-950/40 p-8 flex flex-col justify-between backdrop-blur-md relative group hover:border-slate-800 transition-all">
            <div>
              <h3 className="text-xl font-black text-white">Free Sandbox</h3>
              <p className="text-xs text-slate-400 mt-2 min-h-[32px]">
                Perfect for basic workflow testing using our shared community keys or your personal links.
              </p>

              <div className="mt-6 flex items-baseline gap-1">
                <span className="text-5xl font-black text-white">{isIndia ? "₹0" : "$0"}</span>
                <span className="text-xs font-mono text-slate-500">/ month</span>
              </div>

              <div className="mt-8 space-y-4 border-t border-slate-900 pt-6">
                <div className="text-[10px] font-mono uppercase tracking-widest text-slate-500 font-bold mb-1">Execution Guardrails</div>
                {[
                  "Shared Community API Key Tier",
                  "Auto-Prompt to add your own key on HTTP 429",
                  "Bring Your Own API Key (BYOK) Ready",
                  "Agent State Controls (Pause / Resume / Kill)",
                  "Audit & Event History Logs Active",
                  "1 Active AI Agent Capacity",
                  "1 Concurrent Agent Execution Window",
                  "10 Total Runtime Hours Limit",
                  "Live WebSocket Dashboard Updates",
                  "Standard Performance Analytics",
                  "No RAG Knowledge Document Uploads"
                ].map((feat, i) => (
                  <div key={i} className="flex items-center gap-3 text-xs text-slate-300 font-sans">
                    <CheckCircle2 size={14} className="text-cyan-500 shrink-0" />
                    <span className={feat.startsWith("No") || feat.includes("Shared") ? "text-slate-400" : ""}>{feat}</span>
                  </div>
                ))}
              </div>
            </div>

            <button className="w-full mt-8 py-4 bg-slate-900/60 border border-slate-800/80 text-slate-400 font-bold font-mono text-xs uppercase tracking-wider rounded-xl cursor-default">
              Current Tier Access
            </button>
          </div>

          {/* PRO PLAN */}
          <div className="rounded-3xl border-2 border-cyan-400 bg-gradient-to-b from-slate-950 to-slate-900/60 p-8 flex flex-col justify-between relative shadow-[0_0_50px_rgba(34,211,238,0.1)] transform lg:scale-[1.02]">
            <div className="absolute top-4 right-4 px-3 py-1 bg-cyan-400 text-black font-mono font-black text-[10px] uppercase rounded-full tracking-wider">
              Recommended
            </div>

            <div>
              <h3 className="text-xl font-black text-white flex items-center gap-2">
                Pro Stack <Cpu size={16} className="text-cyan-400" />
              </h3>
              <p className="text-xs text-slate-400 mt-2 min-h-[32px]">
                Advanced runtime controls and custom key integrations for team collaboration workflows.
              </p>

              <div className="mt-6 flex items-baseline gap-1">
                <span className="text-4xl md:text-5xl font-black text-white">
                  {isIndia 
                    ? (isYearly ? "₹2,174" : "₹2,740") 
                    : (isYearly ? "$23" : "$29")}
                </span>
                <span className="text-xs font-mono text-slate-400">/{isYearly ? "mo billed yearly" : "month"}</span>
              </div>

              <div className="mt-8 space-y-4 border-t border-cyan-950 pt-6">
                <div className="text-[10px] font-mono uppercase tracking-widest text-cyan-400 font-bold mb-1">Execution Guardrails</div>
                {[
                  "Bring Your Own API Key (BYOK) Native Integration",
                  "Agent State Controls (Pause / Resume / Kill)",
                  "Automated Budget Ceiling Guardrails",
                  "State Loop & Infinite Execution Detection",
                  "Multi-Workspace Partitioning Active",
                  "Model Context Protocol (MCP Layer Access)",
                  "RAG Documents Enabled (Up to 20 files)",
                  "10 Active AI Agent Capacity",
                  "5 Concurrent Agent Executions",
                  "100 Total Runtime Hours Limit",
                  "10 Team Member Seats Allocated",
                  "Workspace Bulk Controls (Kill All / Resume All)",
                  "Priority Asynchronous Execution Queues"
                ].map((feat, i) => (
                  <div key={i} className="flex items-center gap-3 text-xs text-slate-200 font-sans font-medium">
                    <CheckCircle2 size={14} className="text-cyan-400 shrink-0" />
                    <span>{feat}</span>
                  </div>
                ))}
              </div>
            </div>

            <button className="w-full mt-8 py-4 bg-cyan-400 text-black font-black font-mono text-xs uppercase tracking-wider rounded-xl hover:shadow-[0_0_20px_rgba(34,211,238,0.4)] hover:scale-[1.01] transition-all">
              Upgrade to Pro Plan
            </button>
          </div>

          {/* ENTERPRISE PLAN */}
          <div className="rounded-3xl border border-slate-900 bg-slate-950/40 p-8 flex flex-col justify-between backdrop-blur-md relative group hover:border-slate-800 transition-all">
            <div>
              <h3 className="text-xl font-black text-white">Enterprise Node</h3>
              <p className="text-xs text-slate-400 mt-2 min-h-[32px]">
                Full scaling metrics capacity and high-throughput logs for corporate cluster deployments.
              </p>

              <div className="mt-6 flex items-baseline gap-1">
                <span className="text-4xl md:text-5xl font-black text-white">
                  {isIndia 
                    ? (isYearly ? "₹15,025" : "₹18,805") 
                    : (isYearly ? "$159" : "$199")}
                </span>
                <span className="text-xs font-mono text-slate-500">/{isYearly ? "mo billed yearly" : "month"}</span>
              </div>

              <div className="mt-8 space-y-4 border-t border-slate-900 pt-6">
                <div className="text-[10px] font-mono uppercase tracking-widest text-slate-500 font-bold mb-1">Execution Guardrails</div>
                {[
                  "Bring Your Own API Key (BYOK) Native Integration",
                  "Agent State Controls (Pause / Resume / Kill)",
                  "Automated Budget Ceiling Guardrails",
                  "Enterprise Role-Based Access Control (RBAC)",
                  "RAG Knowledge Documents (Up to 1,000 files)",
                  "100 Active AI Agent Capacity",
                  "100 Concurrent Agent Executions",
                  "10,000 Total Runtime Hours Limit",
                  "100 Team Member Seats Allocated",
                  "Infinite Telemetry Audit Log History",
                  "Workspace Bulk Controls (Kill All / Resume All)"
                ].map((feat, i) => (
                  <div key={i} className="flex items-center gap-3 text-xs text-slate-300 font-sans">
                    <CheckCircle2 size={14} className="text-emerald-400 shrink-0" />
                    <span>{feat}</span>
                  </div>
                ))}
              </div>
            </div>

            <button className="w-full mt-8 py-4 bg-emerald-500 text-black font-black font-mono text-xs uppercase tracking-wider rounded-xl hover:bg-emerald-400 transition-colors">
              Contact Infrastructure Sales
            </button>
          </div>

        </div>

        {/* CLEAN NOTIFIED FAQ SECTION */}
        <div className="max-w-4xl mx-auto pb-24 border-t border-slate-900/60 pt-20">
          <div className="flex items-center justify-center gap-2 mb-12 text-center">
            <h2 className="text-2xl md:text-3xl font-black text-white font-sans">System Operations FAQ</h2>
          </div>

          <div className="space-y-4">
            {faqs.map((faq, idx) => {
              const isOpen = openFaq === idx;
              return (
                <div key={idx} className="border border-slate-900 bg-slate-950/20 rounded-2xl overflow-hidden transition-all backdrop-blur-md">
                  <button
                    onClick={() => toggleFaq(idx)}
                    className="w-full px-6 py-5 flex items-center justify-between text-left bg-slate-950/40 hover:bg-slate-900/20 transition-colors"
                  >
                    <span className="text-xs md:text-sm font-bold text-slate-200 font-sans">{faq.question}</span>
                    <ChevronDown size={16} className={`text-slate-500 transition-transform duration-300 ${isOpen ? "rotate-180 text-cyan-400" : ""}`} />
                  </button>
                  <div className={`transition-all duration-300 ease-in-out overflow-hidden ${isOpen ? "max-h-40 border-t border-slate-900/60" : "max-h-0"}`}>
                    <p className="p-6 text-xs text-slate-400 leading-relaxed font-sans bg-black/40">
                      {faq.answer}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}