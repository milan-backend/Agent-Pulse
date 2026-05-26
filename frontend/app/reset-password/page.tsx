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
  Lock,
  ShieldCheck,
  ArrowRight,
  Activity,
} from "lucide-react";

import {
  resetPassword,
} from "@/components/api";

import { toast } from "sonner";



function ResetPasswordContent() {

  const searchParams =
    useSearchParams();

  const token =
    searchParams.get(
      "token"
    ) || "";

  const [password, setPassword] =
    useState("");

  const [
    confirmPassword,
    setConfirmPassword,
  ] = useState("");

  const [loading, setLoading] =
    useState(false);

  const [success, setSuccess] =
    useState(false);

  useEffect(() => {

    if (!token) {

      toast.error(
        "Invalid reset token"
      );
    }

  }, [token]);

  async function handleReset(
    e: React.FormEvent
  ) {

    e.preventDefault();

    if (!password) {

      toast.error(
        "Password required"
      );

      return;
    }

    if (
      password !==
      confirmPassword
    ) {

      toast.error(
        "Passwords do not match"
      );

      return;
    }

    try {

      setLoading(true);

      const response =
        await resetPassword(
          token,
          password
        );

      setSuccess(true);

      toast.success(
        response?.message ||
        "Password reset successful"
      );

      setTimeout(() => {

        window.location.href =
          "/login";

      }, 2000);

    } catch (err: any) {

      toast.error(
        err?.message ||
        "Password reset failed"
      );

    } finally {

      setLoading(false);
    }
  }

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

        <div className="relative z-10">

          {/* HEADER */}

          <div
            className="
              flex
              items-center
              gap-5
            "
          >

            <div
              className="
                h-20
                w-20
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
                size={38}
              />

            </div>

            <div>

              <h1
                className="
                  text-5xl
                  font-black
                  leading-none
                "
              >

                <span className="text-cyan-400">
                  Agent
                </span>

                <span className="text-white">
                  Pulse
                </span>

              </h1>

              <p
                className="
                  mt-2
                  text-slate-400
                "
              >
                Secure Password Recovery
              </p>

            </div>

          </div>

          {/* TITLE */}

          <div className="mt-10">

            <h2
              className="
                text-4xl
                font-black
                text-white
              "
            >
              Reset Password
            </h2>

            <p
              className="
                mt-3
                text-slate-400
                text-lg
              "
            >
              Create a new secure password
              for your account.
            </p>

          </div>

          {/* FORM */}

          <form
            onSubmit={
              handleReset
            }
            className="
              mt-8
              space-y-6
            "
          >

            {/* PASSWORD */}

            <div>

              <label
                className="
                  text-sm
                  text-slate-400
                  mb-3
                  block
                "
              >
                New Password
              </label>

              <div className="relative">

                <Lock
                  className="
                    absolute
                    left-5
                    top-1/2
                    -translate-y-1/2
                    text-slate-500
                  "
                  size={20}
                />

                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) =>
                    setPassword(
                      e.target.value
                    )
                  }
                  placeholder="••••••••••"
                  className="
                    w-full
                    rounded-3xl
                    border
                    border-cyan-500/20
                    bg-[#0f172a]
                    px-14
                    py-5
                    text-white
                    text-lg
                    outline-none
                    transition-all
                    focus:border-cyan-400
                    focus:ring-4
                    focus:ring-cyan-500/10
                    placeholder:text-slate-500
                  "
                />

              </div>

            </div>

            {/* CONFIRM PASSWORD */}

            <div>

              <label
                className="
                  text-sm
                  text-slate-400
                  mb-3
                  block
                "
              >
                Confirm Password
              </label>

              <div className="relative">

                <ShieldCheck
                  className="
                    absolute
                    left-5
                    top-1/2
                    -translate-y-1/2
                    text-slate-500
                  "
                  size={20}
                />

                <input
                  type="password"
                  required
                  value={confirmPassword}
                  onChange={(e) =>
                    setConfirmPassword(
                      e.target.value
                    )
                  }
                  placeholder="••••••••••"
                  className="
                    w-full
                    rounded-3xl
                    border
                    border-cyan-500/20
                    bg-[#0f172a]
                    px-14
                    py-5
                    text-white
                    text-lg
                    outline-none
                    transition-all
                    focus:border-cyan-400
                    focus:ring-4
                    focus:ring-cyan-500/10
                    placeholder:text-slate-500
                  "
                />

              </div>

            </div>

            {/* BUTTON */}

            <button
              type="submit"
              disabled={
                loading ||
                success
              }
              className="
                w-full
                rounded-3xl
                bg-cyan-500
                hover:bg-cyan-400
                transition-all
                py-5
                text-black
                font-black
                text-lg
                flex
                items-center
                justify-center
                gap-3
                disabled:opacity-50
              "
            >

              {
                loading ? (

                  "Resetting Password..."

                ) : success ? (

                  <>
                    <ShieldCheck
                      size={22}
                    />

                    Password Updated
                  </>

                ) : (

                  <>
                    <ShieldCheck
                      size={22}
                    />

                    Reset Password

                    <ArrowRight
                      size={22}
                    />
                  </>
                )
              }

            </button>

          </form>

          {/* FOOTER */}

          <div
            className="
              mt-8
              text-center
              text-slate-400
            "
          >

            Remember your password?
            {" "}

            <Link
              href="/login"
              className="
                text-cyan-300
                hover:text-cyan-200
                font-bold
              "
            >
              Login
            </Link>

          </div>

        </div>

      </div>

    </div>
  );
}



export default function ResetPasswordPage() {

  return (

    <Suspense fallback={null}>

      <ResetPasswordContent />

    </Suspense>
  );
}