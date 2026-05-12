"use client"

import { useEffect, useState } from "react"

import { useRouter } from "next/navigation"

import { getToken } from "@/lib/auth"

import SectionHeader from "@/components/ui/SectionHeader"

import LiveIndicator from "@/components/ui/LiveIndicator"

import StatusBadge from "@/components/ui/StatusBadge"

import TimelineEvent from "@/components/ui/TimelineEvent"

const API_URL = process.env.NEXT_PUBLIC_API_URL

export default function UsageLogsPage() {

  const router = useRouter()

  const [logs, setLogs] =
    useState<any[]>([])

  const [loading, setLoading] =
    useState(true)

  useEffect(() => {

    const token = getToken()

    if (!token) {
      window.location.href = "/login"
      return
    }

    async function loadLogs() {

      try {

        const response = await fetch(
          `${API_URL}/dashboard/usage/logs`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        )

        const data = await response.json()

        console.log(data)

        setLogs(
          Array.isArray(data)
            ? data
            : []
        )

      } catch (err) {

        console.error(err)

      } finally {

        setLoading(false)

      }
    }

    loadLogs()

  }, [])

  if (loading) {
    return (
      <div className="
        min-h-screen
        bg-black
        text-white
        flex
        items-center
        justify-center
        text-3xl
        font-black
      ">
        Loading Usage Logs...
      </div>
    )
  }

  return (
    <div className="
      min-h-screen
      bg-gradient-to-br
      from-slate-950
      via-slate-900
      to-black
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
            title="Usage Telemetry"
            subtitle="Real-time AI activity stream."
          />

        </div>

        <div className="
          flex
          items-center
          gap-4
        ">

          <LiveIndicator />

          <button
            onClick={() =>
              router.push("/dashboard")
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
            Back To Dashboard
          </button>

        </div>

      </div>

      {/* TELEMETRY FEED */}
      <div className="space-y-6">

        {logs.map(
          (log: any, index: number) => (

            <div
              key={index}
              className="
                bg-[#091121]
                border
                border-cyan-500/20
                rounded-3xl
                p-6
              "
            >

              <div className="
                flex
                items-center
                justify-between
                mb-5
              ">

                <div>

                  <h2 className="
                    text-2xl
                    font-bold
                    text-cyan-400
                  ">
                    {log.action}
                  </h2>

                  <p className="
                    mt-2
                    text-gray-500
                    text-sm
                  ">
                    Step ID:
                    {" "}
                    {log.step_id}
                  </p>

                </div>

                <StatusBadge
                  status={
                    log.status ||
                    "running"
                  }
                />

              </div>

              <TimelineEvent
                event={
                  log.event_type ||
                  "completed"
                }
                timestamp={
                  log.created_at ||
                  log.timestamp
                }
                cost={log.cost}
              />

              <div className="
                mt-6
                grid
                grid-cols-1
                md:grid-cols-2
                gap-4
              ">

                <div className="
                  rounded-2xl
                  bg-black/30
                  p-4
                ">

                  <p className="
                    text-sm
                    text-gray-400
                  ">
                    Agent ID
                  </p>

                  <h3 className="
                    mt-2
                    text-sm
                    break-all
                  ">
                    {log.agent_id}
                  </h3>

                </div>

                <div className="
                  rounded-2xl
                  bg-black/30
                  p-4
                ">

                  <p className="
                    text-sm
                    text-gray-400
                  ">
                    Log ID
                  </p>

                  <h3 className="
                    mt-2
                    text-sm
                    break-all
                  ">
                    {log.id}
                  </h3>

                </div>

              </div>

            </div>

          )
        )}

      </div>

    </div>
  )
}