"use client"

export default function LiveFeed({
  logs,
}: {
  logs: any[]
}) {

  return (

    <div className="
      mt-10
      rounded-3xl
      border
      border-white/10
      bg-white/5
      backdrop-blur-xl
      p-6
      glow-card
    ">

      <div className="
        flex
        items-center
        justify-between
        mb-6
      ">

        <h2 className="
          text-3xl
          font-black
        ">
          Live Activity Feed
        </h2>

        <div className="
          flex
          items-center
          gap-2
          text-green-400
          animate-pulse
          font-semibold
        ">
          <div className="
            w-3
            h-3
            rounded-full
            bg-green-400
          " />

          LIVE
        </div>

      </div>

      <div className="
        space-y-4
        max-h-[500px]
        overflow-y-auto
      ">

        {logs.length === 0 && (

          <div className="
            text-gray-400
          ">
            No activity yet.
          </div>

        )}

        {logs.map((log, index) => (

          <div
            key={index}
            className="
              rounded-2xl
              border
              border-white/10
              bg-black/30
              p-4
              hover:bg-white/5
              transition
            "
          >

            <div className="
              flex
              items-center
              justify-between
            ">

              <div>

                <h3 className="
                  font-bold
                  text-cyan-300
                ">
                  {log.task || "AI Mission"}
                </h3>

                <p className="
                  text-sm
                  text-gray-400
                  mt-1
                ">
                  Agent:
                  {" "}
                  {log.agent_id || "Unknown"}
                </p>

              </div>

              <div className="
                text-sm
                text-green-400
                font-semibold
              ">
                SUCCESS
              </div>

            </div>

          </div>

        ))}

      </div>

    </div>
  )
}