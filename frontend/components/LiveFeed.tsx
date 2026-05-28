"use client";

import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Clock3,
  Coins,
  Cpu,
  Zap,
} from "lucide-react";

interface LiveFeedProps {
  logs: any[];
}

export default function LiveFeed({
  logs,
}: LiveFeedProps) {

  // =========================
  // FORMAT TIME
  // =========================

  const formatTime = (
    timestamp: string
  ) => {

    if (!timestamp)
      return "Unknown";

    return new Date(
      timestamp
    ).toLocaleString();
  };

  // =========================
  // FORMAT COST
  // =========================

  const formatCost = (
    cost: number
  ) => {

    if (!cost)
      return "$0.0000";

    return cost < 0.01
      ? `$${cost.toFixed(4)}`
      : `$${cost.toFixed(2)}`;
  };

  // =========================
  // EMPTY STATE
  // =========================

  if (!logs?.length) {

    return (

      <div
        className="
          rounded-[32px]
          border
          border-cyan-500/20
          bg-[#071120]
          p-10
          text-center
        "
      >

        <div
          className="
            w-20
            h-20
            mx-auto
            rounded-3xl
            bg-cyan-500/10
            border
            border-cyan-500/20
            flex
            items-center
            justify-center
          "
        >

          <Activity
            className="
              text-cyan-300
            "
            size={34}
          />

        </div>

        <h2
          className="
            text-3xl
            font-black
            mt-6
          "
        >
          No Runtime Logs
        </h2>

        <p
          className="
            text-slate-400
            mt-3
          "
        >
          Runtime execution events
          will appear here.
        </p>

      </div>
    );
  }

  // =========================
  // PAGE
  // =========================

  return (

    <div
      className="
        rounded-[32px]
        border
        border-cyan-500/20
        bg-[linear-gradient(180deg,#071120_0%,#091525_100%)]
        p-8
      "
    >

      {/* HEADER */}

      <div
        className="
          flex
          items-center
          justify-between
          flex-wrap
          gap-5
          mb-8
        "
      >

        <div>

          <h2
            className="
              text-5xl
              font-black
            "
          >
            Live Runtime Feed
          </h2>

          <p
            className="
              text-slate-400
              mt-3
              text-lg
            "
          >
            Real-time usage telemetry
            and execution logs.
          </p>

        </div>

        {/* LIVE BADGE */}

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
            LIVE EVENTS
          </span>

        </div>
      </div>

      {/* LOGS */}

      <div className="space-y-6">

        {logs.map(
          (
            log,
            index
          ) => {

            // =========================
            // STATUS LOGIC
            // =========================

            const eventType =
              (
                log?.event_type ||
                log?.type ||
                ""
              ).toLowerCase();

            const isCompleted =
              eventType ===
              "execution_completed";

            const isFailed =
              eventType ===
              "execution_failed";

            const badgeText =
              isCompleted
                ? "COMPLETED"
                : isFailed
                ? "FAILED"
                : "RUNNING";

            const title =
              isCompleted
                ? "Execution Completed"
                : isFailed
                ? "Execution Failed"
                : "Execution Started";

            const badgeColor =
              isCompleted
                ? `
                  bg-green-500/10
                  border-green-500/20
                  text-green-300
                `
                : isFailed
                ? `
                  bg-red-500/10
                  border-red-500/20
                  text-red-300
                `
                : `
                  bg-cyan-500/10
                  border-cyan-500/20
                  text-cyan-300
                `;

            const StatusIcon =
              isCompleted
                ? CheckCircle2
                : isFailed
                ? AlertTriangle
                : Activity;

            const totalTokens =
              Number(
                log?.total_tokens ??
                (
                  Number(
                    log?.prompt_tokens ?? 0
                  ) +
                  Number(
                    log?.completion_tokens ?? 0
                  )
                )
              );

            return (

              <div
                key={index}
                className="
                  rounded-[30px]
                  border
                  border-cyan-500/20
                  bg-[#081425]
                  p-7
                  hover:border-cyan-400/30
                  transition-all
                  duration-300
                "
              >

                {/* TOP */}

                <div
                  className="
                    flex
                    items-center
                    justify-between
                    flex-wrap
                    gap-4
                  "
                >

                  {/* LEFT */}

                  <div
                    className="
                      flex
                      items-center
                      gap-4
                      flex-wrap
                    "
                  >

                    {/* STATUS */}

                    <div
                      className={`
                        px-4
                        py-2
                        rounded-full
                        border
                        text-sm
                        font-bold
                        flex
                        items-center
                        gap-2
                        ${badgeColor}
                      `}
                    >

                      <StatusIcon
                        size={16}
                      />

                      {badgeText}

                    </div>

                    {/* TIME */}

                    <div
                      className="
                        flex
                        items-center
                        gap-2
                        text-slate-300
                      "
                    >

                      <Clock3
                        size={16}
                      />

                      <span
                        className="
                          text-sm
                          font-medium
                        "
                      >
                        {formatTime(
                          log?.created_at
                        )}
                      </span>

                    </div>
                  </div>

                  {/* RIGHT ICON */}

                  <div
                    className="
                      w-14
                      h-14
                      rounded-2xl
                      border
                      border-cyan-500/20
                      bg-cyan-500/10
                      flex
                      items-center
                      justify-center
                      shrink-0
                    "
                  >

                    <Activity
                      className="
                        text-cyan-300
                      "
                      size={26}
                    />

                  </div>
                </div>

                {/* TITLE */}

                <h3
                  className="
                    text-3xl
                    font-black
                    mt-7
                  "
                >
                  {title}
                </h3>

                {/* IDS */}

                <div
                  className="
                    grid
                    grid-cols-1
                    xl:grid-cols-2
                    gap-5
                    mt-7
                  "
                >

                  {/* AGENT ID */}

                  <div
                    className="
                      rounded-2xl
                      border
                      border-cyan-500/20
                      bg-cyan-500/10
                      p-5
                    "
                  >

                    <p
                      className="
                        text-xs
                        uppercase
                        tracking-wider
                        text-cyan-200/70
                        font-bold
                      "
                    >
                      Agent ID
                    </p>

                    <p
                      className="
                        mt-3
                        font-bold
                        text-cyan-100
                        break-all
                      "
                    >
                      {log?.agent_id || "N/A"}
                    </p>

                  </div>

                  {/* STEP ID */}

                  <div
                    className="
                      rounded-2xl
                      border
                      border-indigo-500/20
                      bg-indigo-500/10
                      p-5
                    "
                  >

                    <p
                      className="
                        text-xs
                        uppercase
                        tracking-wider
                        text-indigo-200/70
                        font-bold
                      "
                    >
                      Step ID
                    </p>

                    <p
                      className="
                        mt-3
                        font-bold
                        text-indigo-100
                        break-all
                      "
                    >
                      {log?.step_id || "N/A"}
                    </p>

                  </div>
                </div>

                {/* METRICS */}

                <div
                  className="
                    grid
                    grid-cols-2
                    xl:grid-cols-4
                    gap-4
                    mt-7
                  "
                >

                  {/* PROMPT */}

                  <div
                    className="
                      rounded-2xl
                      border
                      border-cyan-500/20
                      bg-cyan-500/10
                      p-4
                    "
                  >

                    <div
                      className="
                        flex
                        items-center
                        justify-between
                        gap-3
                      "
                    >

                      <p
                        className="
                          text-sm
                          font-bold
                          text-cyan-200
                        "
                      >
                        PROMPT
                      </p>

                      <Cpu
                        size={18}
                        className="
                          text-cyan-300
                          shrink-0
                        "
                      />

                    </div>

                    <p
                      className="
                        mt-3
                        text-2xl
                        font-black
                        text-cyan-100
                      "
                    >
                      {Number(
                        log?.prompt_tokens ?? 0
                      ).toLocaleString()}
                    </p>

                  </div>

                  {/* COMPLETION */}

                  <div
                    className="
                      rounded-2xl
                      border
                      border-green-500/20
                      bg-green-500/10
                      p-4
                    "
                  >

                    <div
                      className="
                        flex
                        items-center
                        justify-between
                        gap-3
                      "
                    >

                      <p
                        className="
                          text-sm
                          font-bold
                          text-green-200
                        "
                      >
                        COMPLETION
                      </p>

                      <Cpu
                        size={18}
                        className="
                          text-green-300
                          shrink-0
                        "
                      />

                    </div>

                    <p
                      className="
                        mt-3
                        text-2xl
                        font-black
                        text-green-100
                      "
                    >
                      {Number(
                        log?.completion_tokens ?? 0
                      ).toLocaleString()}
                    </p>

                  </div>

                  {/* TOTAL */}

                  <div
                    className="
                      rounded-2xl
                      border
                      border-yellow-500/20
                      bg-yellow-500/10
                      p-4
                    "
                  >

                    <div
                      className="
                        flex
                        items-center
                        justify-between
                        gap-3
                      "
                    >

                      <p
                        className="
                          text-sm
                          font-bold
                          text-yellow-200
                        "
                      >
                        TOTAL
                      </p>

                      <Zap
                        size={18}
                        className="
                          text-yellow-300
                          shrink-0
                        "
                      />

                    </div>

                    <p
                      className="
                        mt-3
                        text-2xl
                        font-black
                        text-yellow-100
                      "
                    >
                      {totalTokens.toLocaleString()}
                    </p>

                  </div>

                  {/* COST */}

                  <div
                    className="
                      rounded-2xl
                      border
                      border-purple-500/20
                      bg-purple-500/10
                      p-4
                    "
                  >

                    <div
                      className="
                        flex
                        items-center
                        justify-between
                        gap-3
                      "
                    >

                      <p
                        className="
                          text-sm
                          font-bold
                          text-purple-200
                        "
                      >
                        COST
                      </p>

                      <Coins
                        size={18}
                        className="
                          text-purple-300
                          shrink-0
                        "
                      />

                    </div>

                    <p
                      className="
                        mt-3
                        text-2xl
                        font-black
                        text-purple-100
                        whitespace-nowrap
                      "
                    >
                      {formatCost(
                        Number(
                          log?.cost ?? 0
                        )
                      )}
                    </p>

                  </div>
                </div>
              </div>
            );
          }
        )}
      </div>
    </div>
  );
}

