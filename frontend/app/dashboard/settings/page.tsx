// frontend/app/dashboard/settings/page.tsx

"use client";

import { useState } from "react";

import {
  KeyRound,
  ShieldCheck,
  Power,
  PlayCircle,
  LogOut,
  Settings,
  Cpu,
  AlertTriangle,
} from "lucide-react";

import {
  stopAllAgents,
  resumeAllAgents,
  logout,
} from "@/components/api";

import { toast } from "sonner";

export default function SettingsPage() {

  const [loadingKill, setLoadingKill] =
    useState(false);

  const [loadingResume, setLoadingResume] =
    useState(false);

  async function handleKillAll() {

    if (loadingKill) return;

    try {

      setLoadingKill(true);

      const confirmed =
        window.confirm(
          "Are you sure you want to stop all runtime agents?"
        );

      if (!confirmed) {
        return;
      }

      await stopAllAgents();

      toast.success(
        "All agents stopped successfully"
      );

    } catch (err) {

      console.error(err);

      toast.error(
        err instanceof Error
          ? err.message
          : "Failed to stop agents"
      );

    } finally {

      setLoadingKill(false);
    }
  }

  async function handleResumeAll() {

    if (loadingResume) return;

    try {

      setLoadingResume(true);

      const confirmed =
        window.confirm(
          "Resume all autonomous agents?"
        );

      if (!confirmed) {
        return;
      }

      await resumeAllAgents();

      toast.success(
        "All agents resumed successfully"
      );

    } catch (err) {

      console.error(err);

      toast.error(
        err instanceof Error
          ? err.message
          : "Failed to resume agents"
      );

    } finally {

      setLoadingResume(false);
    }
  }

  return (

    <div className="space-y-8">
      {/* HERO */}

      <div
        className="
          rounded-[32px]
          border
          border-cyan-500/20
          bg-[linear-gradient(180deg,#071120_0%,#091525_100%)]
          p-8
          overflow-hidden
          relative
        "
      >
        {/* GLOW */}

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

        {/* CONTENT */}

        <div className="relative z-10">
          <div
            className="
              flex
              items-center
              gap-4
              mb-6
            "
          >
            <div
              className="
                h-16
                w-16
                rounded-3xl
                border
                border-cyan-500/20
                bg-cyan-500/10
                flex
                items-center
                justify-center
              "
            >
              <Settings
                className="
                  text-cyan-300
                "
                size={32}
              />
            </div>

            <div>
              <h1
                className="
                  text-5xl
                  font-black
                "
              >
                Runtime Settings
              </h1>

              <p
                className="
                  mt-2
                  text-slate-400
                "
              >
                Configure global runtime
                infrastructure controls.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* GRID */}

      <div
        className="
          grid
          grid-cols-1
          xl:grid-cols-2
          gap-8
        "
      >
        {/* AGENT CONTROL */}

        <div
          className="
            rounded-[32px]
            border
            border-red-500/20
            bg-[linear-gradient(180deg,#071120_0%,#140808_100%)]
            p-8
          "
        >
          <div
            className="
              flex
              items-center
              justify-between
              mb-8
            "
          >
            <div>
              <h2
                className="
                  text-3xl
                  font-black
                "
              >
                Runtime Control
              </h2>

              <p
                className="
                  text-slate-400
                  mt-2
                "
              >
                Manage global agent runtime.
              </p>
            </div>

            <div
              className="
                h-14
                w-14
                rounded-2xl
                border
                border-red-500/20
                bg-red-500/10
                flex
                items-center
                justify-center
              "
            >
              <Cpu
                className="
                  text-red-300
                "
                size={28}
              />
            </div>
          </div>

          {/* BUTTONS */}

          <div className="space-y-5">
            {/* STOP */}

            <button
              onClick={
                handleKillAll
              }
              disabled={loadingKill}
              className="
                w-full
                rounded-3xl
                border
                border-red-500/20
                bg-red-500/10
                hover:bg-red-500/20
                transition-all
                p-6
                flex
                items-center
                justify-between
                disabled:opacity-50
                disabled:cursor-not-allowed
              "
            >
              <div className="flex items-center gap-4">
                <Power
                  className="
                    text-red-300
                  "
                  size={28}
                />

                <div className="text-left">
                  <h3
                    className="
                      text-xl
                      font-black
                      text-red-300
                    "
                  >
                    {
                      loadingKill
                        ? "Stopping Runtime..."
                        : "Kill All Agents"
                    }
                  </h3>

                  <p className="text-sm text-slate-400 mt-1">
                    Emergency runtime stop.
                  </p>
                </div>
              </div>

              <AlertTriangle
                className="
                  text-red-300
                "
                size={24}
              />
            </button>

            {/* RESUME */}

            <button
              onClick={
                handleResumeAll
              }
              disabled={loadingResume}
              className="
                w-full
                rounded-3xl
                border
                border-green-500/20
                bg-green-500/10
                hover:bg-green-500/20
                transition-all
                p-6
                flex
                items-center
                justify-between
                disabled:opacity-50
                disabled:cursor-not-allowed
              "
            >
              <div className="flex items-center gap-4">
                <PlayCircle
                  className="
                    text-green-300
                  "
                  size={28}
                />

                <div className="text-left">
                  <h3
                    className="
                      text-xl
                      font-black
                      text-green-300
                    "
                  >
                    {
                      loadingResume
                        ? "Resuming Runtime..."
                        : "Resume Runtime"
                    }
                  </h3>

                  <p className="text-sm text-slate-400 mt-1">
                    Restart all autonomous
                    agents.
                  </p>
                </div>
              </div>

              <ShieldCheck
                className="
                  text-green-300
                "
                size={24}
              />
            </button>
          </div>
        </div>

        {/* SECURITY */}

        <div
          className="
            rounded-[32px]
            border
            border-cyan-500/20
            bg-[linear-gradient(180deg,#071120_0%,#091525_100%)]
            p-8
          "
        >
          <div
            className="
              flex
              items-center
              justify-between
              mb-8
            "
          >
            <div>
              <h2
                className="
                  text-3xl
                  font-black
                "
              >
                Security
              </h2>

              <p
                className="
                  text-slate-400
                  mt-2
                "
              >
                Session and API controls.
              </p>
            </div>

            <div
              className="
                h-14
                w-14
                rounded-2xl
                border
                border-cyan-500/20
                bg-cyan-500/10
                flex
                items-center
                justify-center
              "
            >
              <KeyRound
                className="
                  text-cyan-300
                "
                size={28}
              />
            </div>
          </div>

          {/* CARDS */}

          <div className="space-y-5">
            {/* API */}

            <div
              className="
                rounded-3xl
                border
                border-cyan-500/20
                bg-cyan-500/10
                p-6
              "
            >
              <div
                className="
                  flex
                  items-center
                  justify-between
                "
              >
                <div>
                  <h3
                    className="
                      text-xl
                      font-black
                      text-cyan-300
                    "
                  >
                    API Gateway
                  </h3>

                  <p className="text-sm text-slate-400 mt-2">
                    Runtime authentication
                    active.
                  </p>

                  <div
                    className="
                      mt-4
                      inline-flex
                      items-center
                      gap-2
                      rounded-full
                      border
                      border-green-500/20
                      bg-green-500/10
                      px-3
                      py-1
                      text-xs
                      font-bold
                      text-green-300
                    "
                  >
                    <div
                      className="
                        h-2
                        w-2
                        rounded-full
                        bg-green-400
                        animate-pulse
                      "
                    />

                    ACTIVE
                  </div>
                </div>

                <ShieldCheck
                  className="
                    text-cyan-300
                  "
                  size={28}
                />
              </div>
            </div>

            {/* LOGOUT */}

            <button
              onClick={() => {

                toast.success(
                  "Session ended successfully"
                );

                setTimeout(() => {
                  logout();
                }, 800);
              }}
              className="
                w-full
                rounded-3xl
                border
                border-red-500/20
                bg-red-500/10
                hover:bg-red-500/20
                transition-all
                p-6
                flex
                items-center
                justify-between
              "
            >
              <div className="flex items-center gap-4">
                <LogOut
                  className="
                    text-red-300
                  "
                  size={28}
                />

                <div className="text-left">
                  <h3
                    className="
                      text-xl
                      font-black
                      text-red-300
                    "
                  >
                    Logout Session
                  </h3>

                  <p className="text-sm text-slate-400 mt-1">
                    Terminate current admin
                    session.
                  </p>
                </div>
              </div>

              <LogOut
                className="
                  text-red-300
                "
                size={24}
              />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}