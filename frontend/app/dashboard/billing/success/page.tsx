"use client";

import Link from "next/link";

import {
  CheckCircle2,
  ArrowRight,
  Sparkles
} from "lucide-react";

export default function BillingSuccessPage() {

  return (

    <div
      className="
        min-h-screen
        bg-[#020817]
        flex
        items-center
        justify-center
        px-6
        relative
        overflow-hidden
      "
    >

      {/* BACKGROUND */}

      <div
        className="
          absolute
          top-0
          left-0
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
          right-0
          h-[500px]
          w-[500px]
          rounded-full
          bg-purple-500/10
          blur-3xl
        "
      />

      {/* CARD */}

      <div
        className="
          relative
          z-10
          w-full
          max-w-2xl
          rounded-[40px]
          border
          border-cyan-500/20
          bg-[linear-gradient(180deg,#071120_0%,#091525_100%)]
          p-12
          text-center
          overflow-hidden
        "
      >

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

        <div className="relative z-10">

          <div
            className="
              mx-auto
              flex
              h-28
              w-28
              items-center
              justify-center
              rounded-full
              bg-green-500/10
              border
              border-green-500/20
            "
          >
            <CheckCircle2
              className="text-green-400"
              size={58}
            />
          </div>

          <h1
            className="
              mt-10
              text-5xl
              font-black
              text-white
            "
          >
            Payment Successful
          </h1>

          <p
            className="
              mt-5
              text-xl
              text-slate-400
              leading-relaxed
            "
          >
            Your workspace subscription
            has been upgraded successfully.
          </p>

          <div
            className="
              mt-8
              inline-flex
              items-center
              gap-3
              rounded-full
              border
              border-cyan-500/20
              bg-cyan-500/10
              px-6
              py-3
            "
          >

            <Sparkles
              className="
                text-cyan-300
              "
              size={18}
            />

            <span
              className="
                text-sm
                font-bold
                text-cyan-300
              "
            >
              PREMIUM FEATURES ACTIVATED
            </span>

          </div>

          <div className="mt-12">

            <Link
              href="/dashboard"
              className="
                inline-flex
                items-center
                gap-3
                rounded-3xl
                bg-cyan-500
                hover:bg-cyan-400
                transition-all
                px-8
                py-5
                text-black
                font-black
                text-lg
              "
            >

              Go To Dashboard

              <ArrowRight
                size={22}
              />

            </Link>

          </div>

        </div>

      </div>

    </div>
  );
}