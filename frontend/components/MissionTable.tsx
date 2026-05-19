"use client";

import Link from "next/link";

import {
  Rocket,
  Clock3,
  CheckCircle2,
  AlertTriangle,
  RotateCcw,
  Eye,
  Database,
} from "lucide-react";

import {
  retryStep,
  killMission,
  resumeMission,
} from "@/components/api";

interface Mission {

  id?: string;

  task_name?: string;

  status?: string;

  created_at?: string;

  retry_count?: number;

  agent_id?: string;

  cache_hit?: boolean;

  runtime_controlled?: boolean;
}

export default function MissionTable({
  steps = [],
}: {
  steps: Mission[];
}) {

  // =========================
  // RETRY
  // =========================

  async function handleRetry(
    stepId: string
  ) {

    try {

      await retryStep(
        stepId
      );

      window.location.reload();

    } catch (err) {

      console.error(err);
    }
  }

  // =========================
  // KILL
  // =========================

  async function handleKill(
    stepId: string
  ) {

    try {

      await killMission(
        stepId
      );

      window.location.reload();

    } catch (err) {

      console.error(err);
    }
  }

  // =========================
  // RESUME
  // =========================

  async function handleResume(
    stepId: string
  ) {

    try {

      await resumeMission(
        stepId
      );

      window.location.reload();

    } catch (err) {

      console.error(err);
    }
  }

  // =========================
  // STATUS COLORS
  // =========================

  function getStatusColor(
    status: string
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

      case "running":
      case "processing":

        return `
          border-cyan-500/20
          bg-cyan-500/10
          text-cyan-300
        `;

      case "paused":

        return `
          border-yellow-500/20
          bg-yellow-500/10
          text-yellow-300
        `;

      default:

        return `
          border-slate-500/20
          bg-slate-500/10
          text-slate-300
        `;
    }
  }

  return (

    <div
      className="
        rounded-[32px]
        border
        border-cyan-500/20
        bg-[linear-gradient(180deg,#081120_0%,#07111d_100%)]
        p-8
        overflow-hidden
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
              text-4xl
              font-black
            "
          >
            Active Missions
          </h2>

          <p
            className="
              mt-2
              text-slate-400
            "
          >
            Real-time autonomous mission
            execution telemetry.
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
            className="text-cyan-300"
          />

          <span
            className="
              text-sm
              font-bold
              text-cyan-300
            "
          >
            {steps.length} MISSIONS
          </span>

        </div>
      </div>

      {/* EMPTY */}

      {steps.length === 0 && (

        <div
          className="
            rounded-3xl
            border
            border-white/10
            bg-white/[0.03]
            p-10
            text-center
          "
        >

          <Rocket
            className="
              mx-auto
              text-slate-500
            "
            size={48}
          />

          <h3
            className="
              mt-5
              text-2xl
              font-black
            "
          >
            No Missions Found
          </h3>

          <p
            className="
              mt-3
              text-slate-400
            "
          >
            Waiting for runtime execution
            tasks.
          </p>

        </div>
      )}

      {/* TABLE */}

      {steps.length > 0 && (

        <div className="space-y-5">

          {steps.map(
            (
              mission,
              index
            ) => {

              // FIXED HERE

              const stepId =
                mission.id || "";

              return (

                <div
                  key={
                    stepId || index
                  }
                  className="
                    rounded-3xl
                    border
                    border-cyan-500/10
                    bg-black/20
                    p-6
                    transition-all
                    duration-300
                    hover:border-cyan-400/30
                  "
                >

                  <div
                    className="
                      flex
                      items-start
                      justify-between
                      gap-6
                      flex-wrap
                    "
                  >

                    {/* LEFT */}

                    <div className="flex-1">

                      <div
                        className="
                          flex
                          items-center
                          gap-4
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
                            ${getStatusColor(
                              mission.status ||
                              ""
                            )}
                          `}
                        >
                          {mission.status ||
                            "Unknown"}
                        </div>

                        <div
                          className="
                            flex
                            items-center
                            gap-2
                            text-slate-400
                            text-sm
                          "
                        >

                          <Clock3
                            size={16}
                          />

                          {mission.created_at
                            ? new Date(
                                mission.created_at
                              ).toLocaleString()
                            : "Live"}

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
                        {mission.task_name ||
                          "AI Mission"}
                      </h3>

                      {/* AGENT */}

                      {mission.agent_id && (

                        <p
                          className="
                            mt-4
                            text-sm
                            text-slate-500
                            break-all
                          "
                        >
                          Agent:
                          {" "}
                          {mission.agent_id}
                        </p>
                      )}

                      {/* STATS */}

                      <div
                        className="
                          mt-5
                          flex
                          items-center
                          gap-6
                          flex-wrap
                        "
                      >

                        {/* RETRIES */}

                        <div
                          className="
                            rounded-2xl
                            bg-cyan-500/10
                            border
                            border-cyan-500/20
                            px-4
                            py-3
                          "
                        >

                          <p className="text-xs text-slate-400">
                            Retries
                          </p>

                          <p
                            className="
                              text-xl
                              font-black
                              text-cyan-300
                            "
                          >
                            {mission.retry_count || 0}
                          </p>

                        </div>

                        {/* CACHE */}

                        <div
                          className="
                            rounded-2xl
                            bg-green-500/10
                            border
                            border-green-500/20
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
                              text-green-300
                            "
                          />

                          <div>

                            <p className="text-xs text-slate-400">
                              Cache
                            </p>

                            <p
                              className="
                                text-xl
                                font-black
                                text-green-300
                              "
                            >
                              {mission.cache_hit
                                ? "HIT"
                                : "MISS"}
                            </p>

                          </div>
                        </div>
                      </div>
                    </div>

                    {/* ACTIONS */}

                    <div
                      className="
                        flex
                        flex-col
                        gap-3
                        min-w-[180px]
                      "
                    >

                      {/* VIEW */}

                      <Link
                        href={`/dashboard/missions/${stepId}`}
                        className="
                          flex
                          items-center
                          justify-center
                          gap-2
                          rounded-2xl
                          bg-cyan-500
                          hover:bg-cyan-400
                          transition-all
                          py-3
                          font-bold
                          text-black
                        "
                      >

                        <Eye size={18} />

                        View

                      </Link>

                      {/* RETRY */}

                      <button
                        onClick={() =>
                          handleRetry(
                            stepId
                          )
                        }
                        className="
                          flex
                          items-center
                          justify-center
                          gap-2
                          rounded-2xl
                          border
                          border-purple-500/20
                          bg-purple-500/10
                          hover:bg-purple-500/20
                          transition-all
                          py-3
                          font-bold
                          text-purple-300
                        "
                      >

                        <RotateCcw
                          size={18}
                        />

                        Retry

                      </button>

                      {/* RESUME */}

                      <button
                        onClick={() =>
                          handleResume(
                            stepId
                          )
                        }
                        className="
                          flex
                          items-center
                          justify-center
                          gap-2
                          rounded-2xl
                          border
                          border-green-500/20
                          bg-green-500/10
                          hover:bg-green-500/20
                          transition-all
                          py-3
                          font-bold
                          text-green-300
                        "
                      >

                        <CheckCircle2
                          size={18}
                        />

                        Resume

                      </button>

                      {/* KILL */}

                      <button
                        onClick={() =>
                          handleKill(
                            stepId
                          )
                        }
                        className="
                          flex
                          items-center
                          justify-center
                          gap-2
                          rounded-2xl
                          border
                          border-red-500/20
                          bg-red-500/10
                          hover:bg-red-500/20
                          transition-all
                          py-3
                          font-bold
                          text-red-300
                        "
                      >

                        <AlertTriangle
                          size={18}
                        />

                        Kill

                      </button>

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