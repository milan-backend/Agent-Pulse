"use client";

import React, { useState, useRef, useEffect } from "react";
import { Sparkles, Send, ArrowRight, Bot, Shield, Key, Database, Cpu, Terminal } from "lucide-react";
import { askCopilotService } from "@/components/api"; // Reverted cleanly back to your old stable function[cite: 2]

interface Message {
  id: string;
  type: "user" | "system";
  text: string;
}

export default function DashboardCopilotPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const quickSuggestions = [
    { text: "How do I create an AI agent?", icon: Bot },
    { text: "How does Knowledge (RAG) work?", icon: Database },
    { text: "How do I connect my AI provider?", icon: Key },
    { text: "What is Runtime Guard?", icon: Shield },
    { text: "How do I integrate the API and MCP?", icon: Cpu },
    { text: "Where can I monitor tasks?", icon: Terminal },
  ];

  // 🎯 FIX: Scroll behaves flawlessly inside the container boundaries now
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [messages, isLoading]);

  const handleQuerySubmission = async (queryText: string) => {
    if (!queryText.trim() || isLoading) return;

    const userMessageText = queryText.trim();
    setInput("");
    
    setMessages((prev) => [...prev, { id: crypto.randomUUID(), type: "user", text: userMessageText }]);
    setIsLoading(true);

    try {
      // 🔄 Running clean, stable non-streaming function payload check]
      const copilotResponse = await askCopilotService(userMessageText);
      
      setMessages((prev) => [
        ...prev, 
        { id: crypto.randomUUID(), type: "system", text: copilotResponse }
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { id: crypto.randomUUID(), type: "system", text: "⚠️ An operational processing timeout or connection exception occurred. Please try sending your query again." }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleQuerySubmission(input);
  };

  return (
    /* 🎯 FIX 1: Maximize page height and hide parent document window body overflows */
    <div className="flex h-[calc(100vh-4rem)] w-full max-w-5xl mx-auto flex-col bg-[#020817] text-slate-100 antialiased overflow-hidden">
      
      {/* 🧵 CHAT AREA COMPONENT WINDOW */}
      {/* 🎯 FIX 2: Added 'h-full flex flex-col justify-between' layout boundaries to isolate scroll boxes */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6 custom-chat-scrollbar min-h-0">
        {messages.length === 0 ? (
          
          /* 👋 WELCOME SCREEN */
          <div className="h-full flex flex-col justify-center items-center max-w-2xl mx-auto text-center pt-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="h-14 w-14 rounded-2xl bg-gradient-to-br from-cyan-500/20 to-blue-600/20 border border-cyan-500/30 flex items-center justify-center shadow-[0_0_30px_rgba(34,211,238,0.1)] mb-6">
              <Sparkles size={26} className="text-cyan-400" />
            </div>

            <h1 className="text-2xl md:text-3xl font-black tracking-tight text-white">
              Welcome to <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-blue-400 to-indigo-400">AgentPulse Copilot</span>
            </h1>
            
            <p className="mt-4 text-sm md:text-base text-slate-400 leading-relaxed font-normal">
              I'm your AI assistant for the AgentPulse platform. I can help you create AI agents, understand Knowledge (RAG), configure AI providers, integrate APIs and MCP, explain Runtime Guard, workspaces, and troubleshooting.
            </p>
            
            <div className="mt-5 flex items-center space-x-2 text-xs font-mono text-slate-500 bg-slate-900/40 px-3 py-1.5 rounded-full border border-slate-800/60">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-500 animate-pulse"></span>
              <span>All answers derived directly from official platform documentation</span>
            </div>

            {/* 💡 TILES */}
            <div className="mt-12 w-full grid grid-cols-1 md:grid-cols-2 gap-3 text-left">
              {quickSuggestions.map((suggestion, index) => {
                const SuggestionIcon = suggestion.icon;
                return (
                  <button
                    key={index}
                    onClick={() => handleQuerySubmission(suggestion.text)}
                    className="group flex items-start gap-4 bg-slate-950/40 hover:bg-cyan-950/10 border border-slate-900 hover:border-cyan-500/30 p-4 rounded-xl text-xs md:text-sm transition-all duration-200 shadow-sm"
                  >
                    <div className="mt-0.5 text-slate-500 group-hover:text-cyan-400 transition-colors">
                      <SuggestionIcon size={16} />
                    </div>
                    <div className="flex-1 font-medium text-slate-300 group-hover:text-white transition-colors flex items-center justify-between">
                      <span>{suggestion.text}</span>
                      <ArrowRight size={14} className="opacity-0 group-hover:opacity-100 text-cyan-400 transform translate-x-[-4px] group-hover:translate-x-0 transition-all" />
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        ) : (
          
          /* 💬 IMMERSIVE INTERACTIVE CHAT FLOW BUBBLES */
          <div className="space-y-6 max-w-3xl mx-auto w-full">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex w-full ${msg.type === "user" ? "justify-end" : "justify-start"} animate-in fade-in duration-300`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-3.5 text-sm md:text-base leading-relaxed ${
                    msg.type === "user"
                      ? "bg-gradient-to-br from-cyan-600 to-blue-600 text-white font-normal shadow-md"
                      : "bg-[#090f1a] text-slate-200 border border-slate-800/80 font-normal"
                  }`}
                >
                  <p className="whitespace-pre-wrap selection:bg-cyan-500/30">{msg.text}</p>
                </div>
              </div>
            ))}

            {/* ⚡ THINKING LOADER */}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-[#090f1a] text-slate-400 border border-slate-800 max-w-[85%] px-5 py-4 rounded-2xl text-xs md:text-sm flex items-center space-x-3 shadow-sm">
                  <div className="flex space-x-1.5 items-center py-1">
                    <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                    <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                    <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce"></div>
                  </div>
                  <span className="font-mono text-xs tracking-wide text-slate-500">Searching documentation & thinking...</span>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>
        )}
      </div>

      {/* 📥 USER TEXT PROMPT INTERFACE LAYER */}
      <div className="p-4 bg-[#020817] border-t border-slate-900 mt-auto">
        <form onSubmit={handleFormSubmit} className="max-w-3xl mx-auto w-full flex flex-col space-y-2">
          <div className="flex items-center space-x-3 relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={isLoading ? "AgentPulse Copilot is processing..." : "Ask about AgentPulse, API integrations, or monitoring limits..."}
              className="w-full bg-[#090f1a] border border-slate-800 focus:border-cyan-500/40 rounded-xl pl-4 pr-14 py-3.5 text-sm font-sans text-slate-100 focus:outline-none placeholder-slate-600 transition-all shadow-inner"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 p-2.5 rounded-lg bg-cyan-500 hover:bg-cyan-600 text-slate-950 disabled:bg-slate-900 disabled:text-slate-700 transition-colors flex items-center justify-center shadow-md"
            >
              <Send size={16} />
            </button>
          </div>
          
          <div className="text-center text-[10px] font-mono text-slate-600 tracking-wider pt-1.5 uppercase select-none">
            🔒 Multi-Tenant Context Shielding Active • Powered by an AgentPulse Agent
          </div>
        </form>
      </div>

      <style jsx global>{`
        .custom-chat-scrollbar::-webkit-scrollbar {
          width: 5px;
        }
        .custom-chat-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-chat-scrollbar::-webkit-scrollbar-thumb {
          background: #0f172a;
          border-radius: 99px;
        }
        .custom-chat-scrollbar::-webkit-scrollbar-thumb:hover {
          background: #06b6d4;
        }
      `}</style>
    </div>
  );
}