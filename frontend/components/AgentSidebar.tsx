"use client";

import Link from "next/link";

import {
  ArrowLeft,
  Play,
  Square,
  KeyRound,
  Wallet,
  Settings,
} from "lucide-react";

export default function AgentSidebar() {

  return (

    <aside
      className="
        w-[320px]
        min-h-screen
        border-r
        border-cyan-500/10
        bg-[#08111f]
        p-6
      "
    >

      {/* LOGO */}

      <div className="mb-10">

        <h1
          className="
            text-4xl
            font-black
          "
        >

          <span className="text-cyan-400">

            Agent

          </span>

          <span>

            Pulse

          </span>

        </h1>

        <p
          className="
            mt-2
            text-sm
            text-zinc-500
          "
        >

          Runtime Agent Control

        </p>

      </div>

      {/* AGENT CONTROLS */}

      <div className="space-y-4">

        <SidebarItem
          href="/dashboard/agents"
          icon={<ArrowLeft />}
          title="Back To Agents"
        />

        <SidebarButton
          icon={<Play />}
          title="Resume Agent"
        />

        <SidebarButton
          icon={<Square />}
          title="Kill Agent"
          danger
        />

        <SidebarButton
          icon={<Wallet />}
          title="Budget Control"
        />

        <SidebarButton
          icon={<KeyRound />}
          title="Regenerate API Key"
        />

        <SidebarButton
          icon={<Settings />}
          title="Agent Settings"
        />

      </div>

      {/* STATUS */}

      <div
        className="
          mt-10
          rounded-3xl
          border
          border-cyan-500/10
          bg-black/20
          p-6
        "
      >

        <div className="flex items-center justify-between">

          <div>

            <p className="text-sm text-zinc-500">

              Runtime Status

            </p>

            <h3
              className="
                mt-2
                text-2xl
                font-black
                text-green-400
              "
            >

              ACTIVE

            </h3>

          </div>

          <div
            className="
              h-4
              w-4
              rounded-full
              bg-green-400
              shadow-[0_0_20px_#4ade80]
            "
          />

        </div>

      </div>

    </aside>

  );
}

function SidebarItem({
  href,
  icon,
  title,
}: any) {

  return (

    <Link
      href={href}
      className="
        flex
        items-center
        gap-4
        rounded-2xl
        border
        border-white/5
        bg-black/20
        px-5
        py-4
        transition-all
        hover:border-cyan-500/30
        hover:bg-cyan-500/10
      "
    >

      <div className="text-cyan-300">

        {icon}

      </div>

      <span className="font-bold">

        {title}

      </span>

    </Link>

  );
}

function SidebarButton({
  icon,
  title,
  danger = false,
}: any) {

  return (

    <button
      className={`
        flex
        w-full
        items-center
        gap-4
        rounded-2xl
        border
        px-5
        py-4
        transition-all

        ${
          danger
            ? "border-red-500/20 bg-red-500/10 hover:border-red-500/40 hover:bg-red-500/20"
            : "border-white/5 bg-black/20 hover:border-cyan-500/30 hover:bg-cyan-500/10"
        }
      `}
    >

      <div
        className={
          danger
            ? "text-red-400"
            : "text-cyan-300"
        }
      >

        {icon}

      </div>

      <span className="font-bold">

        {title}

      </span>

    </button>

  );
}