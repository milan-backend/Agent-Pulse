import React from "react";
import MatrixBg from "@/components/MatrixBg";
import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import Problem from "@/components/Problem";
import Features from "@/components/Features";
import Docs from "@/components/Docs";
import Showcase from "@/components/Showcase";
import Pricing from "@/components/Pricing";
import Footer from "@/components/Footer";

export default function AgentPulseLandingPage() {
  return (
    <div className="min-h-screen bg-black text-slate-100 font-sans selection:bg-cyan-500/30 relative overflow-x-hidden">
      {/* 1. Matrix Animation & Background Glows Context Layer */}
      <MatrixBg />

      {/* 2. Top Header Navigation Bar */}
      <Navbar />

      {/* 3. Hero Copy with Live Interactive Telemetry Controls Block */}
      <Hero />

      {/* 4. The 8 Core Production Pain Points Grid */}
      <Problem />

      {/* 5. Capability Grid & Detailed Architectural Feature Sections */}
      <Features />

      {/* 6. Developer Documentation Code Snippet Panel */}
      <Docs />

      {/* 7. Interactive App Screenshot View Window */}
      <Showcase />

      {/* 8. Predictable SaaS Pricing Matrix Tiers */}
      <Pricing />

      {/* 9. Bottom Retention Banner & Footer Links Grid */}
      <Footer />
    </div>
  );
}