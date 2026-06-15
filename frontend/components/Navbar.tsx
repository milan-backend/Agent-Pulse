"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Menu, X, ArrowRight } from "lucide-react";

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 border-b border-slate-900 bg-black/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
        
        {/* LOGO LINK */}
        <Link href="/" className="flex items-center gap-1.5 text-xl font-black">
          <span className="text-white">Agent</span>
          <span className="from-cyan-400 to-purple-500 bg-gradient-to-r bg-clip-text text-transparent">
            Pulse
          </span>
        </Link>

        {/* DESKTOP NAVIGATION MENU ITEMS */}
        <div className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-400">
          <Link href="/#features" className="hover:text-white transition-colors">
            Product
          </Link>
          <Link href="/#features" className="hover:text-white transition-colors">
            Features
          </Link>
          <Link href="/pricing" className="text-slate-300 hover:text-cyan-400 font-bold transition-colors">
            Pricing
          </Link>
          <Link href="/#docs" className="hover:text-white transition-colors">
            Documentation
          </Link>
        </div>

        {/* DESKTOP CALL TO ACTION BUTTONS */}
        <div className="hidden md:flex items-center gap-4">
          <Link href="/login" className="text-sm font-medium text-slate-400 hover:text-white transition-colors">
            Sign In
          </Link>
          <Link
            href="/signup"
            className="px-5 py-2.5 bg-cyan-400 text-black font-black text-xs uppercase tracking-wider font-mono rounded-xl hover:shadow-[0_0_25px_rgba(34,211,238,0.3)] transition-all flex items-center gap-1.5"
          >
            Get Started <ArrowRight size={14} />
          </Link>
        </div>

        {/* MOBILE HAMBURGER BUTTON TOGGLE */}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="md:hidden p-2 text-slate-400 hover:text-white transition-colors"
        >
          {isOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* MOBILE EXPANDABLE MENU OVERLAY */}
      {isOpen && (
        <div className="md:hidden bg-black border-b border-slate-900 px-6 py-6 space-y-4 animate-in fade-in slide-in-from-top-5 duration-200">
          <div className="flex flex-col gap-4 text-base font-medium text-slate-400">
            <Link onClick={() => setIsOpen(false)} href="/#features" className="hover:text-white transition-colors">
              Product
            </Link>
            <Link onClick={() => setIsOpen(false)} href="/#features" className="hover:text-white transition-colors">
              Features
            </Link>
            <Link onClick={() => setIsOpen(false)} href="/pricing" className="text-cyan-400 font-bold transition-colors">
              Pricing
            </Link>
            <Link onClick={() => setIsOpen(false)} href="/#docs" className="hover:text-white transition-colors">
              Documentation
            </Link>
            <hr className="border-slate-900 my-2" />
            <Link onClick={() => setIsOpen(false)} href="/login" className="hover:text-white transition-colors">
              Sign In
            </Link>
            <Link
              onClick={() => setIsOpen(false)}
              href="/signup"
              className="w-full py-3 bg-cyan-400 text-black font-black text-center text-xs uppercase tracking-wider font-mono rounded-xl block"
            >
              Get Started
            </Link>
          </div>
        </div>
      )}
    </nav>
  );
}