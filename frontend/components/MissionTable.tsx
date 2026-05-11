"use client"

import { useRouter } from "next/navigation"

interface Props {
  steps: any[]
}

export default function MissionTable({
  steps,
}: Props) {

  const router = useRouter()

  return (
    <div
      className="
        mt-10
        rounded-3xl
        border
        border-white/10
        bg-white/5
        backdrop-blur-xl
        overflow-hidden
      "
    >

      {/* Header */}
      <div
        className="
          flex
          items-center
          justify-between
          px-8
          py-6
          border-b
          border-white/10
        "
      >

        <div>

          <h2
            className="
              text-4xl
              font-black
            "
          >
            Live Missions
          </h2>

          <p
            className="
              mt-2
              text-gray-400
            "
          >
            Real-time AI mission monitoring.
          </p>

        </div>

        <div
          className="
            px-4
            py-2
            rounded-full
            bg-green-500/10
            border
            border-green-400/20
            text-green-300
            text-sm
            font-bold
            animate-pulse
          "
        >
          ● LIVE
        </div>

      </div>

      {/* Table */}
      <div className="overflow-x-auto">

        <table className="w-full">

          <thead>

            <tr
              className="
                border-b
                border-white/10
                text-left
              "
            >

              <th
                className="
                  px-8
                  py-5
                  text-gray-400
                  font-semibold
                "
              >
                Task
              </th>

              <th
                className="
                  px-8
                  py-5
                  text-gray-400
                  font-semibold
                "
              >
                Status
              </th>

              <th
                className="
                  px-8
                  py-5
                  text-gray-400
                  font-semibold
                "
              >
                Agent
              </th>

              <th
                className="
                  px-8
                  py-5
                  text-gray-400
                  font-semibold
                "
              >
                Retries
              </th>

              <th
                className="
                  px-8
                  py-5
                  text-gray-400
                  font-semibold
                "
              >
                Cache
              </th>

            </tr>

          </thead>

          <tbody>

            {steps.map((step, index) => (

              <tr
                key={index}
                onClick={() =>
                  router.push(
                    `/dashboard/agent/${step.agent_id}`
                  )
                }
                className="
                  border-b
                  border-white/5
                  cursor-pointer
                  hover:bg-cyan-500/10
                  transition
                  duration-300
                "
              >

                {/* Task */}
                <td
                  className="
                    px-8
                    py-6
                    font-bold
                  "
                >
                  {step.task || "AI Mission"}
                </td>

                {/* Status */}
                <td className="px-8 py-6">

                  <span
                    className={`
                      px-4
                      py-2
                      rounded-full
                      text-sm
                      font-bold
                      ${
                        step.status === "active"
                          ? `
                            bg-green-500/20
                            text-green-300
                            border
                            border-green-400/20
                          `
                          : `
                            bg-cyan-500/20
                            text-cyan-300
                            border
                            border-cyan-400/20
                          `
                      }
                    `}
                  >
                    {step.status || "running"}
                  </span>

                </td>

                {/* Agent */}
                <td
                  className="
                    px-8
                    py-6
                    text-gray-300
                    font-mono
                    text-sm
                  "
                >
                  {step.agent_id}
                </td>

                {/* Retries */}
                <td
                  className="
                    px-8
                    py-6
                    font-bold
                  "
                >
                  {step.retry_count || 0}
                </td>

                {/* Cache */}
                <td
                  className="
                    px-8
                    py-6
                  "
                >

                  {step.cache_hit ? (

                    <span
                      className="
                        px-4
                        py-2
                        rounded-full
                        bg-purple-500/20
                        border
                        border-purple-400/20
                        text-purple-300
                        text-sm
                        font-bold
                      "
                    >
                      Cache Hit
                    </span>

                  ) : (

                    <span
                      className="
                        px-4
                        py-2
                        rounded-full
                        bg-white/5
                        border
                        border-white/10
                        text-gray-400
                        text-sm
                        font-bold
                      "
                    >
                      No Cache
                    </span>

                  )}

                </td>

              </tr>

            ))}

          </tbody>

        </table>

      </div>

    </div>
  )
}