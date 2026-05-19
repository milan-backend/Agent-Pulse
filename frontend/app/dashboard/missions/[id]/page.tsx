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

export default function MissionPage() {

  // =========================
  // ROUTER
  // =========================

  const router =
    useRouter()

  const params =
    useParams()

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
  // LOAD
  // =========================

  useEffect(() => {

    async function loadMission() {

      try {

        if (
          !auth.getToken()
        ) {

          router.push(
            "/login"
          )

          return
        }

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

  }, [
    stepId,
    router,
  ])

  // =========================
  // LOADING
  // =========================

  if (loading) {

    return (

      <div
        className="
          min-h-screen
          bg-black
          text-white
          flex
          items-center
          justify-center
        "
      >
        Loading Mission...
      </div>
    )
  }

  // =========================
  // NO DATA
  // =========================

  if (!mission) {

    return (

      <div
        className="
          min-h-screen
          bg-black
          text-red-400
          flex
          items-center
          justify-center
        "
      >
        Mission Not Found
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
        p-10
      "
    >

      {/* HEADER */}

      <div className="mb-10">

        <h1
          className="
            text-5xl
            font-black
          "
        >
          {mission.task_name}
        </h1>

        <p
          className="
            mt-4
            text-slate-400
          "
        >
          Runtime mission telemetry
          and execution analytics.
        </p>

      </div>

      {/* GRID */}

      <div
        className="
          grid
          grid-cols-1
          md:grid-cols-2
          gap-6
        "
      >

        {/* STATUS */}

        <div
          className="
            rounded-3xl
            border
            border-cyan-500/20
            bg-cyan-500/10
            p-6
          "
        >

          <p className="text-slate-400">
            Status
          </p>

          <h2
            className="
              mt-3
              text-4xl
              font-black
              text-cyan-300
            "
          >
            {mission.status}
          </h2>

        </div>

        {/* RETRIES */}

        <div
          className="
            rounded-3xl
            border
            border-green-500/20
            bg-green-500/10
            p-6
          "
        >

          <p className="text-slate-400">
            Retry Count
          </p>

          <h2
            className="
              mt-3
              text-4xl
              font-black
              text-green-300
            "
          >
            {mission.retry_count || 0}
          </h2>

        </div>

        {/* CACHE */}

        <div
          className="
            rounded-3xl
            border
            border-yellow-500/20
            bg-yellow-500/10
            p-6
          "
        >

          <p className="text-slate-400">
            Cache Hit
          </p>

          <h2
            className="
              mt-3
              text-4xl
              font-black
              text-yellow-300
            "
          >
            {mission.cache_hit
              ? "YES"
              : "NO"}
          </h2>

        </div>

        {/* RUNTIME */}

        <div
          className="
            rounded-3xl
            border
            border-purple-500/20
            bg-purple-500/10
            p-6
          "
        >

          <p className="text-slate-400">
            Runtime Controlled
          </p>

          <h2
            className="
              mt-3
              text-4xl
              font-black
              text-purple-300
            "
          >
            {mission.runtime_controlled
              ? "YES"
              : "NO"}
          </h2>

        </div>

      </div>

      {/* DETAILS */}

      <div
        className="
          mt-10
          rounded-3xl
          border
          border-white/10
          bg-white/[0.03]
          p-8
        "
      >

        <h2
          className="
            text-3xl
            font-black
            mb-8
          "
        >
          Mission Details
        </h2>

        <div className="space-y-5">

          <div>
            <p className="text-slate-400">
              Mission ID
            </p>

            <p className="mt-2 break-all">
              {mission.id}
            </p>
          </div>

          <div>
            <p className="text-slate-400">
              Agent ID
            </p>

            <p className="mt-2 break-all">
              {mission.agent_id}
            </p>
          </div>

          <div>
            <p className="text-slate-400">
              Created At
            </p>

            <p className="mt-2">
              {mission.created_at}
            </p>
          </div>

          <div>
            <p className="text-slate-400">
              Updated At
            </p>

            <p className="mt-2">
              {mission.updated_at}
            </p>
          </div>

          <div>
            <p className="text-slate-400">
              Error Message
            </p>

            <pre
              className="
                mt-2
                overflow-auto
                rounded-2xl
                bg-black/40
                p-5
                text-red-300
              "
            >
              {mission.error_message ||
                "No errors"}
            </pre>
          </div>

        </div>
      </div>

    </div>
  )
}