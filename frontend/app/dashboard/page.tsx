"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"

import {
  fetchDashboardSummary,
  fetchDashboardUsage,
  fetchDashboardSteps,
  fetchUsageLogs,
} from "@/components/api"

import MissionTable from "@/components/MissionTable"
import StepTimeline from "@/components/StepTimeline"
import UsageCharts from "@/components/UsageCharts"
import LiveFeed from "@/components/LiveFeed"
import LiveStatus from "@/components/LiveStatus"

import MetricCard from "@/components/ui/MetricCard"

import SectionHeader from "@/components/ui/SectionHeader"

import LiveIndicator from "@/components/ui/LiveIndicator"

import { getToken, logout } from "@/lib/auth"
import { connected } from "process"

export default function DashboardPage() {

  const router = useRouter()

  const [summary, setSummary] =
    useState<any>({})

  const [usage, setUsage] =
    useState<any>({})

  const [steps, setSteps] =
    useState<any[]>([])

  const [logs, setLogs] =
    useState<any[]>([])

  const [loading, setLoading] =
    useState(true)

  const [liveUpdates, setLiveUpdates] =
    useState<any[]>([])

  const [wsConnected, setWsConnected] =
    useState(false)

  async function loadDashboard(token: string) {

    try {

      const summaryData =
        await fetchDashboardSummary(
          token as string
        )

      console.log(
        "Dashboard Summary:",
        summaryData
      )

      const usageData =
        await fetchDashboardUsage(
          token as string
        )

      const stepsData =
        await fetchDashboardSteps(
          token as string
        )

      const logsData =
        await fetchUsageLogs(
          token as string
        )

      setSummary(summaryData)

      setUsage(usageData)

      setSteps(
        Array.isArray(stepsData)
          ? stepsData
          : []
      )

      setLogs(
        Array.isArray(logsData)
          ? logsData
          : []
      )

      setLoading(false)

    } catch (err) {

      console.error(err)

      logout()

      window.location.href =
        "/login"
    }
  }

  useEffect(() => {

    const token = getToken()

    if (!token) {

      window.location.href = "/login"

      return
    }

    loadDashboard(token)

    const protocol =
      window.location.protocol === "https:"
        ? "wss:"
        : "ws:"

    const ws = new WebSocket(
      process.env.NEXT_PUBLIC_WS_URL!
    )

    ws.onopen = () => {

      console.log(
        "WebSocket Connected"
      )
      setWsConnected(true)
    }

    ws.onmessage = (event) => {

      try {

        const data = JSON.parse(
          event.data
        )

        console.log(
          "Live Update:",
          data
        )

        setLiveUpdates((prev) => [

          data,

          ...prev.slice(0, 9)

        ]) 
        loadDashboard(token)

        

      } catch (err) {

        console.log(
          "WebSocket Parse Error:",
          err
        )
      }
    }

    ws.onerror = (error) => {

      console.log(
        "WebSocket Error:",
        error
      )
    }

    ws.onclose = () => {
      setWsConnected(false)

      console.log(
        "WebSocket Disconnected"
      )
      
    }

    return () => {

      ws.close()
    }

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
        Loading Dashboard...
      </div>
    )
  }

  return (

    <div className="
      min-h-screen
      bg-black
      text-white
      relative
      overflow-hidden
    ">

      {/* Matrix Background */}
      <div className="
        absolute
        inset-0
        opacity-20
      ">
        <div className="
          matrix-bg
          h-full
          w-full
        " />
      </div>

      {/* Overlay */}
      <div className="
        absolute
        inset-0
        bg-gradient-to-br
        from-slate-950
        via-slate-900
        to-black
      " />

      <div className="
        relative
        z-10
        flex
      ">

        {/* Sidebar */}
        <aside className="
          hidden
          md:flex
          w-72
          min-h-screen
          flex-col
          border-r
          border-white/10
          bg-white/5
          backdrop-blur-xl
          p-6
        ">

          <div>

            <h1 className="
              text-4xl
              font-black
              glow-text
              bg-gradient-to-r
              from-cyan-400
              to-purple-400
              bg-clip-text
              text-transparent
            ">
              AgentPulse
            </h1>

            <p className="
              mt-2
              text-sm
              text-gray-400
            ">
              AI Observability Platform
            </p>

          </div>

          <nav className="
            mt-10
            space-y-3
          ">

            <button
              onClick={() =>
                router.push("/dashboard")
              }
              className="
                w-full
                rounded-2xl
                bg-cyan-500/20
                border
                border-cyan-400/30
                p-4
                text-left
                font-semibold
              "
            >
              Dashboard
            </button>

            <button
              onClick={() =>
                window.location.href =
                "/dashboard/analytics"
              }
              className="
                w-full
                rounded-2xl
                bg-white/5
                border
                border-white/10
                p-4
                text-left
                hover:bg-white/10
                transition
              "
            >
              Analytics
            </button>

            <button
              onClick={() =>
                router.push("/dashboard/steps")
              }
              className="
                w-full
                rounded-2xl
                bg-white/5
                border
                border-white/10
                p-4
                text-left
                hover:bg-white/10
                transition
              "
            >
              Missions
            </button>

            <button
              onClick={() =>
                router.push(
                  "/dashboard/usage-logs"
                )
              }
              className="
                w-full
                rounded-2xl
                bg-white/5
                border
                border-white/10
                p-4
                text-left
                hover:bg-white/10
                transition
              "
            >
              Usage Logs
            </button>

            <button
              onClick={() =>
                router.push(
                  "/dashboard/settings"
                )
              }
              className="
                w-full
                rounded-2xl
                bg-white/5
                border
                border-white/10
                p-4
                text-left
                hover:bg-white/10
                transition
              "
            >
              Settings
            </button>

            <button
              onClick={() => {
                logout()
                window.location.href =
                  "/login"
              }}
              className="
                w-full
                rounded-2xl
                bg-red-500/20
                border
                border-red-400/30
                p-4
                text-left
                hover:bg-red-500/30
                transition
              "
            >
              Logout
            </button>

          </nav>

          <div className="
            mt-auto
            bg-green-500/10
            border
            border-green-400/20
            rounded-2xl
            p-5
          ">

            <p className="
              text-sm
              text-gray-300
            ">
              System Health
            </p>

            <h2 className="
              text-4xl
              font-black
              text-green-400
              mt-2
            ">
              99.9%
            </h2>

            <p className="
              text-xs
              text-gray-400
              mt-2
            ">
              All systems operational
            </p>

          </div>

        </aside>

        {/* Main */}
        <main className="
          flex-1
          p-6
          md:p-10
        ">

          {/* Header */}
          <div className="
            flex
            items-center
            justify-between
            mb-10
          ">

            <SectionHeader
              title="Mission Control"
              subtitle="AI runtime observability center."
            />

            <LiveIndicator />

          </div>

          <div className="mt-6">

            <LiveStatus connected={wsConnected} />

          </div>

          {/* Metrics */}
          <div className="
            mt-10
            grid
            grid-cols-1
            md:grid-cols-2
            xl:grid-cols-3
            gap-6
          ">

            <MetricCard
              title="Total Steps"
              value={summary.total_steps || 0}
              color="text-cyan-400"
              subtitle="Total AI executions"
            />

            <MetricCard
              title="Completed"
              value={summary.completed || 0}
              color="text-green-400"
              subtitle="Successful missions"
            />

            <MetricCard
              title="Failed"
              value={summary.failed || 0}
              color="text-red-400"
              subtitle="Execution failures"
            />

            <MetricCard
              title="Pending"
              value={summary.pending || 0}
              color="text-yellow-400"
              subtitle="Waiting executions"
            />

            <MetricCard
              title="Success Rate"
              value={`${summary.success_rate || 0}%`}
              color="text-pink-400"
              subtitle="Runtime reliability"
            />

          </div>

          {/* Charts */}
          <UsageCharts
            usage={usage}
          />

          {/* Missions */}
          <MissionTable
            steps={steps}
          />

          {/* Timeline */}
          <StepTimeline
            logs={logs}
          />

          {/* Live Feed */}
          <LiveFeed
            logs={logs}
          />

        </main>

      </div>

    </div>
  )
}