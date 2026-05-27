"use client";

import {
  Clock3,
  Activity,
  CheckCircle2,
  AlertTriangle,
  PauseCircle,
  Rocket,
  Bot,
  Zap,
  DollarSign,
} from "lucide-react";

interface Props {
  logs?: any[];
}

export default function StepTimeline({
  logs = [],
}: Props) {

  function getStatusIcon(
    status?: string
  ) {

    switch (
      status?.toLowerCase()
    ) {

      case "completed":
      case "success":
        return (
          <CheckCircle2
            className="
              text-green-300
            "
            size={22}
          />
        );

      case "failed":
      case "error":
        return (
          <AlertTriangle
            className="
              text-red-300
            "
            size={22}
          />
        );

      case "paused":
        return (
          <PauseCircle
            className="
              text-yellow-300
            "
            size={22}
          />
        );

      default:
        return (
          <Activity
            className="
              text-cyan-300
            "
            size={22}
          />
        );
    }
  }

  function getStatusStyles(
    status?: string
  ) {

    switch (
      status?.toLowerCase()
    ) {

      case "completed":
      case "success":
        return `
          border-green-500/20
          bg-green-500/10
          text-green-300
        `;

      case "failed":
      case "error":
        return `
          border-red-500/20
          bg-red-500/10
          text-red-300
        `;

      case "paused":
        return `
          border-yellow-500/20
          bg-yellow-500/10
          text-yellow-300
        `;

      default:
        return `
          border-cyan-500/20
          bg-cyan-500/10
          text-cyan-300
        `;
    }
  }

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
          h-64
          w-64
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
          flex-wrap
          gap-5
          mb-10
        "
      >
        <div>
          <h2
            className="
              text-4xl
              font-black
            "
          >
            Mission Timeline
          </h2>

          <p
            className="
              mt-2
              text-slate-400
            "
          >
            Chronological runtime execution
            events and telemetry.
          </p>
        </div>

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
          <Rocket
            size={18}
            className="
              text-cyan-300
            "
          />

          <span
            className="
              text-sm
              font-bold
              text-cyan-300
            "
          >
            LIVE TIMELINE
          </span>
        </div>
      </div>

      {/* EMPTY */}

      {logs.length === 0 && (

        <div
          className="
            relative
            z-10
            rounded-3xl
            border
            border-white/10
            bg-white/[0.03]
            p-10
            text-center
          "
        >
          <Clock3
            size={48}
            className="
              mx-auto
              text-slate-500
            "
          />

          <h3
            className="
              mt-5
              text-2xl
              font-black
            "
          >
            No Timeline Events
          </h3>

          <p
            className="
              mt-3
              text-slate-400
            "
          >
            Runtime timeline will appear
            once missions start executing.
          </p>
        </div>
      )}

      {/* TIMELINE */}

      {logs.length > 0 && (

        <div
          className="
            relative
            z-10
            space-y-8
          "
        >
          {logs.map(
            (
              log: any,
              index: number
            ) => {

              const status =
                log?.status ||
                "running";

              return (

                <div
                  key={
                    log?.id ||
                    index
                  }
                  className="
                    flex
                    gap-6
                    items-start
                  "
                >
                  {/* LEFT DOT */}

                  <div className="relative">

                    {/* LINE */}

                    {index !==
                      logs.length -
                        1 && (

                      <div
                        className="
                          absolute
                          left-1/2
                          top-16
                          -translate-x-1/2
                          h-full
                          w-[2px]
                          bg-gradient-to-b
                          from-cyan-500/40
                          to-transparent
                        "
                      />
                    )}

                    {/* ICON */}

                    <div
                      className={`
                        relative
                        z-10
                        h-14
                        w-14
                        rounded-2xl
                        border
                        flex
                        items-center
                        justify-center
                        ${getStatusStyles(
                          status
                        )}
                      `}
                    >
                      {getStatusIcon(
                        status
                      )}
                    </div>
                  </div>

                  {/* CONTENT */}

                  <div
                    className="
                      flex-1
                      rounded-3xl
                      border
                      border-white/10
                      bg-black/20
                      p-6
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
                      <div>
                        <div
                          className="
                            flex
                            items-center
                            gap-3
                            flex-wrap
                          "
                        >
                          <div
                            className={`
                              rounded-full
                              border
                              px-4
                              py-2
                              text-sm
                              font-bold
                              ${getStatusStyles(
                                status
                              )}
                            `}
                          >
                            {status}
                          </div>

                          <div
                            className="
                              flex
                              items-center
                              gap-2
                              text-sm
                              text-slate-400
                            "
                          >
                            <Clock3
                              size={15}
                            />

                            {log?.created_at ||
                            log?.timestamp
                              ? new Date(
                                  log.created_at ||
                                  log.timestamp
                                ).toLocaleString()
                              : "LIVE"}
                          </div>
                        </div>

                        <h3
                          className="
                            mt-5
                            text-2xl
                            font-black
                            break-words
                          "
                        >
                          {log?.message ||
                            log?.event ||
                            log?.task ||
                            "Runtime Event"}
                        </h3>
                      </div>
                    </div>

                    {/* DESCRIPTION */}

                    {(log?.description ||
                      log?.details) && (

                      <p
                        className="
                          mt-5
                          text-slate-400
                          leading-relaxed
                        "
                      >
                        {log?.description ||
                          log?.details}
                      </p>
                    )}

                    {/* FOOTER */}

                    <div
                      className="
                        mt-6
                        flex
                        items-center
                        gap-4
                        flex-wrap
                      "
                    >
                      {/* AGENT */}

                      <div
                        className="
                          rounded-2xl
                          border
                          border-cyan-500/20
                          bg-cyan-500/10
                          px-4
                          py-3
                          flex
                          items-center
                          gap-3
                        "
                      >
                        <Bot
                          size={18}
                          className="
                            text-cyan-300
                          "
                        />

                        <div>
                          <p
                            className="
                              text-xs
                              text-slate-400
                            "
                          >
                            Agent
                          </p>

                          <p
                            className="
                              mt-1
                              text-sm
                              font-bold
                              text-cyan-300
                              break-all
                            "
                          >
                            {log?.agent_id ||
                              "Runtime"}
                          </p>
                        </div>
                      </div>

                      {/* STEP */}

                      <div
                        className="
                          rounded-2xl
                          border
                          border-purple-500/20
                          bg-purple-500/10
                          px-4
                          py-3
                          flex
                          items-center
                          gap-3
                        "
                      >
                        <Rocket
                          size={18}
                          className="
                            text-purple-300
                          "
                        />

                        <div>
                          <p
                            className="
                              text-xs
                              text-slate-400
                            "
                          >
                            Mission
                          </p>

                          <p
                            className="
                              mt-1
                              text-sm
                              font-bold
                              text-purple-300
                              break-all
                            "
                          >
                            {log?.step_id ||
                              "MISSION"}
                          </p>
                        </div>
                      </div>

                      {/* TOKENS */}

                      <div
                        className="
                          rounded-2xl
                          border
                          border-green-500/20
                          bg-green-500/10
                          px-4
                          py-3
                          flex
                          items-center
                          gap-3
                        "
                      >
                        <Zap
                          size={18}
                          className="
                            text-green-300
                          "
                        />

                        <div>
                          <p
                            className="
                              text-xs
                              text-slate-400
                            "
                          >
                            Tokens
                          </p>

                          <p
                            className="
                              mt-1
                              text-sm
                              font-bold
                              text-green-300
                            "
                          >
                            {(log?.prompt_tokens || 0) +
                              (log?.completion_tokens || 0)}
                          </p>
                        </div>
                      </div>

                      {/* COST */}

                      <div
                        className="
                          rounded-2xl
                          border
                          border-yellow-500/20
                          bg-yellow-500/10
                          px-4
                          py-3
                          flex
                          items-center
                          gap-3
                        "
                      >
                        <DollarSign
                          size={18}
                          className="
                            text-yellow-300
                          "
                        />

                        <div>
                          <p
                            className="
                              text-xs
                              text-slate-400
                            "
                          >
                            Cost
                          </p>

                          <p
                            className="
                              mt-1
                              text-sm
                              font-bold
                              text-yellow-300
                            "
                          >
                            $
                            {Number(
                              log?.execution_cost ||
                              0
                            ).toFixed(6)}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              );
            }
          )}
        </div>
      )}
    </div>
  );
}