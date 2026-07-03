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
import { login, forgotPassword, loginWithSSO } from "@/components/api";
import { toast } from "sonner";
import { signInWithPopup } from "firebase/auth";
import { auth, googleProvider, githubProvider, microsoftProvider } from "@/components/firebase";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [ssoLoading, setSsoLoading] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [forgotLoading, setForgotLoading] = useState(false);
  const [forgotEmail, setForgotEmail] = useState("");
  const [showForgotPassword, setShowForgotPassword] = useState(false);

  // Reusable navigation router redirect mechanism
  function handleNavigationRedirect(workspaces: any) {
    setSuccess(true);
    setTimeout(() => {
      if (workspaces && workspaces.length > 1) {
        window.location.href = "/select-workspace";
      } else {
        window.location.href = "/dashboard";
      }
    }, 1000);
  }

  // Classic Password Login Submission Handler
  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    try {
      setLoading(true);
      const response = await login(email, password);

      if (response?.access_token) {
        toast.success(response?.message || "Authentication successful");
        handleNavigationRedirect(response.workspaces);
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

  // Multi-Provider OAuth SSO Handshake Processor
  async function handleSocialSSO(providerName: "google" | "github" | "microsoft") {
    try {
      setSsoLoading(providerName);
      let activeProvider;

      if (providerName === "google") activeProvider = googleProvider;
      else if (providerName === "github") activeProvider = githubProvider;
      else activeProvider = microsoftProvider;
      
      // Fire client popup login interface hook
      const result = await signInWithPopup(auth, activeProvider);
      const user = result.user;

      if (!user.email) {
        throw new Error(`Could not read a verified email profile context from your ${providerName} account.`);
      }

      // Inject provider details into your backend /auth/sso/callback route
      const response = await loginWithSSO({
        email: user.email,
        name: user.displayName || user.email.split("@")[0],
        provider: providerName,
        provider_id: user.uid
      });

      if (response?.access_token) {
        toast.success(response?.message || `Successfully logged in via ${providerName}`);
        handleNavigationRedirect(response.workspaces);
      }
    } catch (err: any) {
      console.error(err);
      toast.error(err?.message || `Authentication with ${providerName} aborted or failed.`);
    } finally {
      setSsoLoading(null);
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

      {/* MAIN CONTAINER */}
      <div className="relative z-10 w-full max-w-xl rounded-[40px] border border-cyan-500/20 hover:border-cyan-400/30 transition-all duration-500 bg-[linear-gradient(180deg,#071120_0%,#091525_100%)] p-10 overflow-hidden animate-[fadeIn_.5s_ease]">
        <div className="absolute top-0 right-0 h-72 w-72 rounded-full bg-cyan-500/10 blur-3xl" />

        <div className="relative z-10">
          {/* LOGO TITLE HEADER */}
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

          <div className="mt-10">
            <h2 className="text-4xl font-black">Mission Control Login</h2>
            <p className="mt-3 text-slate-400 text-lg">Authenticate to access runtime observability systems.</p>

            <div className="mt-6 inline-flex items-center gap-3 rounded-full border border-cyan-500/20 bg-cyan-500/10 px-5 py-3">
              <div className="h-2 w-2 rounded-full bg-green-400 animate-pulse" />
              <span className="text-sm font-bold text-cyan-300">SECURE ACCESS</span>
            </div>
          </div>

          {/* ⚡ THIRD PARTY SOCIAL IDENTITY OAUTH PROVIDERS (3-COLUMN GRID) */}
          <div className="mt-8 grid grid-cols-3 gap-3">
            {/* Google */}
            <button
              type="button"
              disabled={loading || ssoLoading !== null}
              onClick={() => handleSocialSSO("google")}
              className="flex items-center justify-center gap-2 rounded-2xl border border-cyan-500/20 bg-[#0f172a] hover:bg-[#1e293b] py-4 text-white text-sm font-bold transition-all disabled:opacity-50"
            >
              {ssoLoading === "google" ? (
                <div className="h-4 w-4 rounded-full border-2 border-cyan-400/20 border-t-cyan-400 animate-spin" />
              ) : (
                <svg className="h-4 w-4 fill-current" viewBox="0 0 24 24">
                  <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                  <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                  <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" fill="#FBBC05"/>
                  <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.53 12-4.53z" fill="#EA4335"/>
                </svg>
              )}
              Google
            </button>

            {/* GitHub */}
            <button
              type="button"
              disabled={loading || ssoLoading !== null}
              onClick={() => handleSocialSSO("github")}
              className="flex items-center justify-center gap-2 rounded-2xl border border-cyan-500/20 bg-[#0f172a] hover:bg-[#1e293b] py-4 text-white text-sm font-bold transition-all disabled:opacity-50"
            >
              {ssoLoading === "github" ? (
                <div className="h-4 w-4 rounded-full border-2 border-purple-400/20 border-t-purple-400 animate-spin" />
              ) : (
                <svg className="h-4 w-4 fill-current" viewBox="0 0 24 24">
                  <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.166 6.839 9.489.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.603-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.464-1.11-1.464-.908-.62.069-.061.069-.061 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.831.092-.646.35-1.086.636-1.336-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.579.688.481C19.137 20.162 22 16.418 22 12c0-5.523-4.477-10-10-10z" />
                </svg>
              )}
              GitHub
            </button>

            {/* Microsoft */}
            <button
              type="button"
              disabled={loading || ssoLoading !== null}
              onClick={() => handleSocialSSO("microsoft")}
              className="flex items-center justify-center gap-2 rounded-2xl border border-cyan-500/20 bg-[#0f172a] hover:bg-[#1e293b] py-4 text-white text-sm font-bold transition-all disabled:opacity-50"
            >
              {ssoLoading === "microsoft" ? (
                <div className="h-4 w-4 rounded-full border-2 border-blue-400/20 border-t-blue-400 animate-spin" />
              ) : (
                <svg className="h-4 w-4" viewBox="0 0 23 23">
                  <path fill="#f35325" d="M0 0h11v11H0z"/>
                  <path fill="#81bc06" d="M12 0h11v11H12z"/>
                  <path fill="#05a6f0" d="M0 12h11v11H0z"/>
                  <path fill="#ffba08" d="M12 12h11v11H12z"/>
                </svg>
              )}
              Microsoft
            </button>
          </div>

          {/* DUST SEPARATOR DECORATION */}
          <div className="relative my-8">
            <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-cyan-500/10" /></div>
            <div className="relative flex justify-center text-xs uppercase"><span className="bg-[#081322] px-4 text-slate-500 font-bold tracking-widest">OR CONTINUE WITH EMAIL</span></div>
          </div>

          {/* CREDENTIALS SUBMISSION INPUT BLOCK */}
          <form onSubmit={handleLogin} className="space-y-6">
            <div>
              <label className="text-sm text-slate-400 mb-3 block">Email Address</label>
              <div className="relative">
                <Mail className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-500" size={20} />
                <input
                  type="email"
                  required
                  disabled={loading || ssoLoading !== null}
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
                  disabled={loading || ssoLoading !== null}
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
              disabled={loading || ssoLoading !== null}
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

          {/* FORGOT PASSWORD SCREEN MODAL LAYER */}
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