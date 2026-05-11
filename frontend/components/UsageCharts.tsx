"use client"

import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
} from "recharts"

export default function UsageCharts({
  usage,
}: {
  usage: any
}) {

  const pieData = [
    {
      name: "Cache Hits",
      value: usage.cache_hits || 0,
    },
    {
      name: "Executions",
      value: usage.executions || 0,
    },
  ]

  const barData = [
    {
      name: "Calls",
      value: usage.total_calls || 0,
    },
    {
      name: "Retries",
      value: usage.retries || 0,
    },
    {
      name: "Cache",
      value: usage.cache_hits || 0,
    },
  ]

  return (

    <div className="
      mt-10
      grid
      grid-cols-1
      lg:grid-cols-2
      gap-8
    ">

      {/* Pie Chart */}
      <div className="
        glow-card
        rounded-3xl
        border
        border-white/10
        bg-white/5
        backdrop-blur-xl
        p-6
      ">

        <h2 className="
          text-2xl
          font-black
          mb-6
        ">
          Cache Efficiency
        </h2>

        <div className="h-80">

          <ResponsiveContainer
            width="100%"
            height="100%"
          >

            <PieChart>

              <Pie
                data={pieData}
                dataKey="value"
                outerRadius={110}
                label
              >

                <Cell fill="#00ffff" />
                <Cell fill="#9333ea" />

              </Pie>

              <Tooltip />

            </PieChart>

          </ResponsiveContainer>

        </div>

      </div>

      {/* Bar Chart */}
      <div className="
        glow-card
        rounded-3xl
        border
        border-white/10
        bg-white/5
        backdrop-blur-xl
        p-6
      ">

        <h2 className="
          text-2xl
          font-black
          mb-6
        ">
          System Metrics
        </h2>

        <div className="h-80">

          <ResponsiveContainer
            width="100%"
            height="100%"
          >

            <BarChart data={barData}>

              <XAxis dataKey="name" />

              <YAxis />

              <Tooltip />

              <Bar
                dataKey="value"
                fill="#06b6d4"
                radius={[10,10,0,0]}
              />

            </BarChart>

          </ResponsiveContainer>

        </div>

      </div>

    </div>
  )
}