"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"

import {
  fetchDashboardSteps,
} from "@/components/api"

import { getToken } from "@/lib/auth"

export default function StepsPage() {

  const router = useRouter()

  const [steps, setSteps] =
    useState<any[]>([])

  const [loading, setLoading] =
    useState(true)

  useEffect(() => {

    const token = getToken()

    if (!token) {
      window.location.href = "/login"
      return
    }

    async function loadSteps() {

      try {

        const data =
          await fetchDashboardSteps(
            token as string
          )

        setSteps(
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

    loadSteps()

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
        Loading Missions...
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
            Missions
          </h1>

          <p className="
            mt-2
            text-gray-400
          ">
            Real-time agent execution monitoring.
          </p>

        </div>

        <button
          onClick={() =>
            window.location.href =
              "/dashboard"
          }
          className="
            px-5
            py-3
            rounded-2xl
            bg-cyan-500/20
            border
            border-cyan-400/30
            hover:bg-cyan-500/30
            transition
          "
        >
          Back Dashboard
        </button>

      </div>

      <div className="
        mt-10
        overflow-x-auto
        rounded-3xl
        border
        border-white/10
        bg-white/5
        backdrop-blur-xl
      ">

        <table className="
          w-full
          text-left
        ">

          <thead className="
            bg-white/10
          ">

            <tr>

              <th className="p-5">
                Task
              </th>

              <th className="p-5">
                Status
              </th>

              <th className="p-5">
                Agent
              </th>

              <th className="p-5">
                Retries
              </th>

              <th className="p-5">
                Cache
              </th>

            </tr>

          </thead>

          <tbody>

            {steps.map((step) => (

              <tr
                key={step.id}
                onClick={() =>
                  router.push(
                    `/dashboard/missions/${step.id}`
                  )
                }
                className="
                  border-t
                  border-white/10
                  hover:bg-cyan-500/10
                  cursor-pointer
                  transition-all
                  duration-200
                "
              >

                <td className="p-5">
                  {step.task_name}
                </td>

                <td className="p-5">

                  <span className="
                    px-3
                    py-1
                    rounded-full
                    text-sm
                    bg-cyan-500/20
                    text-cyan-300
                  ">
                    {step.status}
                  </span>

                </td>

                <td className="
                  p-5
                  text-gray-400
                  text-sm
                ">
                  {step.agent_id}
                </td>

                <td className="p-5">
                  {step.retry_count}
                </td>

                <td className="p-5">
                  {step.cache_key
                    ? "Cached"
                    : "No Cache"}
                </td>

              </tr>

            ))}

          </tbody>

        </table>

      </div>

    </div>
  )
}