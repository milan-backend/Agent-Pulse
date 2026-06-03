"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import axios from "axios"; // Using axios directly, or replace with your custom internal 'api' client instance

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
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // 1. Fire a silent, secure background check to see if a valid refresh cookie exists
    // Make sure to match your exact backend production URL endpoint configuration
    axios.post(
      "https://agentpulse-backend.onrender.com/auth/refresh", 
      {}, 
      { withCredentials: true } // CRITICAL: This explicitly forces the browser to send the HttpOnly cookie
    )
    .then((response) => {
      // 2. If the server verifies the cookie and returns a 200 OK, update access tokens
      if (response.data && response.data.access_token) {
        // Save the fresh access token back to your local runtime state memory or storage
        localStorage.setItem("access_token", response.data.access_token);
        
        // Push the authenticated user directly into the internal mission control cockpit
        router.push("/dashboard");
      } else {
        setIsLoading(false);
      }
    })
    .catch(() => {
      // 3. If it returns a 401 or errors out, it means no active session exists. 
      // Stop the loading state smoothly and render the pristine landing page view.
      setIsLoading(false);
    });
  }, [router]);

  // If the browser is busy performing the background verification handshake, 
  // show a clean dark loading layer matching your Matrix theme to prevent visual flickering.
  if (isLoading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center text-cyan-400 font-mono">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-sm tracking-widest animate-pulse">SYNCHRONIZING DESKTOP SECURE RUNTIME...</p>
        </div>
      </div>
    );
  }

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
