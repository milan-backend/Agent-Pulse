"use client";

import {
  useEffect,
  useState,
} from "react";

import {
  useRouter,
} from "next/navigation";

import {
  Activity,
  ShieldCheck,
  ArrowRight,
  Building2,
  CheckCircle2,
} from "lucide-react";

import { toast } from "sonner";

export default function SelectWorkspacePage() {

  const router =
    useRouter();

  const [workspaces, setWorkspaces] =
    useState<any[]>([]);

  const [selecting, setSelecting] =
    useState<string | null>(null);

  useEffect(() => {

    const stored =
      localStorage.getItem(
        "workspaces"
      );

    const token =
      localStorage.getItem(
        "token"
      );

    if (!token) {

      router.push("/login");

      return;
    }

    if (!stored) {

      toast.error(
        "No workspaces found"
      );

      router.push("/login");

      return;
    }

    try {

      const parsed =
        JSON.parse(stored);

      setWorkspaces(parsed);

    } catch {

      toast.error(
        "Invalid workspace session"
      );

      router.push("/login");
    }

  }, [router]);

  function chooseWorkspace(
    workspace: any
  ) {

    setSelecting(
      workspace.workspace_id
    );

    localStorage.setItem(
      "workspace_id",
      workspace.workspace_id
    );

    localStorage.setItem(
      "role",
      workspace.role
    );

    toast.success(

      `Workspace selected: ${workspace.workspace_name}`
    );

    setTimeout(() => {

      router.push(
        "/dashboard"
      );

    }, 800);
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
        py-20
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
          max-w-3xl
          rounded-[40px]
          border
          border-cyan-500/20
          bg-[linear-gradient(180deg,#071120_0%,#091525_100%)]
          p-10
          overflow-hidden
          animate-[fadeIn_.5s_ease]
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
                "
              >
                Select Workspace
              </h1>

              <p
                className="
                  mt-3
                  text-slate-400
                  text-lg
                "
              >
                Choose your AI runtime
                environment and mission
                control workspace.
              </p>

            </div>
          </div>

          {/* STATUS */}

          <div
            className="
              mt-8
              inline-flex
              items-center
              gap-3
              rounded-full
              border
              border-green-500/20
              bg-green-500/10
              px-5
              py-3
            "
          >

            <div
              className="
                h-2
                w-2
                rounded-full
                bg-green-400
                animate-pulse
              "
            />

            <span
              className="
                text-sm
                font-bold
                text-green-300
              "
            >
              MULTI WORKSPACE DETECTED
            </span>

          </div>

          {/* EMPTY */}

          {workspaces.length === 0 && (

            <div
              className="
                mt-10
                rounded-3xl
                border
                border-white/10
                bg-white/[0.03]
                p-14
                text-center
              "
            >

              <Building2
                size={60}
                className="
                  mx-auto
                  text-slate-600
                "
              />

              <h2
                className="
                  mt-6
                  text-3xl
                  font-black
                "
              >
                No Workspaces Found
              </h2>

              <p
                className="
                  mt-3
                  text-slate-500
                "
              >
                Your account does not
                belong to any workspace.
              </p>

            </div>
          )}

          {/* WORKSPACES */}

          <div className="mt-10 space-y-5">

            {workspaces.map(
              (
                workspace,
                index
              ) => (

                <button
                  key={index}
                  onClick={() =>
                    chooseWorkspace(
                      workspace
                    )
                  }
                  disabled={
                    selecting ===
                    workspace.workspace_id
                  }
                  className="
                    w-full
                    rounded-3xl
                    border
                    border-cyan-500/20
                    bg-cyan-500/10
                    hover:bg-cyan-500/20
                    transition-all
                    duration-300
                    p-8
                    text-left
                    group
                    disabled:opacity-50
                  "
                >

                  <div
                    className="
                      flex
                      items-start
                      justify-between
                      gap-5
                      flex-wrap
                    "
                  >

                    {/* LEFT */}

                    <div>

                      <div
                        className="
                          flex
                          items-center
                          gap-4
                        "
                      >

                        <div
                          className="
                            h-14
                            w-14
                            rounded-2xl
                            border
                            border-cyan-500/20
                            bg-cyan-500/10
                            flex
                            items-center
                            justify-center
                          "
                        >

                          <Building2
                            className="
                              text-cyan-300
                            "
                            size={26}
                          />

                        </div>

                        <div>

                          <h2
                            className="
                              text-3xl
                              font-black
                            "
                          >
                            {
                              workspace.workspace_name
                            }
                          </h2>

                          <p
                            className="
                              mt-2
                              text-slate-400
                            "
                          >
                            Workspace Role:
                            {" "}
                            {workspace.role}
                          </p>

                        </div>
                      </div>

                      {/* BADGES */}

                      <div
                        className="
                          mt-6
                          flex
                          items-center
                          gap-3
                          flex-wrap
                        "
                      >

                        <div
                          className="
                            rounded-full
                            border
                            border-green-500/20
                            bg-green-500/10
                            px-4
                            py-2
                            text-sm
                            font-bold
                            text-green-300
                            flex
                            items-center
                            gap-2
                          "
                        >

                          <ShieldCheck
                            size={16}
                          />

                          ACTIVE

                        </div>

                        <div
                          className="
                            rounded-full
                            border
                            border-cyan-500/20
                            bg-cyan-500/10
                            px-4
                            py-2
                            text-sm
                            font-bold
                            text-cyan-300
                          "
                        >
                          AI RUNTIME
                        </div>

                      </div>

                    </div>

                    {/* RIGHT */}

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

                      {
                        selecting ===
                        workspace.workspace_id

                          ? (

                            <CheckCircle2
                              className="
                                text-green-300
                              "
                              size={30}
                            />

                          )

                          : (

                            <ArrowRight
                              className="
                                text-cyan-300
                                group-hover:translate-x-1
                                transition-transform
                              "
                              size={30}
                            />

                          )
                      }

                    </div>

                  </div>

                </button>
              )
            )}

          </div>

        </div>
      </div>
    </div>
  );
}