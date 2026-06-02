"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Activity,
  Lock,
  Mail,
  ArrowRight,
  ShieldCheck,
} from "lucide-react";
import { login, forgotPassword } from "@/components/api";
import { toast } from "sonner";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [forgotLoading, setForgotLoading] = useState(false);
  const [forgotEmail, setForgotEmail] = useState("");
  const [showForgotPassword, setShowForgotPassword] = useState(false);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    try {
      setLoading(true);

      // This triggers our optimized api.ts login handler
      const response = await login(email, password);

      if (response?.access_token) {
        setSuccess(true);
        toast.success(response?.message || "Authentication successful");

        setTimeout(() => {
          if (response.workspaces && response.workspaces.length > 1) {
            window.location.href = "/select-workspace";
          } else {
            window.location.href = "/dashboard";
          }
        }, 1000);
      } else {
        toast.error("Invalid login response.");
      }
    } catch (err: any) {
      console.error(err);
      toast.error(err?.message || "Login failed.");
    } finally {
      setLoading(false);
    }
  }

  async function handleForgotPassword() {
    if (!forgotEmail) {
      toast.error("Please enter your email");
      return;
    }
    try {
      setForgotLoading(true);
      const response = await forgotPassword(forgotEmail);
      toast.success(response?.message || "Reset link sent");
      setShowForgotPassword(false);
    } catch (err: any) {
      toast.error(err?.message || "Failed to send reset email");
    } finally {
      setForgotLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-[#020817] overflow-hidden relative flex items-center justify-center px-6">
      {/* BACKGROUND EFFECTS */}
      <div className="absolute top-0 left-0 h-[500px] w-[500px] rounded-full bg-cyan-500/10 blur-3xl" />
      <div className="absolute bottom-0 right-0 h-[500px] w-[500px] rounded-full bg-purple-500/10 blur-3xl" />

      {/* LOGIN CARD */}
      <div className="relative z-10 w-full max-w-xl rounded-[40px] border border-cyan-500/20 hover:border-cyan-400/30 transition-all duration-500 bg-[linear-gradient(180deg,#071120_0%,#091525_100%)] p-10 overflow-hidden animate-[fadeIn_.5s_ease]">
        <div className="absolute top-0 right-0 h-72 w-72 rounded-full bg-cyan-500/10 blur-3xl" />

        <div className="relative z-10">
          {/* BRAND LOGO */}
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

          {/* CARD HEADLINE */}
          <div className="mt-10">
            <h2 className="text-4xl font-black">Mission Control Login</h2>
            <p className="mt-3 text-slate-400 text-lg">Authenticate to access runtime observability systems.</p>

            <div className="mt-6 inline-flex items-center gap-3 rounded-full border border-cyan-500/20 bg-cyan-500/10 px-5 py-3">
              <div className="h-2 w-2 rounded-full bg-green-400 animate-pulse" />
              <span className="text-sm font-bold text-cyan-300">SECURE ACCESS</span>
            </div>

            <div className="mt-6 grid grid-cols-2 gap-4">
              <div className="rounded-2xl border border-green-500/20 bg-green-500/10 p-4">
                <p className="text-xs text-green-200/70">API STATUS</p>
                <h3 className="mt-2 text-lg font-black text-green-300">ONLINE</h3>
              </div>
              <div className="rounded-2xl border border-cyan-500/20 bg-cyan-500/10 p-4">
                <p className="text-xs text-cyan-200/70">SECURITY</p>
                <h3 className="mt-2 text-lg font-black text-cyan-300">ACTIVE</h3>
              </div>
            </div>
          </div>

          {/* CREDENTIALS FORM */}
          <form onSubmit={handleLogin} className="mt-8 space-y-6">
            <div>
              <label className="text-sm text-slate-400 mb-3 block">Email Address</label>
              <div className="relative">
                <Mail className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-500" size={20} />
                <input
                  type="email"
                  required
                  disabled={loading}
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
                  disabled={loading}
                  autoComplete="current-password"
                  placeholder="••••••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full rounded-3xl border border-cyan-500/20 bg-[#0f172a] px-14 py-5 text-white text-lg outline-none transition-all focus:border-cyan-400 focus:ring-4 focus:ring-cyan-500/10 placeholder:text-slate-500"
                />
              </div>
            </div>

            <div className="flex justify-end -mt-2">
              <button
                type="button"
                onClick={() => setShowForgotPassword(true)}
                className="text-sm text-cyan-300 hover:text-cyan-200 font-semibold transition-all"
              >
                Forgot Password?
              </button>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-3xl bg-cyan-500 hover:bg-cyan-400 transition-all py-5 text-black font-black text-lg flex items-center justify-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="flex items-center gap-3">
                  <div className="h-5 w-5 rounded-full border-2 border-black/20 border-t-black animate-spin" />
                  Authenticating...
                </div>
              ) : success ? (
                <div className="flex items-center gap-3">
                  <ShieldCheck size={22} />
                  Access Granted
                </div>
              ) : (
                <>
                  <ShieldCheck size={22} />
                  Access Mission Control
                  <ArrowRight size={22} />
                </>
              )}
            </button>
          </form>

          {/* FORGOT PASSWORD MODAL BACKGROUND SHADOW */}
          {showForgotPassword && (
            <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 px-6">
              <div className="w-full max-w-md rounded-3xl border border-cyan-500/20 bg-[#091525] p-8">
                <h3 className="text-2xl font-black text-white">Reset Password</h3>
                <p className="mt-2 text-slate-400">Enter your email address to receive a reset link.</p>

                <div className="mt-6">
                  <input
                    type="email"
                    placeholder="you@example.com"
                    value={forgotEmail}
                    onChange={(e) => setForgotEmail(e.target.value)}
                    className="w-full rounded-2xl border border-cyan-500/20 bg-[#0f172a] px-5 py-4 text-white outline-none focus:border-cyan-400"
                  />
                </div>

                <div className="mt-6 flex gap-3">
                  <button
                    type="button"
                    onClick={() => setShowForgotPassword(false)}
                    className="flex-1 rounded-2xl border border-slate-700 py-4 text-white font-bold"
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    disabled={forgotLoading}
                    onClick={handleForgotPassword}
                    className="flex-1 rounded-2xl bg-cyan-500 hover:bg-cyan-400 py-4 text-black font-black transition-all disabled:opacity-50"
                  >
                    {forgotLoading ? "Sending..." : "Send Link"}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* REDIRECT FOOTER LINKS */}
          <div className="mt-8 text-center text-slate-400">
            Don&apos;t have an account?{" "}
            <Link href="/signup" className="text-cyan-300 hover:text-cyan-200 font-bold">
              Create Workspace
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
