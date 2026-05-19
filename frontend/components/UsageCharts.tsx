"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";

import {
  Activity,
  TrendingUp,
  DollarSign,
  Cpu,
} from "lucide-react";

interface Props {
  usage?: any;
}

export default function UsageCharts({
  usage = {},
}: Props) {

  // =========================
  // RUNTIME DATA
  // =========================

  const runtimeData = [

    {
      name: "Steps",
      cost:
        Number(
          usage?.total_cost || 0
        ),

      missions:
        Number(
          usage?.total_steps || 0
        ),
    },

    {
      name: "Success",
      cost:
        Number(
          usage?.average_cost || 0
        ),

      missions:
        Number(
          usage?.successful_steps || 0
        ),
    },

    {
      name: "Failed",
      cost: 0,

      missions:
        Number(
          usage?.failed_steps || 0
        ),
    },

    {
      name: "Cache",
      cost: 0,

      missions:
        Number(
          usage?.cache_hits || 0
        ),
    },
  ];

  return (

    <div className="space-y-8">

      {/* TOP CHART */}

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

        {/* HEADER */}

        <div
          className="
            relative
            z-10
            flex
            items-center
            justify-between
            mb-8
            flex-wrap
            gap-5
          "
        >

          <div>

            <h2
              className="
                text-4xl
                font-black
              "
            >
              Runtime Analytics
            </h2>

            <p
              className="
                text-slate-400
                mt-2
              "
            >
              Real-time mission execution
              and runtime spending trends.
            </p>

          </div>

          <div
            className="
              flex
              items-center
              gap-3
              rounded-full
              border
              border-cyan-500/20
              bg-cyan-500/10
              px-5
              py-2
            "
          >

            <TrendingUp
              size={18}
              className="text-cyan-300"
            />

            <span
              className="
                text-sm
                font-bold
                text-cyan-300
              "
            >
              LIVE ANALYTICS
            </span>

          </div>
        </div>

        {/* AREA CHART */}

        <div
          className="
            relative
            z-10
            h-[340px]
          "
        >

          <ResponsiveContainer
            width="100%"
            height={350}
          >

            <AreaChart
              data={runtimeData}
            >

              <defs>

                <linearGradient
                  id="costGradient"
                  x1="0"
                  y1="0"
                  x2="0"
                  y2="1"
                >

                  <stop
                    offset="5%"
                    stopColor="#22d3ee"
                    stopOpacity={0.4}
                  />

                  <stop
                    offset="95%"
                    stopColor="#22d3ee"
                    stopOpacity={0}
                  />
                </linearGradient>
              </defs>

              <CartesianGrid
                strokeDasharray="3 3"
                stroke="#1e293b"
              />

              <XAxis
                dataKey="name"
                stroke="#64748b"
              />

              <YAxis
                stroke="#64748b"
              />

              <Tooltip />

              <Area
                type="monotone"
                dataKey="cost"
                stroke="#22d3ee"
                fillOpacity={1}
                fill="url(#costGradient)"
                strokeWidth={4}
              />

            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* BOTTOM GRID */}

      <div
        className="
          grid
          grid-cols-1
          xl:grid-cols-2
          gap-8
        "
      >

        {/* MISSIONS */}

        <div
          className="
            rounded-[32px]
            border
            border-purple-500/20
            bg-[linear-gradient(180deg,#071120_0%,#091525_100%)]
            p-8
            overflow-hidden
            relative
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
                  text-3xl
                  font-black
                "
              >
                Mission Load
              </h2>

              <p
                className="
                  text-slate-400
                  mt-2
                "
              >
                Runtime execution throughput.
              </p>

            </div>

            <div
              className="
                h-14
                w-14
                rounded-2xl
                bg-purple-500/10
                border
                border-purple-500/20
                flex
                items-center
                justify-center
              "
            >

              <Activity
                className="
                  text-purple-300
                "
                size={26}
              />
            </div>
          </div>

          {/* BAR CHART */}

          <div className="h-[300px]">

            <ResponsiveContainer
              width="100%"
              height={350}
            >

              <BarChart
                data={runtimeData}
              >

                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="#1e293b"
                />

                <XAxis
                  dataKey="name"
                  stroke="#64748b"
                />

                <YAxis
                  stroke="#64748b"
                />

                <Tooltip />

                <Bar
                  dataKey="missions"
                  fill="#a855f7"
                  radius={[
                    10,
                    10,
                    0,
                    0,
                  ]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* COST OVERVIEW */}

        <div
          className="
            rounded-[32px]
            border
            border-green-500/20
            bg-[linear-gradient(180deg,#071120_0%,#091525_100%)]
            p-8
            overflow-hidden
            relative
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
                  text-3xl
                  font-black
                "
              >
                Runtime Spend
              </h2>

              <p
                className="
                  text-slate-400
                  mt-2
                "
              >
                Token and compute cost overview.
              </p>

            </div>

            <div
              className="
                h-14
                w-14
                rounded-2xl
                bg-green-500/10
                border
                border-green-500/20
                flex
                items-center
                justify-center
              "
            >

              <DollarSign
                className="
                  text-green-300
                "
                size={26}
              />
            </div>
          </div>

          {/* STATS */}

          <div className="space-y-5">

            {/* TOTAL */}

            <div
              className="
                rounded-3xl
                border
                border-green-500/20
                bg-green-500/10
                p-6
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

                  <h3
                    className="
                      mt-3
                      text-5xl
                      font-black
                      text-green-300
                    "
                  >
                    $
                    {Number(
                      usage?.total_cost || 0
                    ).toFixed(2)}
                  </h3>

                </div>

                <DollarSign
                  className="
                    text-green-300
                  "
                  size={34}
                />
              </div>
            </div>

            {/* TOKENS */}

            <div
              className="
                rounded-3xl
                border
                border-cyan-500/20
                bg-cyan-500/10
                p-6
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
                    Tokens Processed
                  </p>

                  <h3
                    className="
                      mt-3
                      text-5xl
                      font-black
                      text-cyan-300
                    "
                  >
                    {usage?.total_tokens || 0}
                  </h3>

                </div>

                <Cpu
                  className="
                    text-cyan-300
                  "
                  size={34}
                />
              </div>
            </div>

            {/* SUCCESS */}

            <div
              className="
                rounded-3xl
                border
                border-purple-500/20
                bg-purple-500/10
                p-6
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
                    Mission Success
                  </p>

                  <h3
                    className="
                      mt-3
                      text-5xl
                      font-black
                      text-purple-300
                    "
                  >
                    {usage?.success_rate || 0}%
                  </h3>

                </div>

                <Activity
                  className="
                    text-purple-300
                  "
                  size={34}
                />
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}