"use client"

type Props = {
  logs: any[]
}

export default function StepTimeline({
  logs,
}: Props) {

  return (
    <div className="mt-10 bg-white/10 backdrop-blur-lg rounded-2xl border border-white/10 p-6">

      <h2 className="text-2xl font-bold text-white">
        Activity Feed
      </h2>

      <div className="mt-6 space-y-4">

        {logs?.map((log, index) => (

          <div
            key={index}
            className="flex items-start gap-4 border border-white/10 rounded-xl p-4 bg-black/20"
          >

            <div
              className={`
                h-3 w-3 rounded-full mt-2

                ${
                  log.action === "execute"
                    ? "bg-cyan-400"
                    : log.action === "retry"
                    ? "bg-yellow-400"
                    : "bg-green-400"
                }
              `}
            />

            <div>
              <p className="text-white font-semibold">
                {log.action}
              </p>

              <p className="text-sm text-gray-400 mt-1">
                Step: {log.step_id?.slice(0, 12)}...
              </p>

              <p className="text-xs text-gray-500 mt-1">
                {log.timestamp}
              </p>
            </div>

          </div>

        ))}

      </div>
    </div>
  )
}