"use client"

import { useEffect, useState } from "react"

import { useParams } from "next/navigation"

import {
  fetchDashboardSteps,
  fetchUsageLogs,
} from "@/components/api"

import {
  getToken,
  logout,
} from "@/lib/auth"

export default function AgentDetailPage() {

  const params = useParams()

  const id = params.id as string

  const [steps, setSteps] =
    useState<any[]>([])

  const [logs, setLogs] =
    useState<any[]>([])

  const [loading, setLoading] =
    useState(true)

  useEffect(() => {

    const token = getToken()

    if (!token) {
      window.location.href =
        "/login"
      return
    }

    async function loadAgent() {

      try {

        const stepsData =
          await fetchDashboardSteps(
            token as string
          )

        const logsData =
          await fetchUsageLogs(
            token as string
          )

        const filteredSteps =
          Array.isArray(stepsData)
            ? stepsData.filter(
                (s: any) =>
                  s.agent_id === id
              )
            : []

        const filteredLogs =
          Array.isArray(logsData)
            ? logsData.filter(
                (l: any) =>
                  l.agent_id === id
              )
            : []

        setSteps(filteredSteps)

        setLogs(filteredLogs)

        setLoading(false)

      } catch {

        logout()

        window.location.href =
          "/login"
      }
    }

    loadAgent()

  }, [id])

  if (loading) {
    return (
      <div className="
        min-h-screen
        bg-black
        text-white
        flex
        items-center
        justify-center
        text-4xl
        font-black
      ">
        Loading Agent...
      </div>
    )
  }

  return (
    <div className="
      min-h-screen
      bg-black
      text-white
      p-8
    ">

      <div className="
        flex
        items-center
        justify-between
      ">

        <div>

          <h1 className="
            text-5xl
            font-black
          ">
            Agent Detail
          </h1>

          <p className="
            text-gray-400
            mt-3
          ">
            Real-time agent monitoring.
          </p>

        </div>

        <button
          onClick={() =>
            window.location.href =
              "/dashboard"
          }
          className="
            px-6
            py-3
            rounded-2xl
            bg-cyan-500/20
            border
            border-cyan-400/30
            text-cyan-300
            font-bold
          "
        >
          Back Dashboard
        </button>

      </div>

      <div className="
        mt-10
        grid
        grid-cols-1
        md:grid-cols-3
        gap-6
      ">

        <div className="
          rounded-3xl
          border
          border-white/10
          bg-white/5
          p-6
        ">

          <p className="
            text-gray-400
          ">
            Agent ID
          </p>

          <h2 className="
            mt-4
            text-xl
            font-bold
            break-all
          ">
            {id}
          </h2>

        </div>

        <div className="
          rounded-3xl
          border
          border-green-400/20
          bg-green-500/10
          p-6
        ">

          <p className="
            text-green-300
          ">
            Total Steps
          </p>

          <h2 className="
            mt-4
            text-5xl
            font-black
          ">
            {steps.length}
          </h2>

        </div>

        <div className="
          rounded-3xl
          border
          border-cyan-400/20
          bg-cyan-500/10
          p-6
        ">

          <p className="
            text-cyan-300
          ">
            Usage Logs
          </p>

          <h2 className="
            mt-4
            text-5xl
            font-black
          ">
            {logs.length}
          </h2>

        </div>

      </div>

      <div className="
        mt-10
        rounded-3xl
        border
        border-white/10
        bg-white/5
        p-8
      ">

        <h2 className="
          text-3xl
          font-black
        ">
          Execution Steps
        </h2>

        <div className="
          mt-6
          space-y-4
        ">

          {steps.map((step, index) => (

            <div
              key={index}
              className="
                rounded-2xl
                border
                border-white/10
                bg-black/30
                p-5
              "
            >

              <div className="
                flex
                items-center
                justify-between
              ">

                <div>

                  <h3 className="
                    text-xl
                    font-bold
                  ">
                    {step.task || "Mission"}
                  </h3>

                  <p className="
                    text-gray-400
                    mt-2
                  ">
                    Status:
                    {" "}
                    {step.status}
                  </p>

                </div>

                <div className="
                  text-right
                ">

                  <p className="
                    text-gray-400
                  ">
                    Retries
                  </p>

                  <h3 className="
                    text-3xl
                    font-black
                  ">
                    {step.retry_count || 0}
                  </h3>

                </div>

              </div>

            </div>

          ))}

        </div>

      </div>

      <div className="
        mt-10
        rounded-3xl
        border
        border-white/10
        bg-white/5
        p-8
      ">

        <h2 className="
          text-3xl
          font-black
        ">
          Usage Activity
        </h2>

        <div className="
          mt-6
          space-y-4
        ">

          {logs.map((log, index) => (

            <div
              key={index}
              className="
                rounded-2xl
                border
                border-white/10
                bg-black/30
                p-5
              "
            >

              <div className="
                flex
                items-center
                justify-between
              ">

                <div>

                  <h3 className="
                    text-xl
                    font-bold
                  ">
                    {log.event_type}
                  </h3>

                  <p className="
                    text-gray-400
                    mt-2
                  ">
                    Step:
                    {" "}
                    {log.step_id}
                  </p>

                </div>

                <div className="
                  text-cyan-300
                  font-bold
                ">
                  {log.timestamp}
                </div>

              </div>

            </div>

          ))}

        </div>

      </div>

    </div>
  )
}