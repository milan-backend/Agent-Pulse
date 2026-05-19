"use client";

import { useEffect, useState } from "react";

export default function SelectWorkspacePage() {

  const [workspaces, setWorkspaces] =
    useState<any[]>([]);

  useEffect(() => {

    const stored =
      localStorage.getItem(
        "workspaces"
      );

    if (stored) {

      setWorkspaces(
        JSON.parse(stored)
      );
    }

  }, []);

  function chooseWorkspace(
    workspace: any
  ) {

    localStorage.setItem(
      "workspace_id",
      workspace.workspace_id
    );

    localStorage.setItem(
      "role",
      workspace.role
    );

    window.location.href =
      "/dashboard";
  }

  return (

    <div
      className="
        min-h-screen
        bg-black
        text-white
        flex
        items-center
        justify-center
        p-8
      "
    >

      <div
        className="
          w-full
          max-w-2xl
        "
      >

        <h1
          className="
            text-5xl
            font-black
            mb-10
          "
        >
          Choose Workspace
        </h1>

        <div className="space-y-5">

          {workspaces.map(
            (workspace, index) => (

              <button
                key={index}
                onClick={() =>
                  chooseWorkspace(
                    workspace
                  )
                }
                className="
                  w-full
                  rounded-3xl
                  border
                  border-cyan-500/20
                  bg-cyan-500/10
                  p-8
                  text-left
                  hover:bg-cyan-500/20
                  transition
                "
              >

                <h2
                  className="
                    text-2xl
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
                  Role:
                  {" "}
                  {workspace.role}
                </p>

              </button>
            )
          )}

        </div>

      </div>

    </div>
  );
}