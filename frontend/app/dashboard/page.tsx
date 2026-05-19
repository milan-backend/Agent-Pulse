"use client";

import { useEffect, useState } from "react";

import {
  Activity,
} from "lucide-react";

import {
  getDashboardSummary,
  createDashboardSocket,
} from "@/components/api";

import SummaryCards from "@/components/SummaryCards";
import LiveStatus from "@/components/LiveStatus";

export default function DashboardPage() {

  const [summary, setSummary] =
    useState<any>({});

  const [connected, setConnected] =
    useState(false);

  const [loading, setLoading] =
    useState(true);

  const [lastEvent, setLastEvent] =
    useState<any>(null);

  async function loadDashboard() {

    try {

      const summaryData =
        await getDashboardSummary();

      setSummary(
        summaryData || {}
      );

    } catch (err) {

      console.error(err);

    } finally {

      setLoading(false);
    }
  }

  useEffect(() => {

    loadDashboard();

    const interval =
      setInterval(() => {

        loadDashboard();

      }, 10000);

    const socket =
      createDashboardSocket(

        (data) => {

          console.log(data);

          setConnected(true);

          if (data.summary) {
            setSummary(data.summary);
          }

          setLastEvent(data);
        },

        () => {
          setConnected(true);
        },


        () => {
          setConnected(false);
        }
      );

    return () => {

      clearInterval(interval);

      socket.close();
    };

  }, []);

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
            Loading Runtime Dashboard...
          </p>
        </div>
      </div>
    );
  }

  return (

    <div className="space-y-8">

      {/* HERO */}

      <div
        className="
          rounded-[40px]
          border
          border-cyan-500/20
          bg-[linear-gradient(180deg,#071120_0%,#091525_100%)]
          p-10
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
            h-96
            w-96
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
              justify-between
              gap-8
              flex-wrap
            "
          >
            {/* LEFT */}

            <div>
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
                    h-24
                    w-24
                    rounded-[32px]
                    border
                    border-cyan-500/20
                    bg-cyan-500/10
                    flex
                    items-center
                    justify-center
                  "
                >
                  <Activity
                    className="
                      text-cyan-300
                    "
                    size={44}
                  />
                </div>

                <div>
                  <h1
                    className="
                      text-6xl
                      font-black
                      leading-none
                    "
                  >
                    Runtime Dashboard
                  </h1>

                  <p
                    className="
                      mt-4
                      text-slate-400
                      text-xl
                    "
                  >
                    Autonomous AI telemetry,
                    orchestration and mission
                    observability.
                  </p>
                </div>
              </div>
            </div>

            {/* STATUS */}

            <div
              className="
                flex
                items-center
                gap-4
                rounded-full
                border
                border-green-500/20
                bg-green-500/10
                px-6
                py-4
              "
            >
              <div
                className="
                  h-3
                  w-3
                  rounded-full
                  bg-green-400
                  animate-pulse
                "
              />

              <span
                className="
                  text-lg
                  font-black
                  text-green-300
                "
              >
                LIVE SYSTEM
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* SUMMARY */}

      <SummaryCards
        summary={summary}
      />

      {/* LIVE STATUS */}

      <LiveStatus
        connected={connected}
        summary={summary}
        lastEvent={lastEvent}
      />

    </div>
  );
}