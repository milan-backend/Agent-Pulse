"use client";

import { API_URL } from 
"@/components/api";

import Link from "next/link";

import {
  useEffect,
  useState,
} from "react";

import {
  ChevronRight,
  Plus,
  Copy,
  X,
} from "lucide-react";

interface Agent {

  id: string;

  name: string;
}

export default function AgentsPage() {

  const [agents, setAgents] =
    useState<Agent[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [showModal, setShowModal] =
    useState(false);

  const [agentName, setAgentName] =
    useState("");

  const [creating, setCreating] =
    useState(false);

  const [newApiKey, setNewApiKey] =
    useState("");

  const [newAgentName, setNewAgentName] =
    useState("");

  const [role, setRole] =
    useState("");

  useEffect(() => {

    fetchAgents();

  }, []);

  async function fetchAgents() {

    try {

      const token =
        localStorage.getItem(
          "token"
        );

      const workspaceId =
        localStorage.getItem(
          "workspace_id"
        );

      const response =
        await fetch(
          `${API_URL}/dashboard/agents`,
          {
            headers: {

              Authorization:
                `Bearer ${token}`,

              "workspace-id":
                workspaceId || "",
            },
          }
        );

      if (!response.ok) {

        throw new Error(
          "Failed to fetch agents"
        );
      }

      const data =
        await response.json();

      console.log("Role =", data.role);

      setAgents(
        data.agents || []
      );

      setRole(
        data.role || "viewer"
      );

    } catch (error) {

      console.error(error);

    } finally {

      setLoading(false);
    }
  }

  async function createAgent() {

    try {

      setCreating(true);

      const token =
        localStorage.getItem(
          "token"
        );

      const workspaceId =
        localStorage.getItem(
          "workspace_id"
        );

      const response =
        await fetch(
          `${API_URL}/agents/`,
          {

            method: "POST",

            headers: {

              "Content-Type":
                "application/json",

              Authorization:
                `Bearer ${token}`,

              "workspace-id":
                workspaceId || "",
            },

            body: JSON.stringify({

              name: agentName
            }),
          }
        );

      if (!response.ok) {

        throw new Error(
          "Failed to create agent"
        );
      }

      const data =
        await response.json();

      setNewApiKey(
        data.api_key
      );

      setNewAgentName(
        data.agent_name
      );

      setAgentName("");

      fetchAgents();

    } catch (error) {

      console.error(error);

    } finally {

      setCreating(false);
    }
  }

  async function copyApiKey() {

    await navigator.clipboard.writeText(
      newApiKey
    );

    alert(
      "API Key copied"
    );
  }

  return (

    <main
      className="
        min-h-screen
        bg-[#050816]
        text-white
        p-10
      "
    >

      {/* HEADER */}

      <div
        className="
          mb-10
          flex
          items-center
          justify-between
          flex-wrap
          gap-6
        "
      >

        <div>

          <h1
            className="
              text-6xl
              font-black
              tracking-tight
            "
          >

            Agents

          </h1>

          <p
            className="
              mt-3
              text-zinc-400
              text-lg
            "
          >

            Runtime agent infrastructure overview.

          </p>

        </div>

        <div
          className="
            flex
            items-center
            gap-4
            flex-wrap
          "
        >

          {/* CREATE AGENT */}

          {(role === "admin" ||
            role === "operator") && (

            <button
              onClick={() =>
                setShowModal(true)
              }
              className="
                flex
                items-center
                gap-3
                rounded-2xl
                border
                border-cyan-500/20
                bg-cyan-500/10
                px-6
                py-4
                text-cyan-300
                transition
                hover:bg-cyan-500/20
              "
            >

              <Plus size={20} />

              <span
                className="
                  font-bold
                "
              >
                Create Agent
              </span>

            </button>
          )}

          {/* TOTAL */}

          <div
            className="
              rounded-3xl
              border
              border-cyan-500/20
              bg-cyan-500/10
              px-8
              py-6
            "
          >

            <p
              className="
                text-sm
                text-zinc-400
              "
            >

              Total Agents

            </p>

            <h2
              className="
                mt-2
                text-5xl
                font-black
                text-cyan-300
              "
            >

              {agents.length}

            </h2>

          </div>

        </div>

      </div>

      {/* LOADING */}

      {loading ? (

        <div
          className="
            rounded-3xl
            border
            border-cyan-500/10
            bg-[#08111f]
            p-10
            text-zinc-400
          "
        >

          Loading agents...

        </div>

      ) : agents.length === 0 ? (

        <div
          className="
            flex
            h-[400px]
            items-center
            justify-center
            rounded-3xl
            border
            border-cyan-500/10
            bg-[#08111f]
          "
        >

          <div className="text-center">

            <h2
              className="
                text-4xl
                font-black
                text-zinc-300
              "
            >

              No Agents Found

            </h2>

            <p
              className="
                mt-4
                text-zinc-500
              "
            >

              Create your first runtime agent.

            </p>

          </div>

        </div>

      ) : (

        <div
          className="
            grid
            gap-6
            md:grid-cols-2
            xl:grid-cols-3
          "
        >

          {agents.map(
            (agent) => (

              <Link
                key={agent.id}
                href={`/agent/${agent.id}`}
              >

                <div
                  className="
                    group
                    rounded-3xl
                    border
                    border-cyan-500/10
                    bg-[#08111f]
                    p-8
                    transition-all
                    hover:border-cyan-400/40
                    hover:bg-cyan-500/5
                  "
                >

                  <div
                    className="
                      flex
                      items-start
                      justify-between
                    "
                  >

                    <div>

                      <h2
                        className="
                          text-3xl
                          font-black
                          text-cyan-300
                        "
                      >

                        {agent.name}

                      </h2>

                      <p
                        className="
                          mt-4
                          break-all
                          text-sm
                          text-zinc-500
                        "
                      >

                        {agent.id}

                      </p>

                    </div>

                    <div
                      className="
                        rounded-2xl
                        border
                        border-cyan-500/20
                        bg-cyan-500/10
                        p-3
                        text-cyan-300
                        transition-all
                        group-hover:translate-x-1
                      "
                    >

                      <ChevronRight />

                    </div>

                  </div>

                </div>

              </Link>
            )
          )}

        </div>
      )}

      {/* MODAL */}

      {showModal && (

        <div
          className="
            fixed
            inset-0
            z-50
            flex
            items-center
            justify-center
            bg-black/70
            backdrop-blur-sm
            p-6
          "
        >

          <div
            className="
              w-full
              max-w-xl
              rounded-3xl
              border
              border-cyan-500/20
              bg-[#08111f]
              p-8
            "
          >

            {/* HEADER */}

            <div
              className="
                mb-8
                flex
                items-center
                justify-between
              "
            >

              <h2
                className="
                  text-4xl
                  font-black
                "
              >

                Create Agent

              </h2>

              <button
                onClick={() =>
                  setShowModal(false)
                }
                className="
                  rounded-xl
                  border
                  border-white/10
                  p-2
                  text-zinc-400
                  hover:bg-white/5
                "
              >

                <X />

              </button>

            </div>

            {/* FORM */}

            {!newApiKey ? (

              <>

                <input
                  value={agentName}
                  onChange={(e) =>
                    setAgentName(
                      e.target.value
                    )
                  }
                  placeholder="Agent Name"
                  className="
                    w-full
                    rounded-2xl
                    border
                    border-cyan-500/20
                    bg-black/30
                    px-5
                    py-4
                    text-lg
                    outline-none
                  "
                />

                <button
                  onClick={createAgent}
                  disabled={
                    creating ||
                    !agentName
                  }
                  className="
                    mt-6
                    w-full
                    rounded-2xl
                    bg-cyan-500
                    px-6
                    py-4
                    text-lg
                    font-black
                    text-black
                    transition
                    hover:bg-cyan-400
                    disabled:opacity-50
                  "
                >

                  {creating
                    ? "Creating..."
                    : "Create Agent"}

                </button>

              </>

            ) : (

              <>

                <div
                  className="
                    rounded-2xl
                    border
                    border-emerald-500/20
                    bg-emerald-500/10
                    p-6
                  "
                >

                  <h3
                    className="
                      text-2xl
                      font-black
                      text-emerald-300
                    "
                  >

                    Agent Created

                  </h3>

                  <p
                    className="
                      mt-2
                      text-zinc-400
                    "
                  >

                    Save this API key now.
                    You will not be able
                    to see it again.

                  </p>

                  <div
                    className="
                      mt-6
                      rounded-2xl
                      border
                      border-white/10
                      bg-black/30
                      p-5
                      break-all
                      text-sm
                    "
                  >

                    {newApiKey}

                  </div>

                  <button
                    onClick={copyApiKey}
                    className="
                      mt-5
                      flex
                      items-center
                      gap-3
                      rounded-2xl
                      border
                      border-cyan-500/20
                      bg-cyan-500/10
                      px-5
                      py-3
                      text-cyan-300
                    "
                  >

                    <Copy size={18} />

                    Copy API Key

                  </button>

                </div>

              </>
            )}

          </div>

        </div>
      )}

    </main>
  );
}