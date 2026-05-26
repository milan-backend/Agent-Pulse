"use client";

import {
  Suspense,
  useEffect,
  useState,
} from "react";

import {
  useSearchParams,
} from "next/navigation";

import Link from "next/link";

import {
  ShieldCheck,
  XCircle,
  Loader2,
  ArrowRight,
  Activity,
} from "lucide-react";

import {
  verifyEmail,
} from "@/components/api";



function VerifyEmailContent() {

  const searchParams =
    useSearchParams();

  const token =
    searchParams.get(
      "token"
    ) || "";

  const [loading, setLoading] =
    useState(true);

  const [success, setSuccess] =
    useState(false);

  const [message, setMessage] =
    useState(
      "Verifying your email..."
    );

  useEffect(() => {

    async function verify() {

      if (!token) {

        setLoading(false);

        setSuccess(false);

        setMessage(
          "Invalid verification token"
        );

        return;
      }

      try {

        const response =
          await verifyEmail(
            token
          );

        setSuccess(true);

        setMessage(
          response?.message ||
          "Email verified successfully"
        );

      } catch (err: any) {

        setSuccess(false);

        setMessage(
          err?.message ||
          "Verification failed"
        );

      } finally {

        setLoading(false);
      }
    }

    verify();

  }, [token]);

  return (

    <div
      className="
        min-h-screen
        bg-[#020817]
        overflow-hidden
        relative
        flex
        items-center
        justify-center
        px-6
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
          max-w-xl
          rounded-[40px]
          border
          border-cyan-500/20
          bg-[linear-gradient(180deg,#071120_0%,#091525_100%)]
          p-10
          overflow-hidden
          text-center
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

          {/* LOGO */}

          <div
            className="
              flex
              flex-col
              items-center
              justify-center
            "
          >

            <div
              className="
                h-24
                w-24
                rounded-3xl
                border
                border-cyan-500/20
                bg-cyan-500/10
                flex
                items-center
                justify-center
              "
            >

              <Activity
                className="
                  text-cyan-300
                "
                size={42}
              />

            </div>

            <h1
              className="
                text-5xl
                font-black
                mt-6
              "
            >

              <span className="text-cyan-400">
                Agent
              </span>

              <span className="text-white">
                Pulse
              </span>

            </h1>

          </div>

          {/* STATUS ICON */}

          <div className="mt-10 flex justify-center">

            {
              loading ? (

                <Loader2
                  className="
                    animate-spin
                    text-cyan-400
                  "
                  size={70}
                />

              ) : success ? (

                <ShieldCheck
                  className="
                    text-green-400
                  "
                  size={70}
                />

              ) : (

                <XCircle
                  className="
                    text-red-400
                  "
                  size={70}
                />

              )
            }

          </div>

          {/* TITLE */}

          <h2
            className="
              mt-8
              text-4xl
              font-black
              text-white
            "
          >

            {
              loading
                ? "Verifying..."
                : success
                ? "Email Verified"
                : "Verification Failed"
            }

          </h2>

          {/* MESSAGE */}

          <p
            className="
              mt-4
              text-slate-400
              text-lg
              leading-relaxed
            "
          >
            {message}
          </p>

          {/* BUTTON */}

          {
            !loading && success && (

              <Link
                href="/login"
                className="
                  inline-flex
                  items-center
                  gap-3
                  mt-10
                  rounded-3xl
                  bg-cyan-500
                  hover:bg-cyan-400
                  transition-all
                  px-8
                  py-4
                  text-black
                  font-black
                  text-lg
                "
              >

                Continue to Login

                <ArrowRight
                  size={22}
                />

              </Link>
            )
          }

        </div>

      </div>

    </div>
  );
}



export default function VerifyEmailPage() {

  return (

    <Suspense fallback={null}>

      <VerifyEmailContent />

    </Suspense>
  );
}