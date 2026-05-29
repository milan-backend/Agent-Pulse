"use client";

import {
  useEffect,
  useState
} from "react";

import {
  createCheckout,
  getCurrentPlan
} from "@/components/api";

import {
  CreditCard,
  Rocket,
  Shield,
  Cpu,
  CheckCircle2,
  Sparkles,
} from "lucide-react";

const plans = [
  {
    name: "Free",
    price: "$0",
    description:
      "For solo runtime experimentation",

    features: [
      "1 Agent",
      "1 Team Member",
      "10 Runtime Hours",
      "Live WebSocket Updates",
      "Analytics",
      "Missions",
      "Usage Logs",
      "Single Agent Pause",
      "Single Agent Resume",
      "Single Agent Kill"
    ],

    button: "Current Plan",

    disabled: true,

    glow:
      "from-slate-700/40 to-slate-900/40",

    border:
      "border-slate-700/40",
  },

  {
    name: "Pro",

    price: "$29",

    description:
      "Advanced orchestration for growing AI teams",

    features: [
      "10 Agents",
      "10 Team Members",
      "100 Runtime Hours",
      "Multi Workspace",
      "Team Collaboration",
      "MCP Access",
      "Priority Execution",
      "Retry Controls",
      "Loop Detection",
      "Budget Controls",
      "Analytics",
      "Audit Logs"
    ],

    button: "Upgrade to Pro",

    planKey: "pro",

    featured: true,

    glow:
      "from-cyan-500/20 to-blue-500/10",

    border:
      "border-cyan-400/30",
  },

  {
    name: "Enterprise",

    price: "$199",

    description:
      "Enterprise-scale autonomous AI infrastructure",

    features: [
      "100 Agents",
      "100 Team Members",
      "10000 Runtime Hours",
      "Dedicated Runtime",
      "Maintenance Mode",
      "Unlimited Missions",
      "Priority Runtime Queue",
      "Advanced Audit Logs",
      "Advanced Budget Control",
      "Enterprise Analytics",
      "MCP Integrations",
      "Full Platform Access"
    ],

    button:
      "Upgrade to Enterprise",

    planKey:
      "enterprise",

    glow:
      "from-fuchsia-500/20 to-cyan-500/10",

    border:
      "border-fuchsia-400/30",
  }
];

export default function BillingPage() {

  const [
    currentPlan,
    setCurrentPlan
  ] = useState("free");

  useEffect(() => {

    const loadPlan = async () => {

      try {

        const data =
          await getCurrentPlan();

        setCurrentPlan(
          (
            data?.plan ||
            "free"
          ).toLowerCase()
        );

      } catch {

        setCurrentPlan(
          "free"
        );
      }
    };

    loadPlan();

  }, []);

  const handleCheckout = async (
    planName: string
  ) => {

    try {

      const response =
        await createCheckout(
          planName
        );

      window.location.href =
        response.checkout_url;

    } catch (error) {

      console.error(error);

      alert("Checkout failed");
    }
  };

  return (

    <div
      className="
        min-h-screen
        bg-[#020817]
        text-white
        overflow-hidden
        relative
        p-8
      "
    >

      {/* BACKGROUND GLOW */}

      <div
        className="
          absolute
          top-0
          right-0
          h-[500px]
          w-[500px]
          rounded-full
          bg-cyan-500/10
          blur-3xl
        "
      />

      <div
        className="
          absolute
          bottom-0
          left-0
          h-[500px]
          w-[500px]
          rounded-full
          bg-fuchsia-500/10
          blur-3xl
        "
      />

      <div className="relative z-10">

        {/* HERO */}

        <div
          className="
            rounded-[40px]
            border
            border-cyan-500/20
            bg-[linear-gradient(180deg,#071120_0%,#091525_100%)]
            p-6 md:p-8
            overflow-hidden
            relative
            mb-6
          "
        >

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

          <div className="relative z-10">

            <div
              className="
                flex
                items-center
                gap-5
              "
            >

              <div
                className="
                  h-16
                  w-16
                  rounded-2xl
                  border
                  border-cyan-500/20
                  bg-cyan-500/10
                  flex
                  items-center
                  justify-center
                "
              >
                <CreditCard
                  size={42}
                  className="
                    text-cyan-300
                  "
                />
              </div>

              <div>

                <h1
                  className="
                    text-4xl md:text-5xl
                    font-black
                    leading-none
                  "
                >
                  AI Runtime Pricing
                </h1>

                <p
                  className="
                    mt-4
                    text-slate-400
                    text-base md:text-lg
                    max-w-3xl
                  "
                >
                  Scale autonomous AI agents
                  from solo experimentation
                  to enterprise-grade runtime
                  orchestration.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* CURRENT PLAN CARD */}

        <div
          className="
            mb-8
            rounded-[32px]
            border
            border-green-500/20
            bg-[linear-gradient(180deg,#071120_0%,#091525_100%)]
            p-8
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

              <p
                className="
                  text-green-300
                  font-black
                  uppercase
                  tracking-wider
                "
              >
                Your Current Plan
              </p>

              <h2
                className="
                  text-4xl
                  font-black
                  mt-2
                "
              >
                {currentPlan.toUpperCase()}
              </h2>

            </div>

            <div
              className="
                px-5
                py-3
                rounded-full
                bg-green-500/10
                border
                border-green-500/20
                text-green-300
                font-black
              "
            >
              ACTIVE
            </div>

          </div>

        </div>

        {/* PRICING CARDS */}

        <div
          className="
            grid
            xl:grid-cols-3
            gap-8
          "
        >

          {plans.map((plan) => (

            <div
              key={plan.name}
              className={`
                relative
                rounded-[36px]
                border
                ${plan.border}
                bg-[linear-gradient(180deg,#0b1220_0%,#091525_100%)]
                p-10
                overflow-hidden
                backdrop-blur-xl
                transition-all
                hover:scale-[1.02]
                hover:shadow-[0_0_60px_rgba(34,211,238,0.12)]

                ${
                  plan.featured
                    ? `
                      scale-[1.03]
                      shadow-[0_0_60px_rgba(34,211,238,0.18)]
                    `
                    : ""
                }
              `}
            >

              {/* CARD GLOW */}

              <div
                className={`
                  absolute
                  inset-0
                  bg-gradient-to-br
                  ${plan.glow}
                  opacity-40
                `}
              />

              <div className="relative z-10">

                {/* BADGE */}

                {plan.featured && (

                  <div
                    className="
                      inline-flex
                      items-center
                      gap-2
                      rounded-full
                      border
                      border-cyan-400/20
                      bg-cyan-500/10
                      px-4
                      py-2
                      mb-6
                    "
                  >
                    <Sparkles
                      size={16}
                      className="
                        text-cyan-300
                      "
                    />

                    <span
                      className="
                        text-sm
                        font-black
                        text-cyan-300
                      "
                    >
                      MOST POPULAR
                    </span>
                  </div>
                )}

                {/* TITLE */}

                <div
                  className="
                    flex
                    items-center
                    justify-between
                    mb-6
                  "
                >

                  <h2
                    className="
                      text-4xl
                      font-black
                    "
                  >
                    {plan.name}
                  </h2>

                  <div
                    className="
                      h-14
                      w-14
                      rounded-2xl
                      bg-cyan-500/10
                      border
                      border-cyan-500/20
                      flex
                      items-center
                      justify-center
                    "
                  >
                    {
                      plan.name === "Enterprise"
                      ? (
                        <Shield
                          className="
                            text-fuchsia-300
                          "
                        />
                      ) : plan.name === "Pro"
                      ? (
                        <Rocket
                          className="
                            text-cyan-300
                          "
                        />
                      ) : (
                        <Cpu
                          className="
                            text-slate-300
                          "
                        />
                      )
                    }
                  </div>
                </div>

                {/* PRICE */}

                <div className="mb-8">

                  <div
                    className="
                      flex
                      items-end
                      gap-2
                    "
                  >
                    <span
                      className="
                        text-6xl
                        font-black
                      "
                    >
                      {plan.price}
                    </span>

                    <span
                      className="
                        text-slate-400
                        mb-2
                      "
                    >
                      /month
                    </span>
                  </div>

                  <p
                    className="
                      mt-3
                      text-slate-400
                    "
                  >
                    {plan.description}
                  </p>
                </div>

                {/* FEATURES */}

                <div
                  className="
                    space-y-4
                    mb-10
                  "
                >

                  {plan.features.map(
                    (feature) => (

                    <div
                      key={feature}
                      className="
                        flex
                        items-center
                        gap-3
                      "
                    >
                      <CheckCircle2
                        size={18}
                        className="
                          text-cyan-300
                          shrink-0
                        "
                      />

                      <span
                        className="
                          text-slate-200
                        "
                      >
                        {feature}
                      </span>
                    </div>

                  ))}
                </div>

                {/* BUTTON */}

                <button

                  disabled={
                    currentPlan ===
                    plan.name.toLowerCase()
                  }

                  onClick={() =>

                    plan.planKey &&
                    handleCheckout(
                      plan.planKey
                    )

                  }

                  className={`

                    w-full
                    py-4
                    rounded-2xl
                    font-black
                    text-lg
                    transition-all

                    ${
                      currentPlan ===
                      plan.name.toLowerCase()

                      ? `
                        bg-green-600
                        text-white
                        cursor-not-allowed
                      `

                      : `
                        bg-cyan-400
                        text-black
                        hover:scale-[1.02]
                        hover:shadow-[0_0_30px_rgba(34,211,238,0.4)]
                      `
                    }
                  `}
                >

                  {
                    currentPlan ===
                    plan.name.toLowerCase()

                      ? "Current Plan"

                      : plan.button
                  }

                </button>
              </div>
            </div>

          ))}
        </div>
      </div>
    </div>
  );
}