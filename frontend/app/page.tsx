"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import axios from "axios"; // Using standard axios directly

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
    // Calling your backend token rotation route directly
    axios.post(
      "https://agentpulse-backend.onrender.com/auth/refresh",
      {},
      { withCredentials: true } // Crucial: Tells the browser to safely pass your secure cookies
    )
    .then((response: any) => {
      if (response.data && response.data.access_token) {
        // Save the fresh short-lived token to memory
        localStorage.setItem("access_token", response.data.access_token);
        // Redirect straight into your dashboard layout cockpit
        router.push("/dashboard");
      } else {
        setIsLoading(false);
      }
    })
    .catch(() => {
      // If no active session cookie exists, stop loading and show the landing screen text smoothly
      setIsLoading(false);
    });
  }, [router]);

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
      <MatrixBg />
      <Navbar />
      <Hero />
      <Problem />
      <Features />
      <Docs />
      <Showcase />
      <Pricing />
      <Footer />
    </div>
  );
}
