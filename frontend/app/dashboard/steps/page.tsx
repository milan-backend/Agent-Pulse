"use client";

import { useEffect, useState } from "react";

import {
  Rocket,
  Activity,
  ShieldCheck,
  AlertTriangle,
  Zap,
} from "lucide-react";

import {
  getDashboardSteps,
} from "@/components/api";

import MissionTable from "@/components/MissionTable";

export default function StepsPage() {

  const [steps, setSteps] =
    useState<any[]>([]);

  const [loading, setLoading] =
    useState(true);

  async function loadSteps() {

    try {

      const response =
        await getDashboardSteps();

      setSteps(
        Array.isArray(response)
          ? response
          : response?.steps || []
      );

    } catch (err) {

      console.error(err);

    } finally {

      setLoading(false);
    }
  }

  useEffect(() => {

    loadSteps();

  }, []);

  const running =
    steps.filter(
      (s) =>
        s?.status ===
          "running" ||
        s?.status ===
          "processing"
    ).length;

  const completed =
    steps.filter(
      (s) =>
        s?.status ===
          "completed" ||
        s?.status ===
          "success"
    ).length;

  const failed =
    steps.filter(
      (s) =>
        s?.status ===
          "failed" ||
        s?.status ===
          "error"
    ).length;

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
            Loading Missions...
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
              <Rocket
                className="
                  text-cyan-300
                "
                size={38}
              />
            </div>

            <div>
              <h1
                className="
                  text-5xl
                  font-black
                "
              >
                Mission Runtime
              </h1>

              <p
                className="
                  mt-3
                  text-slate-400
                  text-lg
                "
              >
                Autonomous AI mission
                execution and telemetry.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* METRICS */}

      <div
        className="
          grid
          grid-cols-1
          md:grid-cols-4
          gap-6
        "
      >
        {/* TOTAL */}

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
                Total Missions
              </p>

              <h2
                className="
                  text-5xl
                  font-black
                  mt-4
                  text-cyan-300
                "
              >
                {steps.length}
              </h2>
            </div>

            <Rocket
              className="
                text-cyan-300
              "
              size={34}
            />
          </div>
        </div>

        {/* RUNNING */}

        <div
          className="
            rounded-[30px]
            border
            border-purple-500/20
            bg-purple-500/10
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
                Running
              </p>

              <h2
                className="
                  text-5xl
                  font-black
                  mt-4
                  text-purple-300
                "
              >
                {running}
              </h2>
            </div>

            <Activity
              className="
                text-purple-300
              "
              size={34}
            />
          </div>
        </div>

        {/* SUCCESS */}

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
                Completed
              </p>

              <h2
                className="
                  text-5xl
                  font-black
                  mt-4
                  text-green-300
                "
              >
                {completed}
              </h2>
            </div>

            <ShieldCheck
              className="
                text-green-300
              "
              size={34}
            />
          </div>
        </div>

        {/* FAILED */}

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
                Failed
              </p>

              <h2
                className="
                  text-5xl
                  font-black
                  mt-4
                  text-red-300
                "
              >
                {failed}
              </h2>
            </div>

            <AlertTriangle
              className="
                text-red-300
              "
              size={34}
            />
          </div>
        </div>
      </div>

      {/* LIVE BAR */}

      <div
        className="
          rounded-[32px]
          border
          border-cyan-500/20
          bg-[linear-gradient(180deg,#071120_0%,#091525_100%)]
          p-6
          flex
          items-center
          justify-between
          flex-wrap
          gap-5
        "
      >
        <div
          className="
            flex
            items-center
            gap-4
          "
        >
          <div
            className="
              h-14
              w-14
              rounded-2xl
              border
              border-cyan-500/20
              bg-cyan-500/10
              flex
              items-center
              justify-center
            "
          >
            <Zap
              className="
                text-cyan-300
              "
              size={28}
            />
          </div>

          <div>
            <h2
              className="
                text-2xl
                font-black
              "
            >
              Runtime Telemetry Active
            </h2>

            <p
              className="
                text-slate-400
                mt-1
              "
            >
              Live mission execution stream
              connected.
            </p>
          </div>
        </div>

        <div
          className="
            flex
            items-center
            gap-3
            rounded-full
            border
            border-green-500/20
            bg-green-500/10
            px-5
            py-3
          "
        >
          <div
            className="
              h-2
              w-2
              rounded-full
              bg-green-400
              animate-pulse
            "
          />

          <span
            className="
              text-sm
              font-bold
              text-green-300
            "
          >
            LIVE
          </span>
        </div>
      </div>

      {/* TABLE */}

      <MissionTable
        steps={steps}
      />
    </div>
  );
}