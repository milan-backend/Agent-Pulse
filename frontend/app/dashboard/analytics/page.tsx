"use client";

import { useEffect, useState } from "react";

import { useRouter } from "next/navigation"

import MetricCard from "@/components/ui/MetricCard"

import SectionHeader from "@/components/ui/SectionHeader"

import LiveIndicator from "@/components/ui/LiveIndicator"

import StatusBadge from "@/components/ui/StatusBadge"

export default function AnalyticsPage() {

  const router = useRouter()

  const [costs, setCosts] = useState<any>(null);

  const [blocked, setBlocked] = useState<any>(null);

  const [agents, setAgents] = useState<any>({});

  useEffect(() => {

    fetchAnalytics();

  }, []);

  const fetchAnalytics = async () => {

    try {

      const token = localStorage.getItem("token");

      const costRes = await fetch(
        "http://127.0.0.1:8000/analytics/costs",
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const blockedRes = await fetch(
        "http://127.0.0.1:8000/analytics/blocked",
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const agentsRes = await fetch(
        "http://127.0.0.1:8000/analytics/agents",
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const costData = await costRes.json();

      const blockedData = await blockedRes.json();

      const agentsData = await agentsRes.json();

      setCosts(costData);

      setBlocked(blockedData);

      setAgents(agentsData);

    } catch (error) {

      console.error(error);

    }
  };

  return (

    <div className="
      min-h-screen
      bg-black
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
            title="Analytics Center"
            subtitle="AI infrastructure intelligence dashboard."
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

      {/* TOP CARDS */}
      <div className="
        grid
        grid-cols-1
        md:grid-cols-2
        xl:grid-cols-4
        gap-6
        mb-10
      ">

        <MetricCard
          title="Total Agents"
          value={agents?.total_agents ?? 0}
          color="text-cyan-400"
          subtitle="Registered AI agents"
        />

        <MetricCard
          title="Blocked Missions"
          value={blocked?.blocked_missions || 0}
          color="text-red-400"
          subtitle="Guardrail interventions"
        />

        <MetricCard
          title="Total Cost"
          value={`$${costs?.total_cost || 0}`}
          color="text-green-400"
          subtitle="AI runtime expenditure"
        />

        <MetricCard
          title="Average Cost"
          value={`$${costs?.average_cost || 0}`}
          color="text-yellow-400"
          subtitle="Average execution spend"
        />

      </div>

      {/* COST SECTION */}
      <div className="
        bg-[#08111f]
        border
        border-cyan-500/20
        rounded-2xl
        p-8
        mb-10
      ">

        <div className="
          flex
          items-center
          justify-between
          mb-6
        ">

          <div>

            <h2 className="
              text-3xl
              font-bold
              text-cyan-400
            ">
              Cost Intelligence
            </h2>

            <p className="
              text-gray-400
              mt-1
            ">
              AI runtime expenditure overview.
            </p>

          </div>

          <LiveIndicator />

        </div>

        <div className="
          grid
          grid-cols-1
          md:grid-cols-3
          gap-6
        ">

          <div className="
            bg-black/40
            rounded-xl
            p-6
          ">

            <p className="
              text-gray-400
              mb-2
            ">
              Total Steps
            </p>

            <h3 className="
              text-4xl
              font-bold
              text-white
            ">
              {costs?.total_steps ?? 0}
            </h3>

          </div>

          <div className="
            bg-black/40
            rounded-xl
            p-6
          ">

            <p className="
              text-gray-400
              mb-2
            ">
              Current Spend
            </p>

            <h3 className="
              text-4xl
              font-bold
              text-cyan-400
            ">
              ${costs?.total_cost ?? 0}
            </h3>

          </div>

          <div className="
            bg-black/40
            rounded-xl
            p-6
          ">

            <p className="
              text-gray-400
              mb-2
            ">
              Avg / Execution
            </p>

            <h3 className="
              text-4xl
              font-bold
              text-yellow-400
            ">
              ${costs?.average_cost ?? 0}
            </h3>

          </div>

        </div>

      </div>

      {/* AGENT TABLE */}
      <div className="
        bg-[#08111f]
        border
        border-cyan-500/20
        rounded-2xl
        p-8
      ">

        <div className="mb-6">

          <h2 className="
            text-3xl
            font-bold
            text-white
          ">
            Agent Operations
          </h2>

          <p className="
            text-gray-400
            mt-1
          ">
            Live AI mission execution overview.
          </p>

        </div>

        <div className="
          bg-black/40
          border
          border-white/5
          rounded-xl
          p-5
          flex
          justify-between
          items-center
        ">

          <div>

            <p className="
              text-cyan-400
              font-bold
            ">
              {agents?.total_agents ?? 0} Registered Agents
            </p>

            <p className="
              text-gray-500
              text-sm
              mt-1
            ">
              Active AI Agent Infrastructure
            </p>

          </div>

          <div className="
            flex
            gap-10
          ">

            <div>

              <p className="
                text-gray-500
                text-sm
                mb-2
              ">
                Status
              </p>

              <StatusBadge status="running" />

            </div>

            <div>

              <p className="
                text-gray-500
                text-sm
                mb-2
              ">
                Security
              </p>

              <StatusBadge status="completed" />

            </div>

          </div>

        </div>

      </div>

    </div>
  );
}