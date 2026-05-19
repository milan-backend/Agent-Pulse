"use client";

import {
  useEffect,
  useState,
} from "react";

import {
  useParams,
  useRouter,
} from "next/navigation";

import Link from "next/link";

import {
  ArrowLeft,
  Rocket,
  Activity,
  ShieldCheck,
  AlertTriangle,
  Clock3,
  Bot,
  Zap,
} from "lucide-react";

import {
  getStepStatus,
} from "@/components/api";

import StepTimeline from "@/components/StepTimeline";

export default function StepDetailsPage() {

  const params =
    useParams();

  const router =
    useRouter();

  const [step, setStep] =
    useState<any>(null);

  const [loading, setLoading] =
    useState(true);

  async function loadStep() {

    try {

      if (!params?.id) {
        return;
      }

      const response =
        await getStepStatus(
          String(params.id)
        );

      setStep(response);

    } catch (err) {

      console.error(err);

    } finally {

      setLoading(false);
    }
  }

  useEffect(() => {

    loadStep();

  }, [params?.id]);

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
            Loading Mission...
          </p>
        </div>
      </div>
    );
  }

  if (!step) {

    return (

      <div
        className="
          min-h-[70vh]
          flex
          items-center
          justify-center
        "
      >
        <div
          className="
            rounded-[32px]
            border
            border-red-500/20
            bg-red-500/10
            p-10
            text-center
            max-w-xl
          "
        >
          <AlertTriangle
            size={60}
            className="
              mx-auto
              text-red-300
            "
          />

          <h2
            className="
              mt-6
              text-4xl
              font-black
              text-red-300
            "
          >
            Mission Not Found
          </h2>

          <p
            className="
              mt-4
              text-slate-300
            "
          >
            The requested mission
            does not exist.
          </p>

          <button
            onClick={() =>
              router.push(
                "/dashboard/steps"
              )
            }
            className="
              mt-8
              rounded-2xl
              bg-cyan-500
              px-6
              py-4
              text-black
              font-bold
            "
          >
            Back
          </button>
        </div>
      </div>
    );
  }

  const status =
    step?.status ||
    "running";

  const failed =
    status === "failed" ||
    status === "error";

  const success =
    status === "completed" ||
    status === "success";

  return (

    <div className="space-y-8">

      {/* TOP */}

      <div
        className="
          flex
          items-center
          justify-between
          gap-5
          flex-wrap
        "
      >
        <Link
          href="/dashboard/steps"
          className="
            flex
            items-center
            gap-3
            rounded-2xl
            border
            border-white/10
            bg-white/[0.04]
            px-5
            py-4
            text-slate-300
            hover:bg-white/[0.08]
            transition-all
          "
        >
          <ArrowLeft size={20} />

          Back
        </Link>

        <div
          className={`
            rounded-full
            border
            px-5
            py-3
            text-sm
            font-bold
            ${
              failed
                ? `
                  border-red-500/20
                  bg-red-500/10
                  text-red-300
                `
                : success
                ? `
                  border-green-500/20
                  bg-green-500/10
                  text-green-300
                `
                : `
                  border-cyan-500/20
                  bg-cyan-500/10
                  text-cyan-300
                `
            }
          `}
        >
          {status.toUpperCase()}
        </div>
      </div>

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
        <div
          className="
            absolute
            top-0
            right-0
            h-80
            w-80
            rounded-full
            bg-cyan-500/10
            blur-3xl
          "
        />

        <div className="relative z-10">

          <div
            className="
              flex
              items-start
              justify-between
              gap-10
              flex-wrap
            "
          >
            {/* LEFT */}

            <div className="max-w-4xl">

              <div
                className="
                  flex
                  items-center
                  gap-6
                "
              >
                <div
                  className="
                    h-28
                    w-28
                    rounded-[32px]
                    border
                    border-cyan-500/20
                    bg-cyan-500/10
                    flex
                    items-center
                    justify-center
                  "
                >
                  <Rocket
                    size={52}
                    className="
                      text-cyan-300
                    "
                  />
                </div>

                <div>

                  <h1
                    className="
                      text-5xl
                      font-black
                    "
                  >
                    {step?.task ||
                      step?.name ||
                      "Mission"}
                  </h1>

                  <p
                    className="
                      mt-4
                      text-lg
                      text-slate-400
                    "
                  >
                    Runtime mission
                    execution telemetry
                    and orchestration.
                  </p>
                </div>
              </div>

              {/* DESCRIPTION */}

              <div
                className="
                  mt-8
                  rounded-3xl
                  border
                  border-white/10
                  bg-black/20
                  p-6
                "
              >
                <p
                  className="
                    text-slate-300
                    leading-relaxed
                  "
                >
                  {step?.description ||
                    "Autonomous runtime mission execution currently processing through orchestration layers."}
                </p>
              </div>
            </div>

            {/* RIGHT */}

            <div
              className="
                rounded-[30px]
                border
                border-white/10
                bg-black/20
                p-8
                w-full
                max-w-sm
              "
            >
              <div className="space-y-5">

                <div
                  className="
                    flex
                    items-center
                    justify-between
                  "
                >
                  <span className="text-slate-400">
                    Runtime
                  </span>

                  <span className="font-bold text-cyan-300">
                    Live
                  </span>
                </div>

                <div
                  className="
                    flex
                    items-center
                    justify-between
                  "
                >
                  <span className="text-slate-400">
                    Security
                  </span>

                  <span className="font-bold text-green-300">
                    Safe
                  </span>
                </div>

                <div
                  className="
                    flex
                    items-center
                    justify-between
                  "
                >
                  <span className="text-slate-400">
                    Performance
                  </span>

                  <span className="font-bold text-purple-300">
                    Optimized
                  </span>
                </div>
              </div>
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

              <p className="text-slate-400">
                Runtime
              </p>

              <h2
                className="
                  mt-4
                  text-4xl
                  font-black
                  text-cyan-300
                "
              >
                LIVE
              </h2>
            </div>

            <Activity
              size={34}
              className="
                text-cyan-300
              "
            />
          </div>
        </div>

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

              <p className="text-slate-400">
                Security
              </p>

              <h2
                className="
                  mt-4
                  text-4xl
                  font-black
                  text-green-300
                "
              >
                SAFE
              </h2>
            </div>

            <ShieldCheck
              size={34}
              className="
                text-green-300
              "
            />
          </div>
        </div>

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

              <p className="text-slate-400">
                Agent
              </p>

              <h2
                className="
                  mt-4
                  text-4xl
                  font-black
                  text-purple-300
                "
              >
                AI
              </h2>
            </div>

            <Bot
              size={34}
              className="
                text-purple-300
              "
            />
          </div>
        </div>

        <div
          className="
            rounded-[30px]
            border
            border-yellow-500/20
            bg-yellow-500/10
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

              <p className="text-slate-400">
                Speed
              </p>

              <h2
                className="
                  mt-4
                  text-4xl
                  font-black
                  text-yellow-300
                "
              >
                FAST
              </h2>
            </div>

            <Zap
              size={34}
              className="
                text-yellow-300
              "
            />
          </div>
        </div>
      </div>

      {/* INFORMATION */}

      <div
        className="
          grid
          grid-cols-1
          xl:grid-cols-2
          gap-8
        "
      >
        {/* DETAILS */}

        <div
          className="
            rounded-[34px]
            border
            border-cyan-500/20
            bg-[linear-gradient(180deg,#071120_0%,#091525_100%)]
            p-8
          "
        >
          <h2
            className="
              text-3xl
              font-black
              mb-8
            "
          >
            Mission Information
          </h2>

          <div className="space-y-5">

            <div
              className="
                rounded-2xl
                bg-black/20
                px-5
                py-4
                flex
                items-center
                justify-between
              "
            >
              <span className="text-slate-400">
                Mission ID
              </span>

              <span className="font-bold">
                {step?.id || "N/A"}
              </span>
            </div>

            <div
              className="
                rounded-2xl
                bg-black/20
                px-5
                py-4
                flex
                items-center
                justify-between
              "
            >
              <span className="text-slate-400">
                Status
              </span>

              <span className="font-bold">
                {status}
              </span>
            </div>

            <div
              className="
                rounded-2xl
                bg-black/20
                px-5
                py-4
                flex
                items-center
                justify-between
              "
            >
              <span className="text-slate-400">
                Created
              </span>

              <div
                className="
                  flex
                  items-center
                  gap-3
                  font-bold
                "
              >
                <Clock3 size={18} />

                {step?.created_at
                  ? new Date(
                      step.created_at
                    ).toLocaleString()
                  : "Unknown"}
              </div>
            </div>
          </div>
        </div>

        {/* TIMELINE */}

        <StepTimeline
          logs={
            step?.logs || []
          }
        />
      </div>
    </div>
  );
}