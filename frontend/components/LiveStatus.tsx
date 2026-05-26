"use client";

import {
  Wifi,
  WifiOff,
  Activity,
  Zap,
  ShieldCheck,
  Clock3,
  Database,
} from "lucide-react";

interface Props {
  connected: boolean;

  summary?: any;

  lastEvent?: any;
}

export default function LiveStatus({
  connected,
  summary = {},
  lastEvent,
}: Props) {

  const totalSteps =
    Number(
      summary?.total_steps ||
      summary?.total ||
      0
    );

  const completed =
    Number(
      summary?.completed ||
      summary?.completed_steps ||
      0
    );

  const failed =
    Number(
      summary?.failed ||
      summary?.failed_steps ||
      0
    );

  const pending =
    Number(
      summary?.pending ||
      summary?.pending_steps ||
      0
    );

  const successRate =
    totalSteps > 0
      ? Math.round(
         (completed / totalSteps) * 100
        )
      : 0;

  const lastSeen =
    lastEvent?.timestamp ||
    lastEvent?.created_at;

  return (

    <div
      className={`
        rounded-[30px]
        border
        p-6
        overflow-hidden
        relative
        transition-all
        duration-300

        ${
          connected
            ? `
              border-green-500/20
              bg-[linear-gradient(180deg,#071120_0%,#081a14_100%)]
            `
            : `
              border-red-500/20
              bg-[linear-gradient(180deg,#071120_0%,#1a0b0b_100%)]
            `
        }
      `}
    >
      {/* GLOW */}

      <div
        className={`
          absolute
          top-0
          right-0
          h-40
          w-40
          rounded-full
          blur-3xl

          ${
            connected
              ? "bg-green-500/10"
              : "bg-red-500/10"
          }
        `}
      />

      {/* CONTENT */}

      <div className="relative z-10">

        {/* HEADER */}

        <div
          className="
            flex
            items-center
            justify-between
            gap-5
          "
        >
          <div>

            <p
              className="
                text-sm
                text-slate-400
                tracking-wide
              "
            >
              Runtime Connection
            </p>

            <h2
              className="
                mt-3
                text-4xl
                font-black
              "
            >
              {connected
                ? "LIVE"
                : "OFFLINE"}
            </h2>
          </div>

          <div
            className={`
              h-16
              w-16
              rounded-2xl
              border
              flex
              items-center
              justify-center

              ${
                connected
                  ? `
                    border-green-500/20
                    bg-green-500/10
                  `
                  : `
                    border-red-500/20
                    bg-red-500/10
                  `
              }
            `}
          >
            {connected ? (

              <Wifi
                className="
                  text-green-300
                "
                size={30}
              />

            ) : (

              <WifiOff
                className="
                  text-red-300
                "
                size={30}
              />
            )}
          </div>
        </div>

        {/* STATUS */}

        <div
          className="
            mt-8
            space-y-4
          "
        >
          {/* WS */}

          <div
            className="
              rounded-2xl
              bg-black/20
              border
              border-white/5
              p-4
              flex
              items-center
              justify-between
            "
          >
            <div
              className="
                flex
                items-center
                gap-3
              "
            >
              <Activity
                size={18}
                className="
                  text-cyan-300
                "
              />

              <span className="text-slate-300">
                WebSocket
              </span>
            </div>

            <div
              className={`
                flex
                items-center
                gap-2
                text-sm
                font-bold

                ${
                  connected
                    ? "text-green-300"
                    : "text-red-300"
                }
              `}
            >
              <div
                className={`
                  h-2
                  w-2
                  rounded-full
                  animate-pulse

                  ${
                    connected
                      ? "bg-green-400"
                      : "bg-red-400"
                  }
                `}
              />

              {connected
                ? "Connected"
                : "Disconnected"}
            </div>
          </div>

          {/* MISSIONS */}

          <div
            className="
              rounded-2xl
              bg-black/20
              border
              border-white/5
              p-4
              flex
              items-center
              justify-between
            "
          >
            <div
              className="
                flex
                items-center
                gap-3
              "
            >
              <Database
                size={18}
                className="
                  text-purple-300
                "
              />

              <span className="text-slate-300">
                Total Missions
              </span>
            </div>

            <span
              className="
                text-sm
                font-bold
                text-purple-300
              "
            >
              {totalSteps}
            </span>
          </div>

          {/* SUCCESS */}

          <div
            className="
              rounded-2xl
              bg-black/20
              border
              border-white/5
              p-4
              flex
              items-center
              justify-between
            "
          >
            <div
              className="
                flex
                items-center
                gap-3
              "
            >
              <ShieldCheck
                size={18}
                className="
                  text-green-300
                "
              />

              <span className="text-slate-300">
                Success Rate
              </span>
            </div>

            <span
              className="
                text-sm
                font-bold
                text-green-300
              "
            >
              {successRate}%
            </span>
          </div>

          {/* PENDING */}

          <div
            className="
              rounded-2xl
              bg-black/20
              border
              border-white/5
              p-4
              flex
              items-center
              justify-between
            "
          >
            <div
              className="
                flex
                items-center
                gap-3
              "
            >
              <Zap
                size={18}
                className="
                  text-yellow-300
                "
              />

              <span className="text-slate-300">
                Pending Queue
              </span>
            </div>

            <span
              className="
                text-sm
                font-bold
                text-yellow-300
              "
            >
              {pending}
            </span>
          </div>

          {/* LAST EVENT */}

          <div
            className="
              rounded-2xl
              bg-black/20
              border
              border-white/5
              p-4
              flex
              items-center
              justify-between
            "
          >
            <div
              className="
                flex
                items-center
                gap-3
              "
            >
              <Clock3
                size={18}
                className="
                  text-cyan-300
                "
              />

              <span className="text-slate-300">
                Last Event
              </span>
            </div>

            <span
              className="
                text-sm
                font-bold
                text-cyan-300
              "
            >
              {
                lastSeen &&
                !isNaN(
                  new Date(lastSeen).getTime()
                )
                  ? new Date(
                      lastSeen
                    ).toLocaleTimeString()
                  : "Waiting"
              }
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}