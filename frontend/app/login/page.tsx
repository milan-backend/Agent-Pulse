// frontend/app/login/page.tsx

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

import {
  login,
} from "@/components/api";

export default function LoginPage() {

  const [email, setEmail] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  async function handleLogin(
    e: React.FormEvent
  ) {

    e.preventDefault();

    try {

      setLoading(true);

      setError("");

      const response =
        await login(
          email,
          password
        );

      if (
        response?.access_token
      ) {

        localStorage.setItem(
          "token",
          response.access_token
        );

        localStorage.setItem(
          "workspaces",
          JSON.stringify(
            response.workspaces || []
          )
        );

        if (
          response.workspaces && response.workspaces.length > 1
        ){
          localStorage.setItem(
            "workspaces",
            JSON.stringify(
              response.workspaces
            )
          );
          window.location.href = "/select-workspace";

        } else {
          localStorage.setItem(
            "workspace_id",
            response.workspace_id
          );

        window.location.href =
          "/dashboard";
        }

      } else {

        setError(
          "Invalid login response."
        );
      }

    } catch (err: any) {

      console.error(err);

      setError(
        err?.message ||
          "Login failed."
      );

    } finally {

      setLoading(false);
    }
  }

  return (

    <div
      className="
        min-h-screen
        bg-[#020817]
        overflow-hidden
        relative
        flex
        items-center
        justify-center
        px-6
      "
    >
      {/* BACKGROUND */}

      <div
        className="
          absolute
          top-0
          left-0
          h-[500px]
          w-[500px]
          rounded-full
          bg-cyan-500/10
          blur-3xl
        "
      />

      <div
        className="
          absolute
          bottom-0
          right-0
          h-[500px]
          w-[500px]
          rounded-full
          bg-purple-500/10
          blur-3xl
        "
      />

      {/* CARD */}

      <div
        className="
          relative
          z-10
          w-full
          max-w-xl
          rounded-[40px]
          border
          border-cyan-500/20
          bg-[linear-gradient(180deg,#071120_0%,#091525_100%)]
          p-10
          overflow-hidden
        "
      >
        {/* INNER GLOW */}

        <div
          className="
            absolute
            top-0
            right-0
            h-72
            w-72
            rounded-full
            bg-cyan-500/10
            blur-3xl
          "
        />

        {/* HEADER */}

        <div className="relative z-10">
          {/* LOGO */}

          <div
            className="
              flex
              items-center
              gap-5
            "
          >
            <div
              className="
                h-20
                w-20
                rounded-3xl
                border
                border-cyan-500/20
                bg-cyan-500/10
                flex
                items-center
                justify-center
              "
            >
              <Activity
                className="
                  text-cyan-300
                "
                size={38}
              />
            </div>

            <div>
              <h1
                className="
                  text-5xl
                  font-black
                  leading-none
                "
              >
                <span className="text-cyan-400">
                  Agent
                </span>

                <span className="text-white">
                  Pulse
                </span>
              </h1>

              <p
                className="
                  mt-2
                  text-slate-400
                "
              >
                AI Runtime Observability
              </p>
            </div>
          </div>

          {/* TITLE */}

          <div className="mt-10">
            <h2
              className="
                text-4xl
                font-black
              "
            >
              Mission Control Login
            </h2>

            <p
              className="
                mt-3
                text-slate-400
                text-lg
              "
            >
              Authenticate to access runtime
              observability systems.
            </p>
          </div>

          {/* ERROR */}

          {error && (

            <div
              className="
                mt-6
                rounded-2xl
                border
                border-red-500/20
                bg-red-500/10
                px-5
                py-4
                text-red-300
                font-semibold
              "
            >
              {error}
            </div>
          )}

          {/* FORM */}

          <form
            onSubmit={
              handleLogin
            }
            className="
              mt-8
              space-y-6
            "
          >
            {/* EMAIL */}

            <div>
              <label
                className="
                  text-sm
                  text-slate-400
                  mb-3
                  block
                "
              >
                Email Address
              </label>

              <div className="relative">
                <Mail
                  className="
                    absolute
                    left-5
                    top-1/2
                    -translate-y-1/2
                    text-slate-500
                  "
                  size={20}
                />

                <input
                  type="email"
                  required
                  placeholder="admin@agentpulse.ai"
                  value={email}
                  onChange={(e) =>
                    setEmail(
                      e.target.value
                    )
                  }
                  className="
                    w-full
                    rounded-3xl
                    border
                    border-cyan-500/20
                    bg-[#0f172a]
                    px-14
                    py-5
                    text-white
                    text-lg
                    outline-none
                    transition-all
                    focus:border-cyan-400
                    focus:ring-4
                    focus:ring-cyan-500/10
                    placeholder:text-slate-500
                  "
                />
              </div>
            </div>

            {/* PASSWORD */}

            <div>
              <label
                className="
                  text-sm
                  text-slate-400
                  mb-3
                  block
                "
              >
                Password
              </label>

              <div className="relative">
                <Lock
                  className="
                    absolute
                    left-5
                    top-1/2
                    -translate-y-1/2
                    text-slate-500
                  "
                  size={20}
                />

                <input
                  type="password"
                  required
                  placeholder="••••••••••••"
                  value={password}
                  onChange={(e) =>
                    setPassword(
                      e.target.value
                    )
                  }
                  className="
                    w-full
                    rounded-3xl
                    border
                    border-cyan-500/20
                    bg-[#0f172a]
                    px-14
                    py-5
                    text-white
                    text-lg
                    outline-none
                    transition-all
                    focus:border-cyan-400
                    focus:ring-4
                    focus:ring-cyan-500/10
                    placeholder:text-slate-500
                  "
                />
              </div>
            </div>

            {/* BUTTON */}

            <button
              type="submit"
              disabled={loading}
              className="
                w-full
                rounded-3xl
                bg-cyan-500
                hover:bg-cyan-400
                transition-all
                py-5
                text-black
                font-black
                text-lg
                flex
                items-center
                justify-center
                gap-3
              "
            >
              {loading ? (
                "Authenticating..."
              ) : (
                <>
                  <ShieldCheck
                    size={22}
                  />

                  Access Mission Control

                  <ArrowRight
                    size={22}
                  />
                </>
              )}
            </button>
          </form>

          {/* FOOTER */}

          <div
            className="
              mt-8
              text-center
              text-slate-400
            "
          >
            Don&apos;t have an account?
            {" "}

            <Link
              href="/signup"
              className="
                text-cyan-300
                hover:text-cyan-200
                font-bold
              "
            >
              Create Workspace
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}