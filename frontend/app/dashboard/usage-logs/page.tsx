"use client";

import { useEffect, useState } from "react";

import {
  ScrollText,
  Activity,
  Clock3,
  Zap,
  Coins,
  Cpu,
  Bot,
} from "lucide-react";

import { getDashboardUsageLogs } from "@/components/api";

import LiveFeed from "@/components/LiveFeed";

import { toast } from "sonner";

export default function UsageLogsPage() {

  // =========================
  // STATE
  // =========================

  const [logs, setLogs] =
    useState<any[]>([]);

  const [loading, setLoading] =
    useState(true);

  // =========================
  // LOAD LOGS
  // =========================

  async function loadLogs() {

    try {

      const response =
        await getDashboardUsageLogs();

      const normalizedLogs =
        (
          Array.isArray(response)
            ? response
            : response?.logs || []
        ).sort(
          (
            a: any,
            b: any
          ) =>
            new Date(
              b?.created_at || 0
            ).getTime()
            -
            new Date(
              a?.created_at || 0
            ).getTime()
        );

      setLogs(normalizedLogs);

    } catch (err) {

      console.error(err);

      toast.error(
        err instanceof Error
          ? err.message
          : "Failed to load usage logs"
      );

    } finally {

      setLoading(false);
    }
  }

  // =========================
  // INITIAL LOAD
  // =========================

  useEffect(() => {

    loadLogs();

    const interval =
      setInterval(() => {

        loadLogs();

      }, 10000);

    return () =>
      clearInterval(interval);

  }, []);

  // =========================
  // METRICS
  // =========================

  const totalCost =
    logs.reduce(
      (
        total,
        log
      ) => (
        total +
        Number(
          log?.cost ?? 0
        )
      ),
      0
    );

  const totalTokens =
    logs.reduce(
      (
        total,
        log
      ) => {

        const prompt =
          Number(
            log?.prompt_tokens ?? 0
          );

        const completion =
          Number(
            log?.completion_tokens ?? 0
          );

        const directTotal =
          Number(
            log?.total_tokens ?? 0
          );

        return (
          total +
          (
            directTotal ||
            prompt + completion
          )
        );
      },
      0
    );

  const totalPromptTokens =
    logs.reduce(
      (
        total,
        log
      ) => (
        total +
        Number(
          log?.prompt_tokens ?? 0
        )
      ),
      0
    );

  const totalCompletionTokens =
    logs.reduce(
      (
        total,
        log
      ) => (
        total +
        Number(
          log?.completion_tokens ?? 0
        )
      ),
      0
    );

  // =========================
  // FORMAT NUMBERS
  // =========================

  function formatNumber(
    value: number
  ) {

    return new Intl.NumberFormat(
      "en-US",
      {
        notation: "compact",
        maximumFractionDigits: 1,
      }
    ).format(value);
  }

  // =========================
  // CARDS
  // =========================

  const cards = [

    {
      title: "Total Logs",
      value: formatNumber(
        logs.length
      ),
      icon: Activity,
      color: `
        border-cyan-500/20
        bg-cyan-500/10
        text-cyan-300
      `,
    },

    {
      title: "Prompt Tokens",
      value: formatNumber(
        totalPromptTokens
      ),
      icon: Bot,
      color: `
        border-blue-500/20
        bg-blue-500/10
        text-blue-300
      `,
    },

    {
      title: "Completion Tokens",
      value: formatNumber(
        totalCompletionTokens
      ),
      icon: Cpu,
      color: `
        border-green-500/20
        bg-green-500/10
        text-green-300
      `,
    },

    {
      title: "Total Tokens",
      value: formatNumber(
        totalTokens
      ),
      icon: Zap,
      color: `
        border-purple-500/20
        bg-purple-500/10
        text-purple-300
      `,
    },

    {
      title: "Runtime Cost",

      value:
        totalCost < 0.01
          ? `$${totalCost.toFixed(4)}`
          : `$${totalCost.toFixed(2)}`,

      icon: Coins,

      color: `
        border-yellow-500/20
        bg-yellow-500/10
        text-yellow-300
      `,
    },
  ];

  // =========================
  // LOADING
  // =========================

  if (loading) {

    return (

      <div
        className="
          min-h-[80vh]
          flex
          items-center
          justify-center
        "
      >

        <div className="text-center">

          <div
            className="
              h-16
              w-16
              rounded-full
              border-4
              border-cyan-500/20
              border-t-cyan-400
              animate-spin
              mx-auto
            "
          />

          <p
            className="
              mt-6
              text-xl
              font-bold
              text-cyan-300
            "
          >
            Loading Runtime Logs...
          </p>

        </div>
      </div>
    );
  }

  // =========================
  // PAGE
  // =========================

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

        <div className="relative z-10">

          <div
            className="
              flex
              items-center
              gap-5
              flex-wrap
            "
          >

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
              "
            >

              <ScrollText
                className="
                  text-cyan-300
                "
                size={34}
              />

            </div>

            {/* TITLE */}

            <div>

              <h1
                className="
                  text-5xl
                  font-black
                "
              >
                Runtime Usage Logs
              </h1>

              <p
                className="
                  mt-3
                  text-slate-400
                  text-lg
                "
              >
                Execution timeline,
                token telemetry and
                runtime observability.
              </p>

            </div>
          </div>
        </div>
      </div>

      {/* METRICS */}

      <div
        className="
          grid
          grid-cols-1
          md:grid-cols-2
          xl:grid-cols-5
          gap-6
        "
      >

        {cards.map(
          (
            card
          ) => {

            const Icon =
              card.icon;

            return (

              <div
                key={card.title}
                className={`
                  rounded-[30px]
                  border
                  p-6
                  overflow-hidden
                  relative
                  min-h-[180px]
                  flex
                  flex-col
                  justify-between
                  transition-all
                  duration-300
                  hover:scale-[1.02]
                  hover:shadow-[0_0_40px_rgba(0,255,255,0.08)]
                  hover:border-cyan-400/30
                  ${card.color}
                `}
              >

                {/* GLOW */}

                <div
                  className="
                    absolute
                    top-0
                    right-0
                    h-32
                    w-32
                    rounded-full
                    bg-white/5
                    blur-3xl
                  "
                />

                {/* TITLE */}

                <p
                  className="
                    text-[15px]
                    font-semibold
                    text-white/90
                    leading-snug
                    relative
                    z-10
                  "
                >
                  {card.title}
                </p>

                {/* VALUE + ICON */}

                <div
                  className="
                    flex
                    items-end
                    justify-between
                    gap-3
                    mt-7
                    min-w-0
                    relative
                    z-10
                  "
                >

                  {/* VALUE */}

                  <div className="min-w-0 flex-1">

                    <h2
                      className="
                        text-3xl
                        xl:text-4xl
                        font-black
                        tracking-tight
                        leading-none
                        truncate
                        whitespace-nowrap
                        overflow-hidden
                      "
                      title={card.value}
                    >
                      {card.value}
                    </h2>

                  </div>

                  {/* ICON */}

                  <div
                    className="
                      h-11
                      w-11
                      rounded-2xl
                      flex
                      items-center
                      justify-center
                      bg-white/5
                      border
                      border-white/10
                      shrink-0
                      backdrop-blur-sm
                    "
                  >
                    <Icon size={20} />
                  </div>

                </div>
              </div>
            );
          }
        )}
      </div>

      {/* TELEMETRY */}

      <div
        className="
          rounded-[32px]
          border
          border-cyan-500/20
          bg-[linear-gradient(180deg,#071120_0%,#091525_100%)]
          p-6
          flex
          items-center
          justify-between
          flex-wrap
          gap-5
        "
      >

        <div
          className="
            flex
            items-center
            gap-4
          "
        >

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

            <Clock3
              className="
                text-cyan-300
              "
              size={26}
            />

          </div>

          <div>

            <h2
              className="
                text-2xl
                font-black
              "
            >
              Runtime Telemetry Stream
            </h2>

            <p
              className="
                text-slate-400
                mt-1
              "
            >
              Monitoring live execution
              telemetry and runtime events.
            </p>

          </div>
        </div>

        {/* LIVE STATUS */}

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
            py-3
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

          <span
            className="
              text-sm
              font-bold
              text-green-300
            "
          >
            STREAMING
          </span>

        </div>
      </div>

      {/* LIVE FEED */}

      <LiveFeed logs={logs} />

    </div>
  );
}