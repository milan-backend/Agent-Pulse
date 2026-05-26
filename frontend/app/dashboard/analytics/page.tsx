"use client";

import { useEffect, useState } from "react";

import {
  DollarSign,
  ShieldAlert,
  Bot,
  Activity,
  TrendingUp,
} from "lucide-react";

import {
  getAnalyticsOverview,
} from "@/components/api";

import CacheChart from "@/components/CacheChart";
import UsageCharts from "@/components/UsageCharts";

import { toast } from "sonner";

export default function AnalyticsPage() {

  // =========================
  // STATES
  // =========================

  const [costs, setCosts] =
    useState<any>({});

  const [blocked, setBlocked] =
    useState<number>(0);

  const [agents, setAgents] =
    useState<number>(0);

  const [blockedList, setBlockedList] =
    useState<any[]>([]);

  const [loading, setLoading] =
    useState(true);

  // =========================
  // LOAD ANALYTICS
  // =========================

  async function loadAnalytics() {

    try {

      const analyticsData =
        await getAnalyticsOverview();

      const overview =
        analyticsData?.overview || {};

      const costsData =
        analyticsData?.costs || {};

      const cacheData =
        analyticsData?.cache || {};

      const tokenData =
        analyticsData?.tokens || {};

      // =========================
      // COSTS
      // =========================

      setCosts({

        total_steps:
          overview?.total_steps || 0,

        total_cost:
          costsData?.total_cost || 0,

        average_cost:
          costsData?.average_cost || 0,

        successful_steps:
          overview?.successful_steps || 0,

        failed_steps:
          overview?.failed_steps || 0,

        success_rate:
          overview?.success_rate || 0,

        cache_hits:
          cacheData?.cache_hits || 0,

        cache_misses:
          cacheData?.cache_misses || 0,

        cache_hit_rate:
          cacheData?.cache_hit_rate || 0,

        total_tokens:
          tokenData?.total_tokens || 0,
      });

      // =========================
      // BLOCKED MISSIONS COUNT
      // =========================

      setBlocked(
        Number(
          overview?.blocked_missions || 0
        )
      );

      // =========================
      // TOTAL AGENTS
      // =========================

      setAgents(
        Number(
          overview?.total_agents || 0
        )
      );

      // =========================
      // LIVE FEED
      // =========================

      setBlockedList(
        analyticsData?.live_feed || []
      );

    } catch (err) {

      console.error(err);

      toast.error(
        err instanceof Error
          ? err.message
          : "Failed to load analytics"
      );

    } finally {

      setLoading(false);
    }
  }

  // =========================
  // INIT
  // =========================

  useEffect(() => {

    loadAnalytics();

    const interval =
      setInterval(() => {
        loadAnalytics();
      }, 15000);

    return () =>
      clearInterval(interval);

  }, []);

  // =========================
  // LOADER
  // =========================

  if (loading) {

    return (

      <div
        className="
          min-h-[80vh]
          flex
          items-center
          justify-center
        "
      >
        <div className="text-center">

          <div
            className="
              h-16
              w-16
              rounded-full
              border-4
              border-cyan-500/20
              border-t-cyan-400
              animate-spin
              mx-auto
            "
          />

          <p
            className="
              mt-6
              text-xl
              font-bold
              text-cyan-300
            "
          >
            Loading Analytics...
          </p>
        </div>
      </div>
    );
  }

  // =========================
  // PAGE
  // =========================

  return (

    <div className="space-y-8">

      {/* HERO */}

      <div
        className="
          rounded-[32px]
          border
          border-cyan-500/20
          bg-[linear-gradient(180deg,#071120_0%,#091525_100%)]
          p-8
          overflow-hidden
          relative
        "
      >

        {/* GLOW */}

        <div
          className="
            absolute
            top-0
            right-0
            h-72
            w-72
            rounded-full
            bg-cyan-500/10
            blur-3xl
          "
        />

        {/* CONTENT */}

        <div className="relative z-10">

          <div
            className="
              flex
              items-center
              gap-5
              flex-wrap
            "
          >

            <div
              className="
                h-20
                w-20
                rounded-3xl
                border
                border-cyan-500/20
                bg-cyan-500/10
                flex
                items-center
                justify-center
              "
            >
              <TrendingUp
                className="
                  text-cyan-300
                "
                size={40}
              />
            </div>

            <div>

              <h1
                className="
                  text-5xl
                  font-black
                "
              >
                Runtime Analytics
              </h1>

              <p
                className="
                  mt-3
                  text-slate-400
                  text-lg
                "
              >
                AI observability telemetry,
                mission performance and
                runtime spend analysis.
              </p>

            </div>
          </div>
        </div>
      </div>

      {/* TOP METRICS */}

      <div
        className="
          grid
          grid-cols-1
          md:grid-cols-3
          gap-6
        "
      >

        {/* COST */}

        <div
          className="
            rounded-[30px]
            border
            border-green-500/20
            bg-green-500/10
            p-7
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

              <p className="text-sm text-slate-400">
                Total Runtime Cost
              </p>

              <h2
                className="
                  text-5xl
                  font-black
                  mt-4
                  text-green-300
                "
              >
                $
                {Number(
                  costs?.total_cost || 0
                ).toFixed(2)}
              </h2>

            </div>

            <DollarSign
              className="
                text-green-300
              "
              size={34}
            />
          </div>
        </div>

        {/* BLOCKED */}

        <div
          className="
            rounded-[30px]
            border
            border-red-500/20
            bg-red-500/10
            p-7
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

              <p className="text-sm text-slate-400">
                Blocked Missions
              </p>

              <h2
                className="
                  text-5xl
                  font-black
                  mt-4
                  text-red-300
                "
              >
                {blocked}
              </h2>

            </div>

            <ShieldAlert
              className="
                text-red-300
              "
              size={34}
            />
          </div>
        </div>

        {/* AGENTS */}

        <div
          className="
            rounded-[30px]
            border
            border-cyan-500/20
            bg-cyan-500/10
            p-7
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

              <p className="text-sm text-slate-400">
                Agent Analytics
              </p>

              <h2
                className="
                  text-5xl
                  font-black
                  mt-4
                  text-cyan-300
                "
              >
                {agents}
              </h2>

            </div>

            <Bot
              className="
                text-cyan-300
              "
              size={34}
            />
          </div>
        </div>
      </div>

      {/* CHARTS */}

      <UsageCharts usage={costs} />

      <CacheChart usage={costs} />

      {/* BLOCKED MISSIONS */}

      <div
        className="
          rounded-[32px]
          border
          border-red-500/20
          bg-[linear-gradient(180deg,#071120_0%,#130909_100%)]
          p-8
        "
      >

        {/* HEADER */}

        <div
          className="
            flex
            items-center
            justify-between
            mb-8
          "
        >

          <div>

            <h2
              className="
                text-4xl
                font-black
              "
            >
              Runtime Feed
            </h2>

            <p
              className="
                mt-2
                text-slate-400
              "
            >
              Recent runtime activity,
              execution logs and failures.
            </p>

          </div>

          <div
            className="
              h-14
              w-14
              rounded-2xl
              border
              border-red-500/20
              bg-red-500/10
              flex
              items-center
              justify-center
            "
          >

            <ShieldAlert
              className="
                text-red-300
              "
              size={28}
            />
          </div>
        </div>

        {/* EMPTY */}

        {blockedList.length === 0 && (

          <div
            className="
              rounded-3xl
              border
              border-white/10
              bg-white/[0.03]
              p-10
              text-center
            "
          >

            <Activity
              size={48}
              className="
                mx-auto
                text-slate-500
              "
            />

            <h3
              className="
                mt-5
                text-2xl
                font-black
              "
            >
              No Runtime Activity
            </h3>

            <p
              className="
                mt-3
                text-slate-400
              "
            >
              Runtime execution is healthy.
            </p>

          </div>
        )}

        {/* LIST */}

        {blockedList.length > 0 && (

          <div className="space-y-5">

            {blockedList.map(
              (
                item: any,
                index: number
              ) => (

                <div
                  key={
                    item?.id ||
                    item?.step_id ||
                    index
                  }
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
                      items-start
                      justify-between
                      gap-5
                      flex-wrap
                    "
                  >

                    <div>

                      <h3
                        className="
                          text-2xl
                          font-black
                          text-red-300
                        "
                      >
                        {
                          item?.action ||
                          item?.event_type ||
                          item?.status ||
                          "Runtime Event"
                        }
                      </h3>

                      <p
                        className="
                          mt-3
                          text-slate-400
                        "
                      >
                        Agent ID:
                        {" "}
                        {
                          item?.agent_id ||
                          "Unknown Agent"
                        }
                      </p>

                      <p
                        className="
                          mt-1
                          text-slate-500
                          text-sm
                        "
                      >
                        Cost:
                        {" "}
                        $
                        {Number(
                          item?.cost || 0
                        ).toFixed(4)}
                      </p>

                    </div>

                    <div
                      className="
                        rounded-full
                        border
                        border-red-500/20
                        bg-red-500/10
                        px-4
                        py-2
                        text-sm
                        font-bold
                        text-red-300
                      "
                    >
                      LIVE
                    </div>

                  </div>
                </div>
              )
            )}
          </div>
        )}
      </div>
    </div>
  );
}