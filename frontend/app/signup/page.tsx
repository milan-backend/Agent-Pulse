"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Activity,
  Mail,
  Lock,
  User,
  ArrowRight,
  ShieldCheck,
} from "lucide-react";
import { signup } from "@/components/api";
import { toast } from "sonner";

export default function SignupPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [emailSent, setEmailSent] = useState(false);

  async function handleSignup(e: React.FormEvent) {
    e.preventDefault();
    try {
      setLoading(true);
      const response = await signup(name, email, password);
      setEmailSent(true);
      toast.success(response?.message || "Verification email sent");
    } catch (err: any) {
      console.error(err);
      toast.error(err?.message || "Signup failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-[#020817] overflow-hidden relative flex items-center justify-center px-6">
      {/* BACKGROUND EFFECTS */}
      <div className="absolute top-0 left-0 h-[500px] w-[500px] rounded-full bg-cyan-500/10 blur-3xl" />
      <div className="absolute bottom-0 right-0 h-[500px] w-[500px] rounded-full bg-purple-500/10 blur-3xl" />

      {/* CARD */}
      <div className="relative z-10 w-full max-w-xl rounded-[40px] border border-cyan-500/20 bg-[linear-gradient(180deg,#071120_0%,#091525_100%)] p-10 overflow-hidden animate-[fadeIn_.5s_ease]">
        <div className="absolute top-0 right-0 h-72 w-72 rounded-full bg-cyan-500/10 blur-3xl" />

        <div className="relative z-10">
          {/* LOGO */}
          <div className="flex items-center gap-5">
            <div className="h-20 w-20 rounded-3xl border border-cyan-500/20 bg-cyan-500/10 flex items-center justify-center">
              <Activity className="text-cyan-300" size={38} />
            </div>
            <div>
              <h1 className="text-5xl font-black leading-none">
                <span className="text-cyan-400">Agent</span>
                <span className="text-white">Pulse</span>
              </h1>
              <p className="mt-2 text-slate-400">AI Runtime Observability</p>
            </div>
          </div>

          {/* TITLE HEADER */}
          <div className="mt-10">
            <h2 className="text-4xl font-black">Create Workspace</h2>
            <p className="mt-3 text-slate-400 text-lg">Launch your autonomous AI runtime observability platform.</p>

            <div className="mt-6 inline-flex items-center gap-3 rounded-full border border-cyan-500/20 bg-cyan-500/10 px-5 py-3">
              <div className="h-2 w-2 rounded-full bg-green-400 animate-pulse" />
              <span className="text-sm font-bold text-cyan-300">RUNTIME READY</span>
            </div>
          </div>

          {/* SUCCESS MESSAGE FEED OR INPUT FORM CONTROLLERS */}
          {emailSent ? (
            <div className="mt-10 rounded-3xl border border-green-500/20 bg-green-500/10 p-8 text-center">
              <div className="mx-auto h-20 w-20 rounded-full bg-green-500/20 flex items-center justify-center">
                <ShieldCheck className="text-green-300" size={40} />
              </div>
              <h3 className="mt-6 text-3xl font-black text-white">Verification Email Sent</h3>
              <p className="mt-4 text-slate-300 text-lg leading-relaxed">We sent a verification link to:</p>
              <p className="mt-3 text-cyan-300 font-bold text-lg break-all">{email}</p>
              <p className="mt-6 text-slate-400">Please verify your email before accessing Mission Control.</p>

              <Link href="/login" className="inline-flex items-center gap-3 mt-8 rounded-2xl bg-cyan-500 hover:bg-cyan-400 transition-all px-8 py-4 text-black font-black">
                Continue to Login
                <ArrowRight size={20} />
              </Link>
            </div>
          ) : (
            <form onSubmit={handleSignup} className="mt-8 space-y-6">
              <div>
                <label className="text-sm text-slate-400 mb-3 block">Workspace Owner</label>
                <div className="relative">
                  <User className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-500" size={20} />
                  <input
                    type="text"
                    required
                    autoComplete="name"
                    placeholder="Agent Operator"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full rounded-3xl border border-cyan-500/20 bg-[#0f172a] px-14 py-5 text-white text-lg outline-none transition-all focus:border-cyan-400 focus:ring-4 focus:ring-cyan-500/10 placeholder:text-slate-500"
                  />
                </div>
              </div>

              <div>
                <label className="text-sm text-slate-400 mb-3 block">Email Address</label>
                <div className="relative">
                  <Mail className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-500" size={20} />
                  <input
                    type="email"
                    required
                    autoComplete="email"
                    placeholder="admin@agentpulse.ai"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full rounded-3xl border border-cyan-500/20 bg-[#0f172a] px-14 py-5 text-white text-lg outline-none transition-all focus:border-cyan-400 focus:ring-4 focus:ring-cyan-500/10 placeholder:text-slate-500"
                  />
                </div>
              </div>

              <div>
                <label className="text-sm text-slate-400 mb-3 block">Password</label>
                <div className="relative">
                  <Lock className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-500" size={20} />
                  <input
                    type="password"
                    required
                    minLength={8}
                    autoComplete="new-password"
                    placeholder="••••••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full rounded-3xl border border-cyan-500/20 bg-[#0f172a] px-14 py-5 text-white text-lg outline-none transition-all focus:border-cyan-400 focus:ring-4 focus:ring-cyan-500/10 placeholder:text-slate-500"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full rounded-3xl bg-cyan-500 hover:bg-cyan-400 transition-all py-5 text-black font-black text-lg flex items-center justify-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <div className="flex items-center gap-3">
                    <div className="h-5 w-5 rounded-full border-2 border-black/20 border-t-black animate-spin" />
                    Creating Workspace...
                  </div>
                ) : (
                  <>
                    <ShieldCheck size={22} />
                    Launch Workspace
                    <ArrowRight size={22} />
                  </>
                )}
              </button>
            </form>
          )}

          {/* LINKING REDIRECT CONNECTIONS */}
          <div className="mt-8 text-center text-slate-400">
            Already have an account?{" "}
            <Link href="/login" className="text-cyan-300 hover:text-cyan-200 font-bold">
              Access Mission Control
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
