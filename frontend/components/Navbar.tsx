"use client";

import React, { useState } from "react";
import { Menu, X } from "lucide-react";
import Link from "next/link";

export default function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <nav className="sticky top-0 z-50 w-full border-b border-slate-800/60 bg-black/70 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
        {/* AgentPulse Logo */}
        <div className="flex items-center gap-2">
          <Link href="/" className="text-2xl font-black tracking-tight select-none">
            <span className="text-white font-extrabold text-3xl">Agent</span>
            <span className="bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-500 bg-clip-text text-transparent font-black text-3xl drop-shadow-[0_0_15px_rgba(34,211,238,0.4)]">
              Pulse
            </span>
          </Link>
        </div>

        {/* Global Nav Links */}
        <div className="hidden md:flex items-center gap-8 text-sm font-semibold text-slate-300">
          <a href="#product" className="hover:text-cyan-400 transition-colors">Product</a>
          <a href="#features" className="hover:text-cyan-400 transition-colors">Features</a>
          <a href="#pricing" className="hover:text-cyan-400 transition-colors">Pricing</a>
          <a href="#docs" className="hover:text-cyan-400 transition-colors">Documentation</a>
        </div>

        {/* Desktop Navigation Links */}
        <div className="hidden md:flex items-center gap-4">
          <Link
            href="/login"
            className="text-sm font-bold text-slate-300 hover:text-white px-4 py-2 transition-colors"
          >
            Login
          </Link>

          <Link
            href="/signup"
            className="text-sm font-bold bg-cyan-400 text-black px-5 py-2.5 rounded-xl hover:scale-[1.02] hover:shadow-[0_0_25px_rgba(34,211,238,0.5)] transition-all"
          >
            Start Free
          </Link>
        </div>

        {/* Mobile Toggle */}
        <button
          className="md:hidden text-slate-300 hover:text-white"
          onClick={() => setMobileMenuOpen(true)}
        >
          <Menu size={24} />
        </button>
      </div>

      {/* Mobile Menu Overlay */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-50 bg-black p-6 flex flex-col justify-between md:hidden">
          <div>
            <div className="flex items-center justify-between pb-8 border-b border-slate-800">
              <span className="text-2xl font-black">
                <span className="text-white">Agent</span>
                <span className="from-cyan-400 to-purple-500 bg-gradient-to-r bg-clip-text text-transparent">
                  Pulse
                </span>
              </span>

              <button
                className="text-slate-300"
                onClick={() => setMobileMenuOpen(false)}
              >
                <X size={24} />
              </button>
            </div>

            <div className="flex flex-col gap-6 pt-8 text-lg font-bold text-slate-300">
              <a href="#product" onClick={() => setMobileMenuOpen(false)}>
                Product
              </a>

              <a href="#features" onClick={() => setMobileMenuOpen(false)}>
                Features
              </a>

              <a href="#pricing" onClick={() => setMobileMenuOpen(false)}>
                Pricing
              </a>

              <a href="#docs" onClick={() => setMobileMenuOpen(false)}>
                Documentation
              </a>
            </div>
          </div>

          {/* Mobile Navigation Links */}
          <div className="flex flex-col gap-4">
            <Link
              href="/login"
              onClick={() => setMobileMenuOpen(false)}
              className="w-full py-4 text-center font-bold border border-slate-800 rounded-2xl text-slate-300"
            >
              Login
            </Link>

            <Link
              href="/signup"
              onClick={() => setMobileMenuOpen(false)}
              className="w-full py-4 text-center font-bold bg-cyan-400 text-black rounded-2xl"
            >
              Start Free
            </Link>
          </div>
        </div>
      )}
    </nav>
  );
}