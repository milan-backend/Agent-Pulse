// frontend/components/SystemHealth.tsx

"use client";

import {
  Activity,
  Cpu,
  ShieldCheck,
  Wifi,
  Database,
  Zap,
} from "lucide-react";

interface Props {
  websocketConnected?: boolean;
  usage?: any;
  summary?: any;
}

export default function SystemHealth({
  websocketConnected = false,
  usage = {},
  summary = {},
}: Props) {
  const healthItems = [
    {
      label: "Runtime Engine",
      value: "Operational",
      icon: Cpu,
      color:
        "text-cyan-300 border-cyan-500/20 bg-cyan-500/10",
    },
    {
      label: "Mission Queue",
      value:
        summary?.total_steps || 0,
      icon: Activity,
      color:
        "text-purple-300 border-purple-500/20 bg-purple-500/10",
    },
    {
      label: "WebSocket",
      value:
        websocketConnected
          ? "Connected"
          : "Disconnected",
      icon: Wifi,
      color: websocketConnected
        ? "text-green-300 border-green-500/20 bg-green-500/10"
        : "text-red-300 border-red-500/20 bg-red-500/10",
    },
    {
      label: "Cache Hit",
      value: `${
        usage?.cache_hit_rate || 0
      }%`,
      icon: Database,
      color:
        "text-amber-300 border-amber-500/20 bg-amber-500/10",
    },
  ];

  return (
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
          items-center
          justify-between
          mb-8
        "
      >
        <div>
          <h2
            className="
              text-4xl
              font-black
            "
          >
            System Health
          </h2>

          <p
            className="
              text-slate-400
              mt-2
            "
          >
            Real-time runtime infrastructure
            status.
          </p>
        </div>

        <div
          className="
            flex
            items-center
            gap-3
            rounded-full
            border
            border-green-500/20
            bg-green-500/10
            px-5
            py-2
          "
        >
          <div className="h-2 w-2 rounded-full bg-green-400 animate-pulse" />

          <span
            className="
              text-sm
              font-bold
              text-green-300
            "
          >
            HEALTHY
          </span>
        </div>
      </div>

      {/* GRID */}

      <div
        className="
          relative
          z-10
          grid
          grid-cols-1
          md:grid-cols-2
          gap-5
        "
      >
        {healthItems.map(
          (item, index) => {
            const Icon =
              item.icon;

            return (
              <div
                key={index}
                className={`
                  rounded-3xl
                  border
                  p-6
                  ${item.color}
                `}
              >
                <div
                  className="
                    flex
                    items-center
                    justify-between
                  "
                >
                  <div>
                    <p className="text-sm opacity-80">
                      {item.label}
                    </p>

                    <h3
                      className="
                        text-3xl
                        font-black
                        mt-3
                      "
                    >
                      {item.value}
                    </h3>
                  </div>

                  <div
                    className="
                      h-14
                      w-14
                      rounded-2xl
                      bg-black/20
                      flex
                      items-center
                      justify-center
                    "
                  >
                    <Icon size={26} />
                  </div>
                </div>
              </div>
            );
          }
        )}
      </div>

      {/* BOTTOM BAR */}

      <div
        className="
          relative
          z-10
          mt-8
          rounded-3xl
          border
          border-cyan-500/10
          bg-black/20
          p-6
        "
      >
        <div
          className="
            flex
            items-center
            justify-between
            flex-wrap
            gap-5
          "
        >
          <div>
            <p className="text-slate-400">
              Runtime Spend
            </p>

            <h2
              className="
                text-5xl
                font-black
                mt-2
                text-cyan-300
              "
            >
              $
              {usage?.total_cost ||
                0}
            </h2>
          </div>

          <div>
            <p className="text-slate-400">
              Success Rate
            </p>

            <h2
              className="
                text-5xl
                font-black
                mt-2
                text-green-300
              "
            >
              {usage?.success_rate ||
                0}
              %
            </h2>
          </div>

          <div
            className="
              h-28
              w-28
              rounded-full
              border-[12px]
              border-cyan-400
              border-t-transparent
              rotate-45
              flex
              items-center
              justify-center
              shadow-[0_0_30px_rgba(34,211,238,0.25)]
            "
          >
            <Zap
              className="
                text-cyan-300
              "
              size={32}
            />
          </div>
        </div>
      </div>
    </div>
  );
}