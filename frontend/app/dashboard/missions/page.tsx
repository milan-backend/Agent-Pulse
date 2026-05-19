"use client"

import { useEffect, useState } from "react"

import {
  useParams,
  useRouter,
} from "next/navigation"

import {
  fetchMissionById,
} from "@/components/api"

import {
  auth,
} from "@/lib/auth"

import TimelineEvent from "@/components/ui/TimelineEvent"

import SectionHeader from "@/components/ui/SectionHeader"

import LiveIndicator from "@/components/ui/LiveIndicator"

import StatusBadge from "@/components/ui/StatusBadge"

import {
  ShieldCheck,
  Cpu,
  Database,
  AlertTriangle,
} from "lucide-react"

export default function MissionDetailPage() {

  // =========================
  // ROUTER
  // =========================

  const router = useRouter()

  const params = useParams()

  const stepId =
    params.id as string

  // =========================
  // STATE
  // =========================

  const [mission, setMission] =
    useState<any>(null)

  const [loading, setLoading] =
    useState(true)

  // =========================
  // LOAD MISSION
  // =========================

  useEffect(() => {

    const loadMission = async () => {

      try {

        if (!auth.getToken()) {

          window.location.href =
            "/login"

          return
        }

        // FETCH MISSION

        const data =
          await fetchMissionById(
            stepId
          )

        setMission(data)

      } catch (err) {

        console.error(err)

      } finally {

        setLoading(false)
      }
    }

    if (stepId) {

      loadMission()
    }

  }, [stepId])

  // =========================
  // LOADING
  // =========================

  if (loading) {

    return (

      <div
        className="
          min-h-screen
          bg-black
          text-cyan-400
          p-10
        "
      >
        Loading mission...
      </div>
    )
  }

  // =========================
  // ERROR
  // =========================

  if (!mission) {

    return (

      <div
        className="
          min-h-screen
          bg-black
          text-red-400
          p-10
        "
      >
        Failed to load mission.
      </div>
    )
  }

  // =========================
  // PAGE
  // =========================

  return (

    <div
      className="
        min-h-screen
        bg-[#050816]
        text-white
        p-8
      "
    >

      {/* HEADER */}

      <div
        className="
          flex
          items-center
          justify-between
          mb-10
          flex-wrap
          gap-5
        "
      >

        <div>

          <SectionHeader
            title={
              mission.task_name ||
              "Mission Trace"
            }
            subtitle="
              Deep execution
              observability and
              runtime telemetry.
            "
          />

        </div>

        <div
          className="
            flex
            items-center
            gap-4
          "
        >

          <LiveIndicator />

          <button
            onClick={() =>
              router.push("/missions")
            }
            className="
              px-6
              py-3
              rounded-xl
              bg-gray-900
              border
              border-cyan-500
              hover:bg-cyan-500
              hover:text-black
              transition-all
              font-bold
            "
          >
            Back To Missions
          </button>

        </div>
      </div>

      {/* TOP STATS */}

      <div
        className="
          grid
          grid-cols-1
          md:grid-cols-2
          xl:grid-cols-4
          gap-6
          mb-8
        "
      >

        {/* STATUS */}

        <div
          className="
            bg-[#091121]
            border
            border-cyan-500/20
            rounded-3xl
            p-6
          "
        >

          <p
            className="
              text-gray-400
              mb-2
            "
          >
            Mission Status
          </p>

          <div className="mt-4">

            <StatusBadge
              status={mission.status}
            />

          </div>

        </div>

        {/* RETRIES */}

        <div
          className="
            bg-[#091121]
            border
            border-green-500/20
            rounded-3xl
            p-6
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

              <p
                className="
                  text-gray-400
                  mb-2
                "
              >
                Retry Count
              </p>

              <h2
                className="
                  text-4xl
                  font-bold
                  text-green-400
                "
              >
                {mission.retry_count || 0}
              </h2>

            </div>

            <ShieldCheck
              className="
                text-green-400
              "
              size={30}
            />

          </div>
        </div>

        {/* CACHE */}

        <div
          className="
            bg-[#091121]
            border
            border-yellow-500/20
            rounded-3xl
            p-6
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

              <p
                className="
                  text-gray-400
                  mb-2
                "
              >
                Cache Hit
              </p>

              <h2
                className="
                  text-4xl
                  font-bold
                  text-yellow-400
                "
              >
                {mission.cache_hit
                  ? "YES"
                  : "NO"}
              </h2>

            </div>

            <Database
              className="
                text-yellow-400
              "
              size={30}
            />

          </div>
        </div>

        {/* RUNTIME */}

        <div
          className="
            bg-[#091121]
            border
            border-pink-500/20
            rounded-3xl
            p-6
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

              <p
                className="
                  text-gray-400
                  mb-2
                "
              >
                Runtime Controlled
              </p>

              <h2
                className="
                  text-4xl
                  font-bold
                  text-pink-400
                "
              >
                {mission.runtime_controlled
                  ? "YES"
                  : "NO"}
              </h2>

            </div>

            <Cpu
              className="
                text-pink-400
              "
              size={30}
            />

          </div>
        </div>
      </div>

      {/* MISSION DETAILS */}

      <div
        className="
          bg-[#091121]
          border
          border-cyan-500/20
          rounded-3xl
          p-8
          mb-8
        "
      >

        <div
          className="
            flex
            items-center
            justify-between
            mb-8
            flex-wrap
            gap-5
          "
        >

          <SectionHeader
            title="Mission Runtime"
            subtitle="
              Full execution metadata
              and orchestration state.
            "
          />

          <LiveIndicator />

        </div>

        <div
          className="
            grid
            grid-cols-1
            xl:grid-cols-2
            gap-6
          "
        >

          {/* LEFT */}

          <div className="space-y-5">

            <div
              className="
                bg-black/30
                rounded-2xl
                p-6
              "
            >

              <p className="text-gray-400">
                Mission ID
              </p>

              <h2
                className="
                  mt-2
                  text-lg
                  font-bold
                  text-cyan-400
                  break-all
                "
              >
                {mission.id}
              </h2>

            </div>

            <div
              className="
                bg-black/30
                rounded-2xl
                p-6
              "
            >

              <p className="text-gray-400">
                Agent ID
              </p>

              <h2
                className="
                  mt-2
                  text-lg
                  font-bold
                  text-yellow-400
                  break-all
                "
              >
                {mission.agent_id}
              </h2>

            </div>

            <div
              className="
                bg-black/30
                rounded-2xl
                p-6
              "
            >

              <p className="text-gray-400">
                Event Type
              </p>

              <h2
                className="
                  mt-2
                  text-lg
                  font-bold
                  text-purple-400
                "
              >
                {mission.event_type || "N/A"}
              </h2>

            </div>

            <div
              className="
                bg-black/30
                rounded-2xl
                p-6
              "
            >

              <p className="text-gray-400">
                Created At
              </p>

              <h2
                className="
                  mt-2
                  text-lg
                  font-bold
                  text-green-400
                "
              >
                {mission.created_at}
              </h2>

            </div>

            <div
              className="
                bg-black/30
                rounded-2xl
                p-6
              "
            >

              <p className="text-gray-400">
                Updated At
              </p>

              <h2
                className="
                  mt-2
                  text-lg
                  font-bold
                  text-cyan-400
                "
              >
                {mission.updated_at}
              </h2>

            </div>

          </div>

          {/* RIGHT */}

          <div className="space-y-5">

            <div
              className="
                bg-black/30
                rounded-2xl
                p-6
              "
            >

              <p className="text-gray-400">
                Started At
              </p>

              <h2
                className="
                  mt-2
                  text-lg
                  font-bold
                  text-cyan-400
                "
              >
                {mission.started_at || "N/A"}
              </h2>

            </div>

            <div
              className="
                bg-black/30
                rounded-2xl
                p-6
              "
            >

              <p className="text-gray-400">
                Paused At
              </p>

              <h2
                className="
                  mt-2
                  text-lg
                  font-bold
                  text-yellow-400
                "
              >
                {mission.paused_at || "N/A"}
              </h2>

            </div>

            <div
              className="
                bg-black/30
                rounded-2xl
                p-6
              "
            >

              <p className="text-gray-400">
                Resumed At
              </p>

              <h2
                className="
                  mt-2
                  text-lg
                  font-bold
                  text-green-400
                "
              >
                {mission.resumed_at || "N/A"}
              </h2>

            </div>

            <div
              className="
                bg-black/30
                rounded-2xl
                p-6
              "
            >

              <p className="text-gray-400">
                Killed At
              </p>

              <h2
                className="
                  mt-2
                  text-lg
                  font-bold
                  text-red-400
                "
              >
                {mission.killed_at || "N/A"}
              </h2>

            </div>

            <div
              className="
                bg-black/30
                rounded-2xl
                p-6
              "
            >

              <p className="text-gray-400">
                Pause Reason
              </p>

              <h2
                className="
                  mt-2
                  text-lg
                  font-bold
                  text-orange-400
                "
              >
                {mission.pause_reason || "N/A"}
              </h2>

            </div>

          </div>
        </div>
      </div>

      {/* INPUT / OUTPUT */}

      <div
        className="
          grid
          grid-cols-1
          xl:grid-cols-2
          gap-8
          mb-8
        "
      >

        {/* INPUT */}

        <div
          className="
            bg-[#091121]
            border
            border-cyan-500/20
            rounded-3xl
            p-8
          "
        >

          <div
            className="
              flex
              items-center
              justify-between
              mb-6
            "
          >

            <SectionHeader
              title="Input Data"
              subtitle="
                Mission execution input.
              "
            />

            <LiveIndicator />

          </div>

          <pre
            className="
              bg-black/40
              rounded-2xl
              p-6
              overflow-auto
              text-sm
              text-cyan-300
            "
          >
            {JSON.stringify(
              mission.input_data,
              null,
              2
            )}
          </pre>

        </div>

        {/* OUTPUT */}

        <div
          className="
            bg-[#091121]
            border
            border-green-500/20
            rounded-3xl
            p-8
          "
        >

          <div
            className="
              flex
              items-center
              justify-between
              mb-6
            "
          >

            <SectionHeader
              title="Output Data"
              subtitle="
                Mission execution output.
              "
            />

            <LiveIndicator />

          </div>

          <pre
            className="
              bg-black/40
              rounded-2xl
              p-6
              overflow-auto
              text-sm
              text-green-300
            "
          >
            {JSON.stringify(
              mission.output_data,
              null,
              2
            )}
          </pre>

        </div>
      </div>

      {/* ERROR */}

      {mission.error_message && (

        <div
          className="
            bg-[#091121]
            border
            border-red-500/20
            rounded-3xl
            p-8
            mb-8
          "
        >

          <div
            className="
              flex
              items-center
              gap-4
              mb-5
            "
          >

            <AlertTriangle
              className="
                text-red-400
              "
              size={30}
            />

            <h2
              className="
                text-3xl
                font-bold
                text-red-400
              "
            >
              Runtime Error
            </h2>

          </div>

          <pre
            className="
              bg-black/40
              rounded-2xl
              p-6
              overflow-auto
              text-sm
              text-red-300
            "
          >
            {mission.error_message}
          </pre>

        </div>
      )}

      {/* TIMELINE */}

      <div
        className="
          bg-[#091121]
          border
          border-cyan-500/20
          rounded-3xl
          p-8
        "
      >

        <div
          className="
            flex
            items-center
            justify-between
            mb-8
          "
        >

          <SectionHeader
            title="Execution Timeline"
            subtitle="
              Runtime execution
              lifecycle telemetry.
            "
          />

          <LiveIndicator />

        </div>

        <div className="space-y-6">

          <TimelineEvent
            event="created"
            timestamp={mission.created_at}
            cost={0}
          />

          {mission.started_at && (

            <TimelineEvent
              event="started"
              timestamp={mission.started_at}
              cost={0}
            />
          )}

          {mission.paused_at && (

            <TimelineEvent
              event="paused"
              timestamp={mission.paused_at}
              cost={0}
            />
          )}

          {mission.resumed_at && (

            <TimelineEvent
              event="resumed"
              timestamp={mission.resumed_at}
              cost={0}
            />
          )}

          {mission.killed_at && (

            <TimelineEvent
              event="killed"
              timestamp={mission.killed_at}
              cost={0}
            />
          )}

          {mission.updated_at && (

            <TimelineEvent
              event={
                mission.status ||
                "updated"
              }
              timestamp={mission.updated_at}
              cost={0}
            />
          )}

        </div>
      </div>

    </div>
  )
}