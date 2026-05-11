"use client"

import { useRouter } from "next/navigation"

export default function Home() {

  const router = useRouter()

  return (
    <main
      className="
        min-h-screen
        bg-black
        text-white
        relative
        overflow-hidden
        flex
        items-center
        justify-center
      "
    >

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
        max-w-5xl
        text-center
        px-6
      ">

        <div className="
          inline-block
          px-4
          py-2
          rounded-full
          border
          border-cyan-400/30
          bg-cyan-500/10
          text-cyan-300
          text-sm
          font-semibold
          mb-6
        ">
          AI Agent Observability Platform
        </div>

        <h1 className="
          text-6xl
          md:text-8xl
          font-black
          leading-tight
        ">
          Agent
          <span className="
            bg-gradient-to-r
            from-cyan-400
            to-purple-400
            bg-clip-text
            text-transparent
          ">
            Pulse
          </span>
        </h1>

        <p className="
          mt-8
          text-xl
          text-gray-300
          max-w-3xl
          mx-auto
          leading-relaxed
        ">
          Monitor AI missions, token usage,
          retries, execution timelines,
          and observability metrics in real-time.
        </p>

        <div className="
          mt-12
          flex
          flex-col
          sm:flex-row
          gap-5
          justify-center
        ">

          <button
            onClick={() => router.push("/signup")}
            className="
              px-8
              py-4
              rounded-2xl
              bg-cyan-500
              hover:bg-cyan-400
              text-black
              font-black
              text-lg
              transition
              hover:scale-105
            "
          >
            Get Started
          </button>

          <button
            onClick={() => router.push("/login")}
            className="
              px-8
              py-4
              rounded-2xl
              bg-white/5
              border
              border-white/10
              hover:bg-white/10
              font-bold
              text-lg
              transition
            "
          >
            Login
          </button>

        </div>

        {/* Feature Cards */}
        <div className="
          mt-20
          grid
          md:grid-cols-3
          gap-6
        ">

          <div className="
            rounded-3xl
            border
            border-white/10
            bg-white/5
            backdrop-blur-xl
            p-8
          ">
            <h3 className="
              text-2xl
              font-black
              text-cyan-300
            ">
              Real-Time Monitoring
            </h3>

            <p className="
              mt-4
              text-gray-400
            ">
              Track every mission execution
              with live updates and metrics.
            </p>
          </div>

          <div className="
            rounded-3xl
            border
            border-white/10
            bg-white/5
            backdrop-blur-xl
            p-8
          ">
            <h3 className="
              text-2xl
              font-black
              text-purple-300
            ">
              Usage Analytics
            </h3>

            <p className="
              mt-4
              text-gray-400
            ">
              Visualize token consumption,
              retries, cache hits, and costs.
            </p>
          </div>

          <div className="
            rounded-3xl
            border
            border-white/10
            bg-white/5
            backdrop-blur-xl
            p-8
          ">
            <h3 className="
              text-2xl
              font-black
              text-green-300
            ">
              Mission Timeline
            </h3>

            <p className="
              mt-4
              text-gray-400
            ">
              Understand every AI workflow
              step-by-step with detailed logs.
            </p>
          </div>

        </div>

      </div>

    </main>
  )
}