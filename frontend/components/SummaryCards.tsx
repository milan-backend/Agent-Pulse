"use client"

export default function SummaryCards({
  summary,
  usage,
}: {
  summary: any
  usage: any
}) {

  const cards = [

    {
      title: "Total Calls",
      value: usage.total_calls || 0,
      color: "from-cyan-500 to-blue-500",
    },

    {
      title: "Executions",
      value: usage.executions || 0,
      color: "from-purple-500 to-pink-500",
    },

    {
      title: "Retries",
      value: usage.retries || 0,
      color: "from-yellow-500 to-orange-500",
    },

    {
      title: "Cache Hits",
      value: usage.cache_hits || 0,
      color: "from-green-500 to-emerald-500",
    },

  ]

  return (

    <div className="
      grid
      grid-cols-1
      md:grid-cols-2
      xl:grid-cols-4
      gap-6
    ">

      {cards.map((card, index) => (

        <div
          key={index}
          className={`
            rounded-3xl
            p-6
            border
            border-white/10
            bg-gradient-to-br
            ${card.color}
            shadow-2xl
            hover:scale-105
            transition
            duration-300
          `}
        >

          <p className="
            text-sm
            text-white/80
          ">
            {card.title}
          </p>

          <h2 className="
            text-5xl
            font-black
            mt-4
            text-white
          ">
            {card.value}
          </h2>

        </div>

      ))}

      {/* Success Rate */}
      <div className="
        rounded-3xl
        p-6
        border
        border-green-400/20
        bg-green-500/10
        backdrop-blur-xl
      ">

        <p className="
          text-sm
          text-green-300
        ">
          Success Rate
        </p>

        <h2 className="
          text-5xl
          font-black
          mt-4
          text-green-400
        ">
          {summary.success_rate || 0}%
        </h2>

      </div>

      {/* Estimated Savings */}
      <div className="
        rounded-3xl
        p-6
        border
        border-cyan-400/20
        bg-cyan-500/10
        backdrop-blur-xl
      ">

        <p className="
          text-sm
          text-cyan-300
        ">
          Estimated Savings
        </p>

        <h2 className="
          text-5xl
          font-black
          mt-4
          text-cyan-400
        ">
          $
          {(
            (usage.cache_hits || 0) * 0.02
          ).toFixed(2)}
        </h2>

      </div>

    </div>
  )
}