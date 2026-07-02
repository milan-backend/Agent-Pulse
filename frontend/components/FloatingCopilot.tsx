"use client";
import React, { useState, useRef, useEffect } from "react";
import { askCopilotService } from "./api"; // Targets components/api.ts directly

interface Message {
  id: number;
  type: "user" | "system";
  text: string;
}

export default function FloatingCopilot() {
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [messages, setMessages] = useState<Message[]>([
    { 
      id: 1, 
      type: "system", 
      text: "👋 Welcome to AgentPulse!\n\nI'm the AgentPulse Copilot. I can help you understand the platform, create AI agents, explain integrations, runtime guard, monitoring, pricing, and documentation.\n\nAsk me anything about AgentPulse." 
    }
  ]);
  const [input, setInput] = useState<string>((""));
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Suggested starter questions
  const starterQuestions = [
    "What is AgentPulse?",
    "What core problems does it solve for developers?",
    "How do the security and BYOK features work?",
    "Can you explain the runtime Guardrail protection?"
  ];

  // Auto-scroll logic
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleExecuteQuery = async (queryText: string) => {
    if (!queryText.trim() || isLoading) return;

    setMessages((prev) => [...prev, { id: Date.now(), type: "user", text: queryText }]);
    setIsLoading(true);

    // Call your centralized components/api.ts service layer
    const copilotResponse = await askCopilotService(queryText);

    setMessages((prev) => [...prev, { id: Date.now() + 1, type: "system", text: copilotResponse }]);
    setIsLoading(false);
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const query = input.trim();
    setInput("");
    handleExecuteQuery(query);
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 font-sans select-none">
      
      {/* 🔮 1. FLOATING TOGGLE BUTTON */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="flex items-center space-x-2 bg-gradient-to-r from-cyan-500 via-blue-600 to-indigo-600 text-slate-950 font-black px-5 py-3.5 rounded-full shadow-[0_0_25px_rgba(6,182,212,0.4)] transition-all duration-300 hover:scale-105 active:scale-95 group border border-cyan-400/30"
        >
          <div className="relative flex h-3 w-3 mr-1">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-slate-950 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-slate-950"></span>
          </div>
          <svg 
            className="w-5 h-5 text-slate-950 transform group-hover:rotate-12 transition-transform duration-300" 
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor" 
            strokeWidth={2.5}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M8 10h.01M12 10h.01M16 10h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          <span className="text-xs font-mono tracking-widest text-slate-950">LAUNCH_COPILOT</span>
        </button>
      )}

      {/* 🖥️ TRANSLUCENT CYBER CHAT PANEL */}
      {isOpen && (
        <div className="w-85 md:w-96 h-[560px] bg-[#060b13]/95 backdrop-blur-xl rounded-2xl border border-cyan-500/20 shadow-[0_0_50px_rgba(0,0,0,0.8)] flex flex-col overflow-hidden animate-in fade-in slide-in-from-bottom-6 duration-300">
          
          {/* Top Panel Operational Header */}
          <div className="bg-[#0c1424]/80 backdrop-blur-md px-4 py-3.5 border-b border-slate-800/60 flex items-center justify-between shadow-sm">
            <div className="flex items-center space-x-2.5">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <div className="flex flex-col">
                <span className="text-xs font-black font-mono tracking-widest bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">AGENT_PULSE_COPILOT</span>
                <span className="text-[9px] font-mono text-emerald-400 uppercase tracking-tight">🟢 Powered by AgentPulse Runtime</span>
              </div>
            </div>
            <button 
              onClick={() => setIsOpen(false)}
              className="text-slate-500 hover:text-cyan-400 font-mono text-[10px] tracking-widest bg-slate-900/50 hover:bg-slate-900 px-2 py-1 rounded border border-slate-800/80 transition-colors"
            >
              [MINIMIZE]
            </button>
          </div>

          {/* Chat Stream Viewport Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-[#04080f]/40 custom-scrollbar flex flex-col">
            {messages.map((msg) => (
              <div key={msg.id} className={`flex ${msg.type === "user" ? "justify-end" : "justify-start"} animate-in fade-in duration-200`}>
                <div className={`max-w-[85%] p-3 rounded-xl text-xs leading-relaxed font-mono tracking-wide transition-all shadow-md select-text ${
                  msg.type === "user" 
                    ? "bg-gradient-to-br from-cyan-950/60 to-blue-950/40 text-cyan-200 border border-cyan-500/30 rounded-br-none shadow-[0_0_15px_rgba(6,182,212,0.05)]" 
                    : "bg-[#0c1322]/90 text-slate-300 border border-slate-800/80 rounded-bl-none"
                }`}>
                  <div className="text-[9px] font-bold tracking-widest uppercase mb-1.5 opacity-40">
                    {msg.type === "user" ? "► INBOUND_REQ" : "▲ COPILOT_OUT"}
                  </div>
                  <p className="whitespace-pre-wrap selection:bg-cyan-500/30">{msg.text}</p>
                </div>
              </div>
            ))}
            
            {/* 🔄 4. IMPROVED LOADING ANIMATION STATE */}
            {isLoading && (
              <div className="flex justify-start animate-pulse">
                <div className="bg-[#0c1322]/90 text-cyan-400 border border-cyan-500/10 max-w-[85%] p-3.5 rounded-xl rounded-bl-none text-[11px] font-mono flex items-center space-x-3 shadow-sm">
                  <div className="relative w-3 h-3">
                    <div className="absolute w-full h-full border-2 border-cyan-500/30 rounded-full"></div>
                    <div className="absolute w-full h-full border-2 border-transparent border-t-cyan-400 rounded-full animate-spin"></div>
                  </div>
                  <span className="tracking-wide text-slate-400 text-[10px]">Searching documentation & thinking...</span>
                </div>
              </div>
            )}

            {/* 🎯 3. CLICKABLE SUGGESTED QUESTIONS BLOCK */}
            {messages.length === 1 && !isLoading && (
              <div className="mt-auto pt-4 space-y-2">
                <p className="text-[10px] font-mono text-slate-500 uppercase tracking-widest mb-1">Suggested Enquiries:</p>
                <div className="grid grid-cols-1 gap-2">
                  {starterQuestions.map((question, index) => (
                    <button
                      key={index}
                      onClick={() => handleExecuteQuery(question)}
                      className="text-left bg-[#0c1322]/60 hover:bg-cyan-950/40 text-slate-400 hover:text-cyan-400 border border-slate-800/80 hover:border-cyan-500/30 p-2.5 rounded-lg text-xs font-mono transition-all duration-200 ease-in-out"
                    >
                      💡 {question}
                    </button>
                  ))}
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Inbound Terminal Prompt Action Form */}
          <form onSubmit={handleFormSubmit} className="p-3 bg-[#0c1424]/90 border-t border-slate-800/80 flex flex-col space-y-2 shadow-2xl">
            <div className="flex space-x-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                // 🎯 2. NATURAL INTERACTIVE PLACEHOLDERS
                placeholder={isLoading ? "AgentPulse Copilot is processing..." : "Ask about AgentPulse or runtime monitoring..."}
                className="flex-1 bg-[#050911] border border-slate-800 focus:border-cyan-500/50 rounded-lg px-3 py-2.5 text-xs font-mono text-slate-100 focus:outline-none placeholder-slate-600 transition-all shadow-inner"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={isLoading || !input.trim()}
                className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 disabled:from-slate-800 disabled:to-slate-800 disabled:text-slate-600 text-slate-950 font-black font-mono text-xs px-4 py-2.5 rounded-lg transition-all shadow-md uppercase tracking-wider"
              >
                RUN
              </button>
            </div>
            
            {/* 🏷️ 5. TINY SUBTLE BRANDING */}
            <div className="text-center text-[9px] font-mono text-slate-600 tracking-widest pt-1 uppercase">
              ⚡ Powered by an AgentPulse Agent
            </div>
          </form>
        </div>
      )}

      {/* Inline Styled CSS Injection for custom scrollbar aesthetics */}
      <style jsx global>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #1e293b;
          border-radius: 99px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: #0891b2;
        }
      `}</style>
    </div>
  );
}