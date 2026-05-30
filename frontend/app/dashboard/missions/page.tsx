"use client"

import { useEffect, useState } from "react"

import { useRouter } from "next/navigation"

import {
  getMissionList,
  retryMission,
  killMission,
  resumeMission,
  getMissionOverview,
} from "@/components/api"

import { auth } from "@/lib/auth"

import { toast } from "sonner"

import {
  Rocket,
  RotateCcw,
  Play,
  Square,
  Eye,
  Activity,
  ShieldCheck,
  AlertTriangle,
} from "lucide-react"

import StatusBadge from "@/components/ui/StatusBadge"

import SectionHeader from "@/components/ui/SectionHeader"

import LiveIndicator from "@/components/ui/LiveIndicator"

export default function MissionsPage() {

  const router =
    useRouter()

  const [missions, setMissions] =
    useState<any[]>([])

  const [overview, setOverview] =
    useState<any>(null)

  const [loading, setLoading] =
    useState(true)

  async function loadData() {

    try {

      const [
        missionData,
        overviewData,
      ] = await Promise.all([
        getMissionList(),
        getMissionOverview(),
      ])

      setMissions(
        Array.isArray(
          missionData
        )
          ? missionData
          : []
      )

      setOverview(
        overviewData
      )

    } catch (err) {

      console.error(err)

      toast.error(
        err instanceof Error
          ? err.message
          : "Failed to load missions"
      )

    } finally {

      setLoading(false)
    }
  }

  useEffect(() => {

    if (!auth.getToken()) {

      router.push("/login")

      return
    }

    loadData()

  }, [router])

  async function handleRetry(
    missionId: string
  ) {

    try {

      const response =
        await retryMission(
          missionId
        )

      toast.success(
        response?.message ||
        "Mission retried"
      )

      loadData()

    } catch (err) {

      toast.error(
        err instanceof Error
          ? err.message
          : "Retry failed"
      )
    }
  }

  async function handleKill(
    missionId: string
  ) {

    try {

      const response =
        await killMission(
          missionId
        )

      toast.success(
        response?.message ||
        "Mission killed"
      )

      loadData()

    } catch (err) {

      toast.error(
        err instanceof Error
          ? err.message
          : "Kill failed"
      )
    }
  }

  async function handleResume(
    missionId: string
  ) {

    try {

      const response =
        await resumeMission(
          missionId
        )

      toast.success(
        response?.message ||
        "Mission resumed"
      )

      loadData()

    } catch (err) {

      toast.error(
        err instanceof Error
          ? err.message
          : "Resume failed"
      )
    }
  }

  if (loading) {

    return (

      <div
        className="
          min-h-screen
          bg-[#050816]
          text-cyan-300
          flex
          items-center
          justify-center
        "
      >
        Loading missions...
      </div>
    )
  }

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
          flex-wrap
          gap-5
          mb-10
        "
      >

        <SectionHeader
          title="Mission Runtime"
          subtitle="
            Autonomous AI mission
            execution and telemetry.
          "
        />

        <LiveIndicator />

      </div>

      {/* METRICS */}

      <div
        className="
          grid
          grid-cols-1
          md:grid-cols-4
          gap-6
          mb-10
        "
      >

        {/* TOTAL */}

        <div
          className="
            rounded-3xl
            border
            border-cyan-500/20
            bg-cyan-500/10
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

              <p className="text-slate-400">
                Total Missions
              </p>

              <h2
                className="
                  mt-3
                  text-5xl
                  font-black
                  text-cyan-300
                "
              >
                {
                  overview?.total_missions || 0
                }
              </h2>

            </div>

            <Rocket
              className="
                text-cyan-300
              "
              size={34}
            />

          </div>

        </div>

        {/* RUNNING */}

        <div
          className="
            rounded-3xl
            border
            border-purple-500/20
            bg-purple-500/10
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

              <p className="text-slate-400">
                Running
              </p>

              <h2
                className="
                  mt-3
                  text-5xl
                  font-black
                  text-purple-300
                "
              >
                {
                  overview?.running || 0
                }
              </h2>

            </div>

            <Activity
              className="
                text-purple-300
              "
              size={34}
            />

          </div>

        </div>

        {/* COMPLETED */}

        <div
          className="
            rounded-3xl
            border
            border-green-500/20
            bg-green-500/10
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

              <p className="text-slate-400">
                Completed
              </p>

              <h2
                className="
                  mt-3
                  text-5xl
                  font-black
                  text-green-300
                "
              >
                {
                  overview?.completed || 0
                }
              </h2>

            </div>

            <ShieldCheck
              className="
                text-green-300
              "
              size={34}
            />

          </div>

        </div>

        {/* FAILED */}

        <div
          className="
            rounded-3xl
            border
            border-red-500/20
            bg-red-500/10
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

              <p className="text-slate-400">
                Failed
              </p>

              <h2
                className="
                  mt-3
                  text-5xl
                  font-black
                  text-red-300
                "
              >
                {
                  overview?.failed || 0
                }
              </h2>

            </div>

            <AlertTriangle
              className="
                text-red-300
              "
              size={34}
            />

          </div>

        </div>

      </div>

      {/* MISSIONS */}

      <div className="space-y-8">

        {missions.map((mission) => (

          <div
            key={mission.mission_id}
            className="
              rounded-3xl
              border
              border-cyan-500/20
              bg-[#091121]
              p-8
            "
          >

            {/* TOP */}

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

                <h2
                  className="
                    text-3xl
                    font-black
                  "
                >
                  {
                    mission.task_name ||
                    "Untitled Mission"
                  }
                </h2>

                <p
                  className="
                    mt-3
                    text-slate-400
                    break-all
                  "
                >
                  {
                    mission.mission_id
                  }
                </p>

              </div>

              <StatusBadge
                status={
                  mission.status ||
                  "unknown"
                }
              />

              {mission.is_retry && (
                <p className="text-orange-400
                text-sm mt-2">
                  🔄 Retry Mission
                </p>
              )}

            </div>

            {/* SMALL STATS */}

            <div
              className="
                grid
                grid-cols-1
                md:grid-cols-3
                gap-5
                mt-8
              "
            >

              <div
                className="
                  rounded-2xl
                  bg-black/30
                  p-5
                "
              >

                <p className="text-slate-400">
                  Retry Count
                </p>

                <h2
                  className="
                    mt-2
                    text-3xl
                    font-black
                    text-green-400
                  "
                >
                  {
                    mission.retry_count || 0
                  }
                </h2>

              </div>

              <div
                className="
                  rounded-2xl
                  bg-black/30
                  p-5
                "
              >

                <p className="text-slate-400">
                  Cache Hit
                </p>

                <h2
                  className="
                    mt-2
                    text-3xl
                    font-black
                    text-yellow-400
                  "
                >
                  {
                    mission.cache_hit
                      ? "YES"
                      : "NO"
                  }
                </h2>

              </div>

              <div
                className="
                  rounded-2xl
                  bg-black/30
                  p-5
                "
              >

                <p className="text-slate-400">
                  Created At
                </p>

                <h2
                  className="
                    mt-2
                    text-sm
                    font-bold
                    text-cyan-300
                  "
                >
                  {
                    mission.created_at
                      ? new Date(
                          mission.created_at
                        ).toLocaleString()
                      : "N/A"
                  }
                </h2>

              </div>

            </div>

            {/* ACTIONS */}

            <div
              className="
                flex
                items-center
                gap-4
                flex-wrap
                mt-8
              "
            >

              {/* VIEW */}

              <button
                onClick={() =>
                  router.push(
                    `/dashboard/missions/${mission.mission_id}`
                  )
                }
                className="
                  flex
                  items-center
                  gap-2
                  px-5
                  py-3
                  rounded-2xl
                  bg-cyan-500/10
                  border
                  border-cyan-500/20
                  hover:bg-cyan-500
                  hover:text-black
                  transition-all
                  font-bold
                "
              >

                <Eye size={18} />

                View Mission

              </button>

              {/* RETRY */}

              <button
                onClick={() =>
                  handleRetry(
                    mission.mission_id
                  )
                }
                className="
                  flex
                  items-center
                  gap-2
                  px-5
                  py-3
                  rounded-2xl
                  bg-green-500/10
                  border
                  border-green-500/20
                  hover:bg-green-500
                  hover:text-black
                  transition-all
                  font-bold
                "
              >

                <RotateCcw size={18} />

                Retry

              </button>

              {/* KILL */}

              <button
                onClick={() =>
                  handleKill(
                    mission.mission_id
                  )
                }
                className="
                  flex
                  items-center
                  gap-2
                  px-5
                  py-3
                  rounded-2xl
                  bg-red-500/10
                  border
                  border-red-500/20
                  hover:bg-red-500
                  hover:text-black
                  transition-all
                  font-bold
                "
              >

                <Square size={18} />

                Kill

              </button>

              {/* RESUME */}

              <button
                onClick={() =>
                  handleResume(
                    mission.mission_id
                  )
                }
                className="
                  flex
                  items-center
                  gap-2
                  px-5
                  py-3
                  rounded-2xl
                  bg-yellow-500/10
                  border
                  border-yellow-500/20
                  hover:bg-yellow-500
                  hover:text-black
                  transition-all
                  font-bold
                "
              >

                <Play size={18} />

                Resume

              </button>

            </div>

          </div>
        ))}

      </div>

    </div>
  )
}