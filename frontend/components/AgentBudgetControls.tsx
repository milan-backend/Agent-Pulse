"use client";

import { useState } from "react";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL;

export default function AgentBudgetControls({
  agentId,
  agent,
}: any) {

  const [maxSteps, setMaxSteps] =
    useState(
      agent?.max_steps || 0
    );

  const [
    maxRetries,
    setMaxRetries,
  ] = useState(
    agent?.max_retries || 0
  );

  const [maxCost, setMaxCost] =
    useState(
      agent?.max_cost || 0
    );

  const [loading, setLoading] =
    useState(false);

  async function updateBudget() {

    try {

      setLoading(true);

      const token =
        localStorage.getItem(
          "token"
        );

      const response =
        await fetch(
          `${API_URL}/update-budget/${agentId}`,
          {
            method: "PUT",

            headers: {
              Authorization:
                `Bearer ${token}`,

              "Content-Type":
                "application/json",
            },

            body: JSON.stringify({
              max_steps:
                maxSteps,

              max_retries:
                maxRetries,

              max_cost:
                maxCost,

              max_repeated_tasks:
                agent?.max_repeated_tasks ||
                5,
            }),
          }
        );

      if (!response.ok) {

        throw new Error(
          "Failed to update budget"
        );
      }

      alert(
        "Budget updated successfully"
      );

    } catch (error) {

      console.error(error);

      alert(
        "Failed to update budget"
      );

    } finally {

      setLoading(false);
    }
  }

  return (

    <div
      className="
        bg-[#111827]
        border
        border-cyan-500/20
        rounded-2xl
        p-6
      "
    >
      <h2
        className="
          text-2xl
          text-cyan-400
          font-bold
          mb-6
        "
      >
        Agent Budget Controls
      </h2>

      <div className="space-y-4">

        {/* MAX STEPS */}

        <input
          type="number"
          value={maxSteps}
          onChange={(e) =>
            setMaxSteps(
              Number(
                e.target.value
              )
            )
          }
          placeholder="Max Steps"
          className="
            w-full
            bg-[#1f2937]
            text-white
            p-3
            rounded-xl
          "
        />

        {/* MAX RETRIES */}

        <input
          type="number"
          value={maxRetries}
          onChange={(e) =>
            setMaxRetries(
              Number(
                e.target.value
              )
            )
          }
          placeholder="Max Retries"
          className="
            w-full
            bg-[#1f2937]
            text-white
            p-3
            rounded-xl
          "
        />

        {/* MAX COST */}

        <input
          type="number"
          value={maxCost}
          onChange={(e) =>
            setMaxCost(
              Number(
                e.target.value
              )
            )
          }
          placeholder="Max Cost"
          className="
            w-full
            bg-[#1f2937]
            text-white
            p-3
            rounded-xl
          "
        />

        {/* BUTTON */}

        <button
          onClick={updateBudget}
          disabled={loading}
          className="
            w-full
            bg-cyan-500
            hover:bg-cyan-600
            disabled:opacity-50
            text-black
            font-bold
            py-3
            rounded-xl
            transition-all
          "
        >
          {loading
            ? "Saving..."
            : "Save Agent Limits"}
        </button>
      </div>
    </div>
  );
}