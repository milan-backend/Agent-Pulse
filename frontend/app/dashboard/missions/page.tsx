"use client"

import Link from "next/link";
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
  Search,
  SlidersHorizontal,
} from "lucide-react"

import StatusBadge from "@/components/ui/StatusBadge"
import SectionHeader from "@/components/ui/SectionHeader"
import LiveIndicator from "@/components/ui/LiveIndicator"

export default function MissionsPage() {
  const router = useRouter()
  const [missions, setMissions] = useState<any[]>([])
  const [overview, setOverview] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  const [searchQuery, setSearchQuery] = useState("")
  const [statusFilter, setStatusFilter] = useState("")

  async function loadData() {
    try {
      const [missionData, overviewData] = await Promise.all([
        getMissionList(searchQuery, statusFilter),
        getMissionOverview(),
      ])

      setMissions(Array.isArray(missionData) ? missionData : [])
      setOverview(overviewData)
    } catch (err) {
      console.error(err)
      toast.error(err instanceof Error ? err.message : "Failed to load missions")
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
  }, [router, statusFilter])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      loadData()
    }
  }

  async function handleRetry(missionId: string) {
    try {
      const response = await retryMission(missionId)
      toast.success(response?.message || "Mission retried")
      loadData()
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Retry failed")
    }
  }

  async function handleKill(missionId: string) {
    try {
      const response = await killMission(missionId)
      toast.success(response?.message || "Mission killed")
      loadData()
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Kill failed")
    }
  }

  async function handleResume(missionId: string) {
    try {
      const response = await resumeMission(missionId)
      toast.success(response?.message || "Mission resumed")
      loadData()
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Resume failed")
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[#050816] text-cyan-300 flex items-center justify-center">
        Loading missions...
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#050816] text-white p-8">
      
      {/* HEADER */}
      <div className="flex items-center justify-between flex-wrap gap-5 mb-10">
        <SectionHeader
          title="Mission Runtime"
          subtitle="Autonomous AI mission execution and telemetry."
        />
        <LiveIndicator />
      </div>

      {/* METRICS */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-10">
        <div className="rounded-3xl border border-cyan-500/20 bg-cyan-500/10 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-400">Total Missions</p>
              <h2 className="mt-3 text-5xl font-black text-cyan-300">{overview?.total_missions || 0}</h2>
            </div>
            <Rocket className="text-cyan-300" size={34} />
          </div>
        </div>

        <div className="rounded-3xl border border-purple-500/20 bg-purple-500/10 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-400">Running</p>
              <h2 className="mt-3 text-5xl font-black text-purple-300">{overview?.running || 0}</h2>
            </div>
            <Activity className="text-purple-300" size={34} />
          </div>
        </div>

        <div className="rounded-3xl border border-green-500/20 bg-green-500/10 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-400">Completed</p>
              <h2 className="mt-3 text-5xl font-black text-green-300">{overview?.completed || 0}</h2>
            </div>
            <ShieldCheck className="text-green-300" size={34} />
          </div>
        </div>

        <div className="rounded-3xl border border-red-500/20 bg-red-500/10 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-400">Failed</p>
              <h2 className="mt-3 text-5xl font-black text-red-300">{overview?.failed || 0}</h2>
            </div>
            <AlertTriangle className="text-red-300" size={34} />
          </div>
        </div>
      </div>

      {/* INTERACTIVE COMPOSITE SEARCH CONTROL BAR CONTAINER */}
      <div className="flex flex-col md:flex-row items-center gap-4 bg-[#091121] border border-cyan-500/10 p-4 rounded-2xl mb-10">
        <div className="relative flex-1 w-full">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Search by Mission ID or Task Name context string..."
            className="w-full bg-black/40 border border-cyan-500/20 rounded-xl pl-12 pr-4 py-3 text-sm focus:outline-none focus:border-cyan-400 transition-colors text-white placeholder-slate-500"
          />
        </div>
        <div className="flex items-center gap-3 w-full md:w-auto shrink-0">
          <div className="relative w-full md:w-48">
            <SlidersHorizontal className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={14} />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full bg-black/40 border border-cyan-500/20 rounded-xl pl-10 pr-4 py-3 text-sm focus:outline-none focus:border-cyan-400 transition-colors text-slate-300 appearance-none cursor-pointer"
            >
              <option value="" className="bg-[#091121] text-white">All Statuses</option>
              <option value="pending" className="bg-[#091121] text-white">Pending</option>
              <option value="running" className="bg-[#091121] text-white">Running</option>
              <option value="completed" className="bg-[#091121] text-white">Completed</option>
              <option value="failed" className="bg-[#091121] text-white">Failed</option>
            </select>
          </div>
          <button
            onClick={loadData}
            className="px-6 py-3 bg-cyan-500 text-black hover:bg-cyan-400 transition-colors font-bold rounded-xl text-sm w-full md:w-auto shadow-lg shadow-cyan-500/10"
          >
            Search
          </button>
        </div>
      </div>

      {/* MISSIONS MAP COMPONENT RENDERING BLOCK */}
      <div className="space-y-8">
        {missions.length === 0 ? (
          <div className="text-center py-12 rounded-3xl border border-cyan-500/10 bg-[#091121] text-slate-400 font-medium">
            No dynamic execution records match your target filter query.
          </div>
        ) : (
          missions.map((mission) => (
            <div key={mission.mission_id} className="rounded-3xl border border-cyan-500/20 bg-[#091121] p-8">
              <div className="flex items-center justify-between flex-wrap gap-5">
                <div>
                  <h2 className="text-3xl font-black">{mission.task_name || "Untitled Mission"}</h2>
                  <p className="mt-3 text-slate-400 break-all">{mission.mission_id}</p>
                </div>
                <StatusBadge status={mission.status || "unknown"} />
                {mission.is_retry && mission.original_mission_id && (
                  <Link
                    href={`/dashboard/missions/${mission.original_mission_id}`}
                    className="inline-flex items-center gap-2 mt-3 px-4 py-2 rounded-xl border border-cyan-400/40 bg-cyan-500/10 text-cyan-300 font-semibold text-sm shadow-lg shadow-cyan-500/20 hover:bg-cyan-500/20 hover:border-cyan-300 transition-all duration-200"
                  >
                    🔁 View Original Mission
                  </Link>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mt-8">
                <div className="rounded-2xl bg-black/30 p-5">
                  <p className="text-slate-400">Retry Count</p>
                  <h2 className="mt-2 text-3xl font-black text-green-400">{mission.retry_count || 0}</h2>
                </div>
                <div className="rounded-2xl bg-black/30 p-5">
                  <p className="text-slate-400">Cache Hit</p>
                  <h2 className="mt-2 text-3xl font-black text-yellow-400">{mission.cache_hit ? "YES" : "NO"}</h2>
                </div>
                <div className="rounded-2xl bg-black/30 p-5">
                  <p className="text-slate-400">Created At</p>
                  <h2 className="mt-2 text-sm font-bold text-cyan-300">
                    {mission.created_at ? new Date(mission.created_at).toLocaleString() : "N/A"}
                  </h2>
                </div>
              </div>

              <div className="flex items-center gap-4 flex-wrap mt-8">
                <button
                  onClick={() => router.push(`/dashboard/missions/${mission.mission_id}`)}
                  className="flex items-center gap-2 px-5 py-3 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 hover:bg-cyan-500 hover:text-black transition-all font-bold"
                >
                  <Eye size={18} /> View Mission
                </button>
                <button
                  onClick={() => handleRetry(mission.mission_id)}
                  className="flex items-center gap-2 px-5 py-3 rounded-2xl bg-green-500/10 border border-green-500/20 hover:bg-green-500 hover:text-black transition-all font-bold"
                >
                  <RotateCcw size={18} /> Retry
                </button>
                <button
                  onClick={() => handleKill(mission.mission_id)}
                  className="flex items-center gap-2 px-5 py-3 rounded-2xl bg-red-500/10 border border-red-500/20 hover:bg-red-500 hover:text-black transition-all font-bold"
                >
                  <Square size={18} /> Kill
                </button>
                <button
                  onClick={() => handleResume(mission.mission_id)}
                  className="flex items-center gap-2 px-5 py-3 rounded-2xl bg-yellow-500/10 border border-yellow-500/20 hover:bg-yellow-500 hover:text-black transition-all font-bold"
                >
                  <Play size={18} /> Resume
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
