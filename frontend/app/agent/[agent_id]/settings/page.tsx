"use client";

import Link from "next/link";

import { useParams } from "next/navigation";

import { useEffect, useState } from "react";

import {
  Copy,
  Check,
} from "lucide-react";

import { toast } from "sonner";

import {
  getAgent,
  regenerateAgentKey,
  updateAgentSettings,
  pauseAgentMission,
  resumeAgentMission,
  killAgentMission,
} from "@/components/api";

export default function AgentSettingsPage() {

  const params = useParams();

  const agentId =
    params.agent_id as string;

  const [loading, setLoading] =
    useState(true);

  const [copied, setCopied] =
    useState(false);

  const [apiKey, setApiKey] =
    useState("");

  const [agentName, setAgentName] =
    useState("");

  const [maxSteps, setMaxSteps] =
    useState<number>(20);

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

  const [saving, setSaving] =
    useState(false);

  const [regenerating, setRegenerating] =
    useState(false);

  const [actionLoading, setActionLoading] =
    useState<string | null>(null);

  useEffect(() => {

    if (agentId) {

      fetchAgent();
    }

  }, [agentId]);

  async function fetchAgent() {

    try {

      setLoading(true);

      const response =
        await getAgent(agentId);

      const agent =
        response?.agent || response;

      const policy =
        response?.policy || {};

      setAgentName(
        agent?.name || "Agent"
      );

      setMaxSteps(
        Number(
          policy?.max_steps
        ) || 20
      );

      setMaxCost(
        Number(
          policy?.max_cost
        ) || 5
      );

      setMaxRetries(
        Number(
          policy?.max_retries
        ) || 3
      );

      setMaxRepeatedTasks(
        Number(
          policy?.max_repeated_tasks
        ) || 3
      );

      setIsActive(
        Boolean(
          agent?.is_active
        )
      );

    } catch (error) {

      console.error(error);

      toast.error(
        "Failed to load agent settings"
      );

    } finally {

      setLoading(false);
    }
  }

  async function regenerateKey() {

    try {

      setRegenerating(true);

      const data =
        await regenerateAgentKey(
          agentId
        );

      setApiKey(
        data?.api_key || ""
      );

      toast.success(
        "API Key regenerated successfully"
      );

    } catch (error) {

      console.error(error);

      toast.error(
        "Failed to regenerate API key"
      );

    } finally {

      setRegenerating(false);
    }
  }

  async function copyApiKey() {

    if (!apiKey) return;

    await navigator.clipboard.writeText(
      apiKey
    );

    setCopied(true);

    toast.success(
      "API Key copied"
    );

    setTimeout(() => {

      setCopied(false);

    }, 2000);
  }

  async function saveSettings() {

    if (
      maxSteps < 1 ||
      maxRetries < 0 ||
      maxRepeatedTasks < 0 ||
      maxCost < 0
    ) {

      toast.error(
        "Invalid runtime limits"
      );

      return;
    }

    try {

      setSaving(true);

      await updateAgentSettings(
        agentId,
        {
          max_cost: maxCost,
          max_steps: maxSteps,
          max_retries: maxRetries,
          max_repeated_tasks:
            maxRepeatedTasks,
        }
      );

      toast.success(
        "Settings updated successfully"
      );

    } catch (error) {

      console.error(error);

      toast.error(
        "Failed to save settings"
      );

    } finally {

      setSaving(false);
    }
  }

  async function pauseAgent() {

    try {

      setActionLoading("pause");

      await pauseAgentMission(
        agentId
      );

      setIsActive(false);

      toast.success(
        "Agent paused"
      );

    } catch (error) {

      console.error(error);

      toast.error(
        "Failed to pause agent"
      );

    } finally {

      setActionLoading(null);
    }
  }

  async function resumeAgent() {

    try {

      setActionLoading("resume");

      await resumeAgentMission(
        agentId
      );

      setIsActive(true);

      toast.success(
        "Agent resumed"
      );

    } catch (error) {

      console.error(error);

      toast.error(
        "Failed to resume agent"
      );

    } finally {

      setActionLoading(null);
    }
  }

  async function killAgent() {

    const confirmed =
      window.confirm(
        "Are you sure you want to kill this agent?"
      );

    if (!confirmed) {

      return;
    }

    try {

      setActionLoading("kill");

      await killAgentMission(
        agentId
      );

      toast.success(
        "Agent killed successfully"
      );

    } catch (error) {

      console.error(error);

      toast.error(
        "Failed to kill agent"
      );

    } finally {

      setActionLoading(null);
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

        <div
          className="
            flex
            items-center
            gap-4
            rounded-3xl
            border
            border-cyan-500/20
            bg-cyan-500/10
            px-8
            py-6
          "
        >

          <div
            className="
              h-6
              w-6
              rounded-full
              border-2
              border-cyan-300/20
              border-t-cyan-300
              animate-spin
            "
          />

          <span
            className="
              text-xl
              font-bold
              text-cyan-300
            "
          >
            Loading Runtime Settings...
          </span>

        </div>

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
          items-start
          justify-between
          gap-6
          flex-wrap
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
            {agentName} Settings
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

          <div
            className={`
              inline-flex
              items-center
              gap-3
              rounded-full
              border
              px-5
              py-3
              mt-5

              ${
                isActive
                  ? `
                    border-green-500/20
                    bg-green-500/10
                    text-green-300
                  `
                  : `
                    border-red-500/20
                    bg-red-500/10
                    text-red-300
                  `
              }
            `}
          >

            <div
              className={`
                h-2
                w-2
                rounded-full

                ${
                  isActive
                    ? "bg-green-400"
                    : "bg-red-400"
                }
              `}
            />

            <span className="font-bold">

              {
                isActive
                  ? "AGENT ACTIVE"
                  : "AGENT PAUSED"
              }

            </span>

          </div>

        </div>

        <div
          className="
            flex
            items-center
            gap-4
            flex-wrap
          "
        >

          <button
            onClick={fetchAgent}
            className="
              rounded-2xl
              border
              border-cyan-500/20
              bg-cyan-500/10
              px-6
              py-4
              font-bold
              text-cyan-300
              hover:bg-cyan-500/20
              transition-all
            "
          >

            Refresh

          </button>

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
              mt-6
              rounded-2xl
              border
              border-yellow-500/20
              bg-yellow-500/10
              p-4
            "
          >

            <p
              className="
                text-sm
                text-yellow-200
                leading-relaxed
              "
            >

              API keys are only visible once
              after regeneration. Store them
              securely.

            </p>

          </div>

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
            disabled={regenerating}
            className="
              mt-8
              w-full
              rounded-2xl
              bg-cyan-400
              py-5
              font-black
              text-black
              disabled:opacity-50
              disabled:cursor-not-allowed
            "
          >
            {
              regenerating
                ? "Regenerating..."
                : "Regenerate API Key"
            }
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
                min={1}
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
                  appearance-none
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
                min={1}
                step="0.01"
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
                  appearance-none
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
                min={1}
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
                  appearance-none
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
                min={1}
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
                  appearance-none
                  rounded-2xl
                  bg-black
                  p-5
                  outline-none
                "
              />

            </div>

            <button
              onClick={saveSettings}
              disabled={saving}
              className="
                w-full
                rounded-2xl
                bg-cyan-400
                py-5
                font-black
                text-black
                disabled:opacity-50
                disabled:cursor-not-allowed
              "
            >
              {
                saving
                  ? "Saving Runtime Settings..."
                  : "Save Settings"
              }
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
            mt-8
            rounded-2xl
            border
            border-red-500/20
            bg-red-500/10
            p-5
          "
        >

          <p
            className="
              text-red-200
              leading-relaxed
            "
          >

            Killing an agent will immediately
            terminate all active missions
            and runtime execution processes.

          </p>

        </div>

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
            disabled={
              actionLoading === "kill"
            }
            className="
              rounded-2xl
              bg-red-500
              py-8
              text-3xl
              font-black
              disabled:opacity-50
              disabled:cursor-not-allowed
            "
          >
            {
              actionLoading === "kill"
                ? "STOPPING..."
                : "KILL AGENT RUNTIME"
            }
          </button>

          <button
            onClick={
              isActive
                ? pauseAgent
                : resumeAgent
            }
            disabled={
              actionLoading === "pause" ||
              actionLoading === "resume"
            }
            className="
              rounded-2xl
              bg-green-500
              py-8
              text-3xl
              font-black
              disabled:opacity-50
              disabled:cursor-not-allowed
            "
          >
            {
              actionLoading === "pause"
                ? "PAUSING..."
                : actionLoading === "resume"
                ? "RESUMING..."
                : isActive
                ? "PAUSE AGENT"
                : "RESUME AGENT"
            }
          </button>

        </div>

      </div>

    </div>
  );
}