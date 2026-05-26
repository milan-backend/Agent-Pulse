"use client";

import {
  Rocket,
  ShieldCheck,
  Activity,
  Zap,
  Bot,
  ShieldAlert,
} from "lucide-react";

interface Props {
  summary?: any;
}

export default function SummaryCards({
  summary = {},
}: Props) {

  const overview =
    summary?.overview || summary;

  const cards = [
    {
      title: "Total Steps",
      value:
        Number(
          overview?.total_steps || 0
        ),
      icon: Rocket,
      color: `
        border-cyan-500/20
        bg-cyan-500/10
        text-cyan-300
      `,
      glow:
        "shadow-[0_0_40px_rgba(34,211,238,0.12)]",
    },

    {
      title: "Completed",
      value:
        Number(
          overview?.completed ||
          overview?.successful_steps ||
          0
        ),
      icon: ShieldCheck,
      color: `
        border-green-500/20
        bg-green-500/10
        text-green-300
      `,
      glow:
        "shadow-[0_0_40px_rgba(34,197,94,0.12)]",
    },

    {
      title: "Failed",
      value:
        Number(
          overview?.failed ||
          overview?.failed_steps ||
          0
        ),
      icon: ShieldAlert,
      color: `
        border-red-500/20
        bg-red-500/10
        text-red-300
      `,
      glow:
        "shadow-[0_0_40px_rgba(239,68,68,0.12)]",
    },

    {
      title: "Pending",
      value:
        Number(
          overview?.pending ||
          overview?.pending_steps ||
          0
        ),
      icon: Activity,
      color: `
        border-amber-500/20
        bg-amber-500/10
        text-amber-300
      `,
      glow:
        "shadow-[0_0_40px_rgba(251,191,36,0.12)]",
    },

    {
      title: "Success Rate",
      value: `${
        Number(
          overview?.success_rate || 0
        )
      }%`,
      icon: Zap,
      color: `
        border-emerald-500/20
        bg-emerald-500/10
        text-emerald-300
      `,
      glow:
        "shadow-[0_0_40px_rgba(16,185,129,0.12)]",
    },

    {
      title: "Live Runtime",
      value:
        overview?.live_status ||
        "ONLINE",
      icon: Bot,
      color: `
        border-purple-500/20
        bg-purple-500/10
        text-purple-300
      `,
      glow:
        "shadow-[0_0_40px_rgba(168,85,247,0.12)]",
    },
  ];

  return (

    <div
      className="
        grid
        grid-cols-1
        md:grid-cols-2
        xl:grid-cols-3
        gap-6
      "
    >
      {cards.map(
        (card, index) => {
          const Icon =
            card.icon;

          return (
            <div
              key={index}
              className={`
                rounded-[30px]
                border
                p-7
                overflow-hidden
                relative
                transition-all
                duration-300
                hover:scale-[1.01]
                ${card.color}
                ${card.glow}
              `}
            >
              {/* BACKGROUND GLOW */}

              <div
                className="
                  absolute
                  top-0
                  right-0
                  h-40
                  w-40
                  rounded-full
                  bg-white/5
                  blur-3xl
                "
              />

              {/* CONTENT */}

              <div className="relative z-10">
                {/* TOP */}

                <div
                  className="
                    flex
                    items-center
                    justify-between
                  "
                >
                  <div>
                    <p
                      className="
                        text-sm
                        opacity-80
                        tracking-wide
                      "
                    >
                      {card.title}
                    </p>

                    <h2
                      className="
                        mt-4
                        text-5xl
                        font-black
                        tracking-tight
                      "
                    >
                      {card.value}
                    </h2>
                  </div>

                  <div
                    className="
                      h-16
                      w-16
                      rounded-2xl
                      bg-black/20
                      flex
                      items-center
                      justify-center
                      border
                      border-white/10
                    "
                  >
                    <Icon size={30} />
                  </div>
                </div>

                {/* BOTTOM */}

                <div
                  className="
                    mt-8
                    flex
                    items-center
                    gap-3
                    text-sm
                    font-bold
                  "
                >
                  <div
                    className="
                      h-2
                      w-2
                      rounded-full
                      bg-current
                      animate-pulse
                    "
                  />

                  LIVE METRIC
                </div>
              </div>
            </div>
          );
        }
      )}
    </div>
  );
}