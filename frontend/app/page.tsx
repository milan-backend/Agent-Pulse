import React from "react";
import AuthBootstrap from "@/components/AuthBootstrap"; // Session guard tracking[cite: 10]
import MatrixBg from "@/components/MatrixBg";           // Animated background canvas layer[cite: 10]
import Navbar from "@/components/Navbar";               // Updated global navbar header
import Hero from "@/components/Hero";                   // Hero + Trust Primitives + Metrics
import Showcase from "@/components/Showcase";           // Screenshot Grid Layout[cite: 10]
import ValueProp from "@/components/ValueProp";         // 8-Card Detailed Capabilities
import Docs from "@/components/Docs";                   // 🎉 RE-ADDED: Developer API Terminal Section
import WhyAgentPulse from "@/components/WhyAgentPulse"; // Build vs Operate Matrix Comparison
import EnterpriseTrust from "@/components/EnterpriseTrust"; // Core reliability policies
import FinalCTA from "@/components/FinalCTA";           // Closing conversion box
import Footer from "@/components/Footer";               // Updated multi-page footer map[cite: 4, 10]
import FloatingCopilot from "@/components/FloatingCopilot";

export const metadata = {
  title: "AgentPulse | AI Agent Observability & Governance Platform",
  description: "Monitor, control, and debug autonomous AI agents in production with trace logging, BYOK security, and budget controls.",
};

export default function AgentPulseLandingPage() {
  return (
    <div className="min-h-screen bg-black text-slate-100 font-sans selection:bg-cyan-500/30 relative overflow-x-hidden">
      {/* Background session token script runner[cite: 10] */}
      <AuthBootstrap />

      {/* Matrix Animation Canvas Layer[cite: 10] */}
      <MatrixBg />

      {/* Global Navigation Header Header[cite: 10] */}
      <Navbar />

      {/* 1. Hero copy block containing platform metrics frameworks layout[cite: 10] */}
      <Hero />

      {/* 2. Interactive Screenshot Simulator Window Section[cite: 10] */}
      <Showcase />

      {/* 3. 8-Card Detailed Value Proposition Operational Primitives Section */}
      <ValueProp />

      {/* 4. Interactive Code Console & Developer Documentation Shell[cite: 2, 10] */}
      <Docs />

      {/* 5. Why AgentPulse Build vs Operate Platform Comparison section */}
      <WhyAgentPulse />

      {/* 6. Enterprise Core Scaling Reliability Infrastructure Grid */}
      <EnterpriseTrust />

      {/* 7. Closing conversion display banner block */}
      <FinalCTA />

      {/* 8. Bottom legal routing network footer layer[cite: 4, 10] */}
      <Footer />

      {/* 🔮 9. INTEGRATED COPILOT LAYER: Accessible right on the landing page */}
      <FloatingCopilot />
    </div>
  );
}