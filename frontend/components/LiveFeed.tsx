"use client";

import {
  Activity,
  Bot,
  Clock3,
  ShieldCheck,
  AlertTriangle,
  Zap,
  DollarSign,
  Cpu,
  Database,
} from "lucide-react";

interface Props {
  logs?: any[];
}

export default function LiveFeed({
  logs = [],
}: Props) {

  // =========================
  // STATUS COLORS
  // =========================

  function getStatusColor(
    success?: boolean
  ) {

    if (success === true) {

      return `
        border-green-500/20
        bg-green-500/10
        text-green-300
      `;
    }

    if (success === false) {

      return `
        border-red-500/20
        bg-red-500/10
        text-red-300
      `;
    }

    return `
      border-cyan-500/20
      bg-cyan-500/10
      text-cyan-300
    `;
  }

  // =========================
  // STATUS LABEL
  // =========================

  function getStatusLabel(
    success?: boolean,
    status?: string
  ) {

    if (status) {
      return status
        .replace("_", " ")
        .toUpperCase()
    }

    if (success === true) {
      return "SUCCESS"
    }

    if (success === false) {
      return "FAILED"
    }

    return "RUNNING"
  }

  const sortedLogs =
    [...logs].sort(
      (
        a,
        b
      ) =>
        new Date(
          b?.created_at || 0
        ).getTime()
        -
        new Date(
          a?.created_at || 0
        ).getTime()
    )

  const hasLogs =
    sortedLogs.length > 0

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
            Live Runtime Feed
          </h2>

          <p
            className="
              text-slate-400
              mt-2
            "
          >
            Real-time usage telemetry
            and execution logs.
          </p>

        </div>

        {/* LIVE */}

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
              text-cyan-300
            "
          >
            LIVE EVENTS
          </span>

        </div>
      </div>

      {/* EMPTY */}

      {!hasLogs && (

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

          <Activity
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
            No Runtime Events
          </h3>

          <p
            className="
              mt-3
              text-slate-400
            "
          >
            Waiting for usage telemetry
            updates.
          </p>

        </div>
      )}

      {/* LOGS */}

      {hasLogs && (

        <div
          className="
            relative
            z-10
            space-y-5
            max-h-[650px]
            overflow-y-auto
            pr-2
          "
        >

          {sortedLogs.map(
            (
              log: any,
              index: number
            ) => {

              const success =
                log?.success ??
                (
                  log?.status === "completed"
                    ? true
                    : log?.status === "failed"
                    ? false
                    : undefined
                )

              const status =
                getStatusLabel(
                  success,
                  log?.status
                );

              return (

                <div
                  key={
                    log?.id ||
                    log?.step_id ||
                    index
                  }
                  className="
                    rounded-3xl
                    border
                    border-white/10
                    bg-black/20
                    p-6
                    transition-all
                    duration-300
                    hover:border-cyan-500/30
                  "
                >

                  {/* TOP */}

                  <div
                    className="
                      flex
                      items-start
                      justify-between
                      gap-5
                      flex-wrap
                    "
                  >

                    {/* LEFT */}

                    <div className="flex-1">

                      {/* STATUS */}

                      <div
                        className="
                          flex
                          items-center
                          gap-4
                          flex-wrap
                        "
                      >

                        {/* BADGE */}

                        <div
                          className={`
                            rounded-full
                            border
                            px-4
                            py-2
                            text-sm
                            font-bold
                            ${getStatusColor(
                              success
                            )}
                          `}
                        >
                          {status}
                        </div>

                        {/* TIME */}

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
                            size={16}
                          />

                          {
                            log?.created_at
                              ? new Date(
                                  log.created_at
                                ).toLocaleString()
                              : "LIVE"
                          }

                        </div>
                      </div>

                      {/* TITLE */}

                      <h3
                        className="
                          mt-5
                          text-2xl
                          font-black
                          break-words
                        "
                      >
                        {
                          log?.action ||
                          log?.event_type ||
                          log?.status ||
                          "Runtime Usage Event"
                        }
                      </h3>

                      {/* IDS */}

                      <div
                        className="
                          mt-5
                          grid
                          grid-cols-1
                          md:grid-cols-2
                          gap-4
                        "
                      >

                        {/* AGENT */}

                        <div
                          className="
                            rounded-2xl
                            border
                            border-cyan-500/20
                            bg-cyan-500/10
                            p-4
                          "
                        >

                          <p
                            className="
                              text-xs
                              text-cyan-200/70
                            "
                          >
                            AGENT ID
                          </p>

                          <p
                            className="
                              mt-2
                              text-sm
                              font-bold
                              text-cyan-300
                              break-all
                            "
                          >
                            {log?.agent_id ||
                              "N/A"}
                          </p>

                        </div>

                        {/* STEP */}

                        <div
                          className="
                            rounded-2xl
                            border
                            border-purple-500/20
                            bg-purple-500/10
                            p-4
                          "
                        >

                          <p
                            className="
                              text-xs
                              text-purple-200/70
                            "
                          >
                            STEP ID
                          </p>

                          <p
                            className="
                              mt-2
                              text-sm
                              font-bold
                              text-purple-300
                              break-all
                            "
                          >
                            {log?.step_id ||
                              "N/A"}
                          </p>

                        </div>
                      </div>

                      {/* TELEMETRY */}

                      <div
                        className="
                          mt-5
                          flex
                          items-center
                          gap-4
                          flex-wrap
                        "
                      >

                        {/* PROMPT TOKENS */}

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

                          <span
                            className="
                              text-sm
                              font-bold
                              text-cyan-300
                            "
                          >
                            PROMPT:
                            {" "}
                            {
                              Number(
                                log?.prompt_tokens || 0
                              ).toLocaleString()
                            }
                          </span>

                        </div>

                        {/* COMPLETION TOKENS */}

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

                          <Cpu
                            size={18}
                            className="
                              text-green-300
                            "
                          />

                          <span
                            className="
                              text-sm
                              font-bold
                              text-green-300
                            "
                          >
                            COMPLETION:
                            {" "}
                            {
                              Number(
                                log?.completion_tokens || 0
                              ).toLocaleString()
                            }
                          </span>

                        </div>

                        {/* TOTAL TOKENS */}

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

                          <Database
                            size={18}
                            className="
                              text-yellow-300
                            "
                          />

                          <span
                            className="
                              text-sm
                              font-bold
                              text-yellow-300
                            "
                          >
                            TOTAL:
                            {" "}
                            {
                              Number(
                                log?.total_tokens ??
                                (
                                  Number(
                                    log?.prompt_tokens || 0
                                  ) +
                                  Number(
                                    log?.completion_tokens || 0
                                  )
                                )
                              ).toLocaleString()
                            }
                          </span>

                        </div>

                        {/* COST */}

                        <div
                          className="
                            rounded-2xl
                            border
                            border-pink-500/20
                            bg-pink-500/10
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
                              text-pink-300
                            "
                          />

                          <span
                            className="
                              text-sm
                              font-bold
                              text-pink-300
                            "
                          >
                            $
                            {Number(
                              log?.cost || 0
                            ).toFixed(6)}
                          </span>

                        </div>

                      </div>
                    </div>

                    {/* RIGHT */}

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
                          success === true

                            ? `
                              border-green-500/20
                              bg-green-500/10
                            `

                            : success === false

                            ? `
                              border-red-500/20
                              bg-red-500/10
                            `

                            : `
                              border-cyan-500/20
                              bg-cyan-500/10
                            `
                        }
                      `}
                    >

                      {success === true ? (

                        <ShieldCheck
                          className="
                            text-green-300
                          "
                          size={30}
                        />

                      ) : success === false ? (

                        <AlertTriangle
                          className="
                            text-red-300
                          "
                          size={30}
                        />

                      ) : (

                        <Activity
                          className="
                            text-cyan-300
                          "
                          size={30}
                        />
                      )}

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