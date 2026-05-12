"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"

import { fetchStepById } from "@/components/api"
import { getToken } from "@/lib/auth"

import TimelineEvent from "@/components/ui/TimelineEvent"

import SectionHeader from "@/components/ui/SectionHeader"

import LiveIndicator from "@/components/ui/LiveIndicator"

import StatusBadge from "@/components/ui/StatusBadge"

const API_URL = process.env.NEXT_PUBLIC_API_KEY

export default function MissionDetailPage() {

  const router = useRouter()

  const params = useParams()

  const stepId = params.id as string

  const [mission, setMission] =
    useState<any>(null)

  const [loading, setLoading] =
    useState(true)

  useEffect(() => {

    const loadStep = async () => {

      try {

        const token = getToken()

        if (!token) {
          window.location.href = "/login"
          return
        }

        const data =
          await fetchStepById(
            stepId,
            token
          )

        setMission(data)

      } catch (err) {

        console.error(err)

      } finally {

        setLoading(false)

      }
    }

    if (stepId) {
      loadStep()
    }

  }, [stepId])

  if (loading) {

    return (

      <div className="
        min-h-screen
        bg-black
        text-cyan-400
        p-10
      ">
        Loading mission...
      </div>

    )
  }

  if (!mission) {

    return (

      <div className="
        min-h-screen
        bg-black
        text-red-400
        p-10
      ">
        Failed to load mission.
      </div>

    )
  }

  return (

    <div className="
      min-h-screen
      bg-[#050816]
      text-white
      p-8
    ">

      {/* HEADER */}
      <div className="
        flex
        items-center
        justify-between
        mb-10
      ">

        <div>

          <SectionHeader
            title="Mission Trace"
            subtitle="Deep execution observability."
          />

        </div>

        <div className="
          flex
          items-center
          gap-4
        ">

          <LiveIndicator />

          <button
            onClick={() => router.push("/dashboard")}
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
            Back To Dashboard
          </button>

        </div>

      </div>

      {/* TOP STATS */}
      <div className="
        grid
        grid-cols-4
        gap-6
        mb-8
      ">

        <div className="
          bg-[#091121]
          border
          border-cyan-500/20
          rounded-3xl
          p-6
        ">

          <p className="
            text-gray-400
            mb-2
          ">
            Status
          </p>

          <h2 className="
            text-3xl
            font-bold
            text-cyan-400
          ">
            <StatusBadge
              status={mission.status}
            />
          </h2>

        </div>

        <div className="
          bg-[#091121]
          border
          border-green-500/20
          rounded-3xl
          p-6
        ">

          <p className="
            text-gray-400
            mb-2
          ">
            Retries
          </p>

          <h2 className="
            text-3xl
            font-bold
            text-green-400
          ">
            {mission.retry_count}
          </h2>

        </div>

        <div className="
          bg-[#091121]
          border
          border-yellow-500/20
          rounded-3xl
          p-6
        ">

          <p className="
            text-gray-400
            mb-2
          ">
            Total Cost
          </p>

          <h2 className="
            text-3xl
            font-bold
            text-yellow-400
          ">
            ${mission.analytics.total_cost}
          </h2>

        </div>

        <div className="
          bg-[#091121]
          border
          border-pink-500/20
          rounded-3xl
          p-6
        ">

          <p className="
            text-gray-400
            mb-2
          ">
            Usage Events
          </p>

          <h2 className="
            text-3xl
            font-bold
            text-pink-400
          ">
            {mission.analytics.usage_events}
          </h2>

        </div>

      </div>

      {/* TOKEN SECTION */}
      <div className="
        bg-[#091121]
        border
        border-cyan-500/20
        rounded-3xl
        p-8
        mb-8
      ">

        <div className="
          flex
          items-center
          justify-between
          mb-6
        ">

          <div>

            <h2 className="
              text-4xl
              font-bold
              text-cyan-400
            ">
              Token Intelligence
            </h2>

            <p className="
              text-gray-400
              mt-2
            ">
              Runtime token observability.
            </p>

          </div>

          <LiveIndicator />

        </div>

        <div className="
          grid
          grid-cols-2
          gap-6
        ">

          <div className="
            bg-black/30
            rounded-2xl
            p-6
          ">

            <p className="
              text-gray-400
              mb-2
            ">
              Prompt Tokens
            </p>

            <h2 className="
              text-5xl
              font-bold
              text-cyan-400
            ">
              {mission.analytics.prompt_tokens}
            </h2>

          </div>

          <div className="
            bg-black/30
            rounded-2xl
            p-6
          ">

            <p className="
              text-gray-400
              mb-2
            ">
              Completion Tokens
            </p>

            <h2 className="
              text-5xl
              font-bold
              text-yellow-400
            ">
              {mission.analytics.completion_tokens}
            </h2>

          </div>

        </div>

      </div>

      {/* ACTIVITY TIMELINE */}
      <div className="
        bg-[#091121]
        border
        border-cyan-500/20
        rounded-3xl
        p-8
      ">

        <div className="
          flex
          items-center
          justify-between
          mb-8
        ">

          <SectionHeader
            title="Execution Timeline"
            subtitle="Real-time execution telemetry."
          />

          <LiveIndicator />

        </div>

        <div className="space-y-6">

          {mission.usage_logs.map(
            (log: any, index: number) => (

              <TimelineEvent
                key={index}
                event={
                  log.event_type ||
                  "completed"
                }
                timestamp={log.timestamp}
                cost={log.cost}
              />

            )
          )}

        </div>

      </div>

    </div>
  )
}