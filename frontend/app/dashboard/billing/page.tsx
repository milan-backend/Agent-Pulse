"use client";

import {
  createCheckout
} from "@/components/api";

const plans = [
  {
    name: "Free",
    price: "$0",
    features: [
      "1 Agent",
      "1 Team Member",
      "10 Runtime Hours"
    ],
    button: "Current Plan",
    disabled: true
  },
  {
    name: "Pro",
    price: "$29",
    features: [
      "10 Agents",
      "10 Team Members",
      "100 Runtime Hours"
    ],
    button: "Upgrade to Pro",
    planKey: "pro"
  },
  {
    name: "Enterprise",
    price: "$199",
    features: [
      "100 Agents",
      "100 Team Members",
      "10000 Runtime Hours"
    ],
    button: "Upgrade to Enterprise",
    planKey: "enterprise"
  }
];

export default function BillingPage() {

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
        bg-black
        text-white
        flex
        items-center
        justify-center
        p-10
      "
    >

      <div
        className="
          grid
          md:grid-cols-3
          gap-8
          w-full
          max-w-6xl
        "
      >

        {plans.map((plan) => (

          <div
            key={plan.name}
            className="
              border
              border-gray-800
              rounded-2xl
              p-8
              bg-zinc-900
            "
          >

            <h2
              className="
                text-3xl
                font-bold
                mb-4
              "
            >
              {plan.name}
            </h2>

            <p
              className="
                text-5xl
                font-bold
                mb-6
              "
            >
              {plan.price}
            </p>

            <ul
              className="
                space-y-3
                mb-8
              "
            >

              {plan.features.map(
                (feature) => (

                <li key={feature}>
                  ✅ {feature}
                </li>

              ))}
            </ul>

            <button

              disabled={plan.disabled}

              onClick={() =>
                handleCheckout(
                  plan.planKey!
                )
              }

              className="
                w-full
                bg-blue-600
                hover:bg-blue-700
                transition
                py-3
                rounded-xl
                font-semibold
                disabled:bg-gray-700
              "
            >

              {plan.button}

            </button>

          </div>

        ))}

      </div>

    </div>
  );
}