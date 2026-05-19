"use client";

import {API_URL} from 
"@/components/api";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import {
  Copy,
  Check,
} from "lucide-react";

export default function AgentSettingsPage() {
  const params = useParams();

  const agentId = params.agent_id;

  const [loading, setLoading] =
    useState(true);

  const [copied, setCopied] =
    useState(false);

  const [apiKey, setApiKey] =
    useState("");

  const [maxSteps, setMaxSteps] =
    useState<number>(20);

  const [maxRuntime, setMaxRuntime] =
    useState<number>(2);

  const [maxCost, setMaxCost] =
    useState<number>(5);

  const [maxRetries, setMaxRetries] =
    useState<number>(3);

  const [
    maxRepeatedTasks,
    setMaxRepeatedTasks,
  ] = useState<number>(3);

  const [isActive, setIsActive] =
    useState(true);

  useEffect(() => {
    fetchAgent();
  }, []);

  async function fetchAgent() {
    try {
      const token =
        localStorage.getItem("token");

      const workspaceId =
        localStorage.getItem(
          "workspace_id"
        );

      const response =
        await fetch(
          `${API_URL}/dashboard/agent/${agentId}`,
          {
            headers: {
              Authorization:
                `Bearer ${token}`,

              "workspace-id":
                workspaceId || "",
            },
          }
        );

      const data =
        await response.json();

      setMaxSteps(
        Number(data.max_steps) || 20
      );

      setMaxCost(
        Number(data.max_cost) || 5
      );

      setMaxRetries(
        Number(data.max_retries) || 3
      );

      setMaxRepeatedTasks(
        Number(
          data.max_repeated_tasks
        ) || 3
      );

      setIsActive(
        data.is_active
      );
    } catch (error) {
      console.log(error);
    } finally {
      setLoading(false);
    }
  }

  async function regenerateKey() {
    try {
      const token =
        localStorage.getItem("token");

      const workspaceId =
        localStorage.getItem(
          "workspace_id"
        );

      const response =
        await fetch(
          `${API_URL}/agents/regenerate-key/${agentId}`,
          {
            method: "POST",

            headers: {
              Authorization:
                `Bearer ${token}`,

              "workspace-id":
                workspaceId || "",
            },
          }
        );

      const data =
        await response.json();

      if (!response.ok) {
        alert(
          data.detail ||
            "Failed to regenerate key"
        );

        return;
      }

      setApiKey(
        data.api_key
      );

      alert(
        "API Key Regenerated"
      );
    } catch (error) {
      console.error(error);

      alert(
        "Failed to regenerate key"
      );
    }
  }

  async function copyApiKey() {
    if (!apiKey) return;

    await navigator.clipboard.writeText(
      apiKey
    );

    setCopied(true);

    setTimeout(() => {
      setCopied(false);
    }, 2000);
  }

  async function saveSettings() {
    try {
      const token =
        localStorage.getItem("token");

      const workspaceId =
        localStorage.getItem(
          "workspace_id"
        );

      const response =
        await fetch(
          `${API_URL}/agents/${agentId}`,
          {
            method: "PUT",

            headers: {
              "Content-Type":
                "application/json",

              Authorization:
                `Bearer ${token}`,

              "workspace-id":
                workspaceId || "",
            },

            body: JSON.stringify({
              max_cost: maxCost,
              max_steps: maxSteps,
              max_retries: maxRetries,
              max_repeated_tasks:
                maxRepeatedTasks,
            }),
          }
        );

      const data =
        await response.json();

      if (!response.ok) {
        alert(
          data.detail ||
            "Failed to update settings"
        );

        return;
      }

      alert(
        "Settings Updated Successfully"
      );
    } catch (error) {
      console.error(error);

      alert(
        "Failed to save settings"
      );
    }
  }

  async function pauseAgent() {
    try {
      const token =
        localStorage.getItem("token");

      const workspaceId =
        localStorage.getItem(
          "workspace_id"
        );

      const response =
        await fetch(
          `${API_URL}/mission-control/pause/${agentId}`,
          {
            method: "POST",

            headers: {
              Authorization:
                `Bearer ${token}`,

              "workspace-id":
                workspaceId || "",
            },
          }
        );

      const data =
        await response.json();

      if (!response.ok) {
        alert(
          data.detail ||
            "Failed to pause agent"
        );

        return;
      }

      setIsActive(false);

      alert(
        "Agent Paused"
      );
    } catch (error) {
      console.error(error);

      alert(
        "Failed to pause agent"
      );
    }
  }

  async function resumeAgent() {
    try {
      const token =
        localStorage.getItem("token");

      const workspaceId =
        localStorage.getItem(
          "workspace_id"
        );

      const response =
        await fetch(
          `${API_URL}/mission-control/resume/${agentId}`,
          {
            method: "POST",

            headers: {
              Authorization:
                `Bearer ${token}`,

              "workspace-id":
                workspaceId || "",
            },
          }
        );

      const data =
        await response.json();

      if (!response.ok) {
        alert(
          data.detail ||
            "Failed to resume agent"
        );

        return;
      }

      setIsActive(true);

      alert(
        "Agent Resumed"
      );
    } catch (error) {
      console.error(error);

      alert(
        "Failed to resume agent"
      );
    }
  }

  async function killAgent() {
    try {
      const token =
        localStorage.getItem("token");

      const workspaceId =
        localStorage.getItem(
          "workspace_id"
        );

      const response =
        await fetch(
        `${API_URL}/mission-control/kill/${agentId}`,
          {
            method: "POST",

            headers: {
              Authorization:
                `Bearer ${token}`,

              "workspace-id":
                workspaceId || "",
            },
          }
        );

      const data =
        await response.json();

      if (!response.ok) {
        alert(
          data.detail ||
            "Failed to kill agent"
        );

        return;
      }

      alert(
        "Agent Killed"
      );
    } catch (error) {
      console.error(error);

      alert(
        "Failed to kill agent"
      );
    }
  }

  if (loading) {
    return (
      <div
        className="
          min-h-screen
          bg-[#071018]
          text-white
          flex
          items-center
          justify-center
        "
      >
        Loading...
      </div>
    );
  }

  return (
    <div
      className="
        min-h-screen
        bg-[#071018]
        text-white
        p-8
      "
    >
      {/* HEADER */}

      <div
        className="
          mb-10
          flex
          items-center
          justify-between
        "
      >
        <div>
          <h1
            className="
              text-6xl
              font-black
              text-cyan-400
            "
          >
            Settings
          </h1>

          <p
            className="
              mt-2
              text-gray-400
            "
          >
            Manage runtime controls
            and emergency systems.
          </p>
        </div>

        <Link
          href={`/agent/${agentId}`}
          className="
            rounded-2xl
            border
            border-cyan-400
            px-8
            py-4
            font-bold
            hover:bg-cyan-400
            hover:text-black
            transition
          "
        >
          Back To Agent
        </Link>
      </div>

      {/* TOP GRID */}

      <div
        className="
          grid
          gap-8
          lg:grid-cols-2
        "
      >
        {/* API SECURITY */}

        <div
          className="
            rounded-3xl
            border
            border-cyan-500/30
            bg-[#09131f]
            p-8
          "
        >
          <h2
            className="
              text-5xl
              font-black
              text-cyan-400
            "
          >
            API Security
          </h2>

          <p
            className="
              mt-3
              text-gray-400
            "
          >
            Generate secure runtime API keys.
          </p>

          <div
            className="
              mt-8
              rounded-2xl
              bg-black
              p-6
              break-all
              text-green-400
              font-bold
              flex
              items-center
              justify-between
              gap-4
            "
          >
            <span>
              {apiKey ||
                "Create New API Key"}
            </span>

            {apiKey && (
              <button
                onClick={copyApiKey}
                className="
                  shrink-0
                  rounded-xl
                  bg-cyan-500/20
                  p-3
                  hover:bg-cyan-500/30
                "
              >
                {copied
                  ? <Check size={18} />
                  : <Copy size={18} />}
              </button>
            )}
          </div>

          <button
            onClick={regenerateKey}
            className="
              mt-8
              w-full
              rounded-2xl
              bg-cyan-400
              py-5
              font-black
              text-black
            "
          >
            Regenerate API Key
          </button>
        </div>

        {/* BUDGET CONTROLS */}

        <div
          className="
            rounded-3xl
            border
            border-cyan-500/30
            bg-[#09131f]
            p-8
          "
        >
          <h2
            className="
              text-5xl
              font-black
              text-cyan-400
            "
          >
            Budget Controls
          </h2>

          <p
            className="
              mt-3
              text-gray-400
            "
          >
            Configure mission safety
            limits and runtime caps.
          </p>

          <div
            className="
              mt-8
              space-y-6
            "
          >
            <div>
              <p className="mb-2">
                Max Mission Steps
              </p>

              <input
                type="number"
                value={maxSteps}
                onChange={(e) =>
                  setMaxSteps(
                    Number(
                      e.target.value
                    ) || 0
                  )
                }
                className="
                  w-full
                  rounded-2xl
                  bg-black
                  p-5
                  outline-none
                "
              />
            </div>

            <div>
              <p className="mb-2">
                Max Runtime (mins)
              </p>

              <input
                type="number"
                value={maxRuntime}
                onChange={(e) =>
                  setMaxRuntime(
                    Number(
                      e.target.value
                    ) || 0
                  )
                }
                className="
                  w-full
                  rounded-2xl
                  bg-black
                  p-5
                  outline-none
                "
              />
            </div>

            <div>
              <p className="mb-2">
                Max Cost ($)
              </p>

              <input
                type="number"
                value={maxCost}
                onChange={(e) =>
                  setMaxCost(
                    Number(
                      e.target.value
                    ) || 0
                  )
                }
                className="
                  w-full
                  rounded-2xl
                  bg-black
                  p-5
                  outline-none
                "
              />
            </div>

            <div>
              <p className="mb-2">
                Max Retries
              </p>

              <input
                type="number"
                value={maxRetries}
                onChange={(e) =>
                  setMaxRetries(
                    Number(
                      e.target.value
                    ) || 0
                  )
                }
                className="
                  w-full
                  rounded-2xl
                  bg-black
                  p-5
                  outline-none
                "
              />
            </div>

            <div>
              <p className="mb-2">
                Max Repeated Tasks
              </p>

              <input
                type="number"
                value={
                  maxRepeatedTasks
                }
                onChange={(e) =>
                  setMaxRepeatedTasks(
                    Number(
                      e.target.value
                    ) || 0
                  )
                }
                className="
                  w-full
                  rounded-2xl
                  bg-black
                  p-5
                  outline-none
                "
              />
            </div>

            <button
              onClick={saveSettings}
              className="
                w-full
                rounded-2xl
                bg-cyan-400
                py-5
                font-black
                text-black
              "
            >
              Save Settings
            </button>
          </div>
        </div>
      </div>

      {/* DANGER ZONE */}

      <div
        className="
          mt-10
          rounded-3xl
          border
          border-red-500/40
          bg-[#1a0507]
          p-8
        "
      >
        <h2
          className="
            text-5xl
            font-black
            text-red-400
          "
        >
          Danger Zone
        </h2>

        <p
          className="
            mt-3
            text-gray-400
          "
        >
          Emergency runtime controls.
        </p>

        <div
          className="
            mt-10
            grid
            gap-8
            lg:grid-cols-2
          "
        >
          <button
            onClick={killAgent}
            className="
              rounded-2xl
              bg-red-500
              py-8
              text-3xl
              font-black
            "
          >
            STOP AGENT
          </button>

          <button
            onClick={
              isActive
                ? pauseAgent
                : resumeAgent
            }
            className="
              rounded-2xl
              bg-green-500
              py-8
              text-3xl
              font-black
            "
          >
            {isActive
              ? "PAUSE AGENT"
              : "RESUME AGENT"}
          </button>
        </div>
      </div>
    </div>
  );
}