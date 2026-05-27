"use client";

import Link from "next/link";

import {
  Bot,
  Cpu,
  Clock3,
  Eye,
  DollarSign,
  RotateCcw,
  Activity,
} from "lucide-react";

interface Agent {
  id?: string;
  name?: string;

  is_active?: boolean;

  is_killed?: boolean;

  total_cost?: number;

  mission_count?: number;

  max_steps?: number;

  max_retries?: number;

  created_at?: string | null;
}

export default function AgentCard({
  agent,
}: {
  agent: Agent;
}) {

  const active =
    agent?.is_active &&
    !agent?.is_killed;

  return (

    <Link
      href={`/dashboard/agents/${agent?.id}`}
      className="
        block
      "
    >

      <div
        className="
          rounded-[32px]
          border
          border-cyan-500/20
          bg-[linear-gradient(180deg,#081120_0%,#07111d_100%)]
          p-7
          overflow-hidden
          relative
          transition-all
          duration-300
          hover:border-cyan-400/40
          hover:shadow-[0_0_40px_rgba(34,211,238,0.08)]
        "
      >

        {/* GLOW */}

        <div
          className="
            absolute
            top-0
            right-0
            h-48
            w-48
            rounded-full
            bg-cyan-500/10
            blur-3xl
          "
        />

        {/* HEADER */}

        <div
          className="
            relative
            z-10
            flex
            items-start
            justify-between
            gap-6
            flex-wrap
          "
        >

          {/* LEFT */}

          <div className="flex gap-5">

            {/* ICON */}

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
                shrink-0
              "
            >

              <Bot
                className="
                  text-cyan-300
                "
                size={38}
              />

            </div>

            {/* INFO */}

            <div>

              <div
                className="
                  flex
                  items-center
                  gap-4
                  flex-wrap
                "
              >

                <h2
                  className="
                    text-3xl
                    font-black
                  "
                >

                  {agent?.name ||
                    "Runtime Agent"}

                </h2>

                <div
                  className={`
                    rounded-full
                    px-4
                    py-2
                    text-sm
                    font-bold
                    border

                    ${
                      active
                        ? `
                          border-green-500/20
                          bg-green-500/10
                          text-green-300
                        `
                        : `
                          border-red-500/20
                          bg-red-500/10
                          text-red-300
                        `
                    }
                  `}
                >

                  {active
                    ? "ACTIVE"
                    : "KILLED"}

                </div>

              </div>

              <div
                className="
                  mt-5
                  flex
                  items-center
                  gap-6
                  flex-wrap
                "
              >

                {/* CREATED */}

                <div
                  className="
                    flex
                    items-center
                    gap-2
                    text-slate-400
                  "
                >

                  <Clock3 size={18} />

                  {agent?.created_at
                    ? new Date(
                        agent.created_at
                      ).toLocaleDateString()
                    : "N/A"}

                </div>

                {/* MISSIONS */}

                <div
                  className="
                    flex
                    items-center
                    gap-2
                    text-slate-400
                  "
                >

                  <Activity size={18} />

                  {agent?.mission_count || 0}
                  {" "}
                  missions

                </div>

              </div>

            </div>

          </div>

          {/* STATUS */}

          <div
            className="
              flex
              items-center
              gap-3
              rounded-full
              border
              border-cyan-500/20
              bg-cyan-500/10
              px-5
              py-2
            "
          >

            <div
              className={`
                h-2
                w-2
                rounded-full
                animate-pulse

                ${
                  active
                    ? "bg-green-400"
                    : "bg-red-400"
                }
              `}
            />

            <span
              className="
                text-sm
                font-bold
                text-cyan-200
              "
            >

              LIVE RUNTIME

            </span>

          </div>

        </div>

        {/* METRICS */}

        <div
          className="
            relative
            z-10
            grid
            grid-cols-1
            md:grid-cols-3
            gap-5
            mt-8
          "
        >

          {/* COST */}

          <div
            className="
              rounded-3xl
              border
              border-cyan-500/20
              bg-cyan-500/10
              p-5
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

                <p className="text-sm text-slate-400">

                  Total Cost

                </p>

                <h3
                  className="
                    text-4xl
                    font-black
                    mt-3
                    text-cyan-300
                  "
                >

                  $
                  {Number(
                    agent?.total_cost || 0
                  ).toFixed(6)}

                </h3>

              </div>

              <DollarSign
                className="
                  text-cyan-300
                "
                size={30}
              />

            </div>

          </div>

          {/* MAX STEPS */}

          <div
            className="
              rounded-3xl
              border
              border-purple-500/20
              bg-purple-500/10
              p-5
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

                <p className="text-sm text-slate-400">

                  Max Steps

                </p>

                <h3
                  className="
                    text-4xl
                    font-black
                    mt-3
                    text-purple-300
                  "
                >

                  {agent?.max_steps || 0}

                </h3>

              </div>

              <Cpu
                className="
                  text-purple-300
                "
                size={30}
              />

            </div>

          </div>

          {/* RETRIES */}

          <div
            className="
              rounded-3xl
              border
              border-yellow-500/20
              bg-yellow-500/10
              p-5
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

                <p className="text-sm text-slate-400">

                  Max Retries

                </p>

                <h3
                  className="
                    text-4xl
                    font-black
                    mt-3
                    text-yellow-300
                  "
                >

                  {agent?.max_retries || 0}

                </h3>

              </div>

              <RotateCcw
                className="
                  text-yellow-300
                "
                size={30}
              />

            </div>

          </div>

        </div>

        {/* VIEW BUTTON */}

        <div
          className="
            relative
            z-10
            mt-8
          "
        >

          <div
            className="
              flex
              items-center
              justify-center
              gap-3
              rounded-2xl
              bg-cyan-500
              hover:bg-cyan-400
              transition-all
              px-6
              py-4
              font-bold
              text-black
            "
          >

            <Eye size={18} />

            View Agent Runtime

          </div>

        </div>

      </div>

    </Link>

  );
}