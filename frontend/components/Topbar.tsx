// frontend/components/Topbar.tsx

"use client";

import {
  Bell,
  Search,
  Wifi,
  Cpu,
} from "lucide-react";

export default function Topbar() {

  return (

    <header
      className="
        sticky
        top-0
        z-40
        border-b
        border-white/5
        bg-[#020817]/80
        backdrop-blur-xl
      "
    >
      <div
        className="
          px-8
          py-5
          flex
          items-center
          justify-between
          gap-6
          flex-wrap
        "
      >
        {/* LEFT */}

        <div className="flex-1 max-w-2xl">

          <div
            className="
              relative
            "
          >
            <Search
              size={20}
              className="
                absolute
                left-5
                top-1/2
                -translate-y-1/2
                text-slate-500
              "
            />

            <input
              type="text"
              placeholder="
                Search agents, missions,
                analytics...
              "
              className="
                w-full
                rounded-[22px]
                border
                border-white/10
                bg-white/[0.04]
                py-4
                pl-14
                pr-5
                text-white
                outline-none
                transition-all
                placeholder:text-slate-500
                focus:border-cyan-400/40
                focus:bg-cyan-500/[0.05]
              "
            />
          </div>
        </div>

        {/* RIGHT */}

        <div
          className="
            flex
            items-center
            gap-4
          "
        >
          {/* STATUS */}

          <div
            className="
              hidden
              md:flex
              items-center
              gap-3
              rounded-full
              border
              border-green-500/20
              bg-green-500/10
              px-5
              py-3
            "
          >
            <div
              className="
                h-2.5
                w-2.5
                rounded-full
                bg-green-400
                animate-pulse
              "
            />

            <span
              className="
                text-sm
                font-bold
                text-green-300
              "
            >
              Runtime Live
            </span>
          </div>

          {/* WEBSOCKET */}

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
            <Wifi
              size={24}
              className="
                text-cyan-300
              "
            />
          </div>

          {/* CPU */}

          <div
            className="
              h-14
              w-14
              rounded-2xl
              border
              border-purple-500/20
              bg-purple-500/10
              flex
              items-center
              justify-center
            "
          >
            <Cpu
              size={24}
              className="
                text-purple-300
              "
            />
          </div>

          {/* NOTIFICATION */}

          <button
            className="
              relative
              h-14
              w-14
              rounded-2xl
              border
              border-white/10
              bg-white/[0.04]
              flex
              items-center
              justify-center
              hover:bg-white/[0.08]
              transition-all
            "
          >
            <Bell
              size={22}
              className="
                text-slate-300
              "
            />

            <div
              className="
                absolute
                top-3
                right-3
                h-2.5
                w-2.5
                rounded-full
                bg-red-400
              "
            />
          </button>

          {/* USER */}

          <div
            className="
              flex
              items-center
              gap-4
              rounded-[22px]
              border
              border-white/10
              bg-white/[0.04]
              px-4
              py-3
            "
          >
            <div
              className="
                h-12
                w-12
                rounded-2xl
                bg-cyan-500/15
                border
                border-cyan-500/20
                flex
                items-center
                justify-center
                text-lg
                font-black
                text-cyan-300
              "
            >
              AP
            </div>

            <div className="hidden md:block">
              <p
                className="
                  text-sm
                  text-slate-400
                "
              >
                Runtime Admin
              </p>

              <h3
                className="
                  font-bold
                  text-white
                "
              >
                AgentPulse
              </h3>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}