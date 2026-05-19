"use client";

import {API_URL} from 
"@/components/api";

import Link from "next/link";

import {
  useEffect,
  useState,
} from "react";

import {
  useParams,
} from "next/navigation";

import {
  ArrowLeft,
  CheckCircle2,
  XCircle,
  Clock3,
  Database,
  Cpu,
} from "lucide-react";

interface Task {

  step_id: string;

  task_name: string;

  status: string;

  input_data: any;

  output_data: any;

  error_message: string | null;

  retry_count: number;

  cache_hit: boolean;

  event_type: string | null;

  started_at: string | null;

  created_at: string | null;

  updated_at: string | null;
}

export default function AgentTasksPage() {

  const params =
    useParams();

  const agentId =
    params?.agent_id;

  const [tasks, setTasks] =
    useState<Task[]>([]);

  const [loading, setLoading] =
    useState(true);

  useEffect(() => {

    async function fetchTasks() {

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
            `${API_URL}/agent/${agentId}`,
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
            "Failed to fetch tasks"
          );
        }

        const data =
          await response.json();

        setTasks(
          data.tasks || []
        );

      } catch (error) {

        console.error(error);

      } finally {

        setLoading(false);
      }
    }

    if (agentId) {

      fetchTasks();
    }

  }, [agentId]);

  function getStatusColor(
    status: string
  ) {

    switch (status) {

      case "completed":

        return `
          border-green-500/20
          bg-green-500/10
          text-green-300
        `;

      case "failed":

        return `
          border-red-500/20
          bg-red-500/10
          text-red-300
        `;

      case "running":

        return `
          border-yellow-500/20
          bg-yellow-500/10
          text-yellow-300
        `;

      default:

        return `
          border-cyan-500/20
          bg-cyan-500/10
          text-cyan-300
        `;
    }
  }

  return (

    <main
      className="
        min-h-screen
        bg-[#020817]
        text-white
        p-8
      "
    >

      {/* HEADER */}

      <div
        className="
          flex
          items-center
          justify-between
          gap-6
          flex-wrap
        "
      >

        <div>

          <Link
            href={`/agent/${agentId}`}
            className="
              inline-flex
              items-center
              gap-2
              rounded-2xl
              border
              border-cyan-500/20
              bg-cyan-500/10
              px-5
              py-3
              text-cyan-300
              transition
              hover:bg-cyan-500/20
            "
          >

            <ArrowLeft size={18} />

            Back To Agent

          </Link>

          <h1
            className="
              mt-6
              text-6xl
              font-black
            "
          >

            Agent Tasks

          </h1>

          <p
            className="
              mt-3
              text-lg
              text-zinc-400
            "
          >

            Runtime execution history
            and telemetry.

          </p>

        </div>

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

            Total Tasks

          </p>

          <h2
            className="
              mt-2
              text-5xl
              font-black
              text-cyan-300
            "
          >

            {tasks.length}

          </h2>

        </div>

      </div>

      {/* LOADING */}

      {loading ? (

        <div
          className="
            mt-10
            rounded-3xl
            border
            border-cyan-500/10
            bg-[#08111f]
            p-10
            text-zinc-400
          "
        >

          Loading tasks...

        </div>

      ) : tasks.length === 0 ? (

        <div
          className="
            mt-10
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

            <Cpu
              size={48}
              className="
                mx-auto
                text-zinc-600
              "
            />

            <h2
              className="
                mt-6
                text-4xl
                font-black
              "
            >

              No Tasks Found

            </h2>

            <p
              className="
                mt-3
                text-zinc-500
              "
            >

              This agent has not
              executed any tasks yet.

            </p>

          </div>

        </div>

      ) : (

        <div
          className="
            mt-10
            space-y-6
          "
        >

          {tasks.map(
            (task) => (

              <div
                key={task.step_id}
                className="
                  rounded-3xl
                  border
                  border-cyan-500/10
                  bg-[#08111f]
                  p-8
                "
              >

                {/* TOP */}

                <div
                  className="
                    flex
                    items-start
                    justify-between
                    gap-6
                    flex-wrap
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

                      {task.task_name}

                    </h2>

                    <p
                      className="
                        mt-3
                        break-all
                        text-sm
                        text-zinc-500
                      "
                    >

                      {task.step_id}

                    </p>

                  </div>

                  {/* STATUS */}

                  <div
                    className={`
                      flex
                      items-center
                      gap-3
                      rounded-2xl
                      border
                      px-5
                      py-3
                      font-bold

                      ${getStatusColor(
                        task.status
                      )}
                    `}
                  >

                    {task.status ===
                    "completed" ? (

                      <CheckCircle2
                        size={18}
                      />

                    ) : task.status ===
                      "failed" ? (

                      <XCircle
                        size={18}
                      />

                    ) : (

                      <Clock3
                        size={18}
                      />

                    )}

                    {task.status}

                  </div>

                </div>

                {/* METADATA */}

                <div
                  className="
                    mt-8
                    grid
                    gap-5
                    md:grid-cols-3
                  "
                >

                  <InfoCard
                    title="Retry Count"
                    value={
                      task.retry_count
                    }
                  />

                  <InfoCard
                    title="Cache Hit"
                    value={
                      task.cache_hit
                        ? "YES"
                        : "NO"
                    }
                  />

                  <InfoCard
                    title="Event Type"
                    value={
                      task.event_type ||
                      "N/A"
                    }
                  />

                </div>

                {/* INPUT */}

                <div
                  className="
                    mt-8
                    rounded-3xl
                    border
                    border-white/10
                    bg-black/30
                    p-6
                  "
                >

                  <div
                    className="
                      flex
                      items-center
                      gap-3
                    "
                  >

                    <Database
                      size={18}
                      className="
                        text-cyan-300
                      "
                    />

                    <h3
                      className="
                        text-xl
                        font-black
                      "
                    >

                      Input Data

                    </h3>

                  </div>

                  <pre
                    className="
                      mt-5
                      overflow-x-auto
                      whitespace-pre-wrap
                      break-all
                      text-sm
                      text-zinc-300
                    "
                  >
                    {JSON.stringify(
                      task.input_data,
                      null,
                      2
                    )}
                  </pre>

                </div>

                {/* OUTPUT */}

                <div
                  className="
                    mt-6
                    rounded-3xl
                    border
                    border-white/10
                    bg-black/30
                    p-6
                  "
                >

                  <div
                    className="
                      flex
                      items-center
                      gap-3
                    "
                  >

                    <Cpu
                      size={18}
                      className="
                        text-green-300
                      "
                    />

                    <h3
                      className="
                        text-xl
                        font-black
                      "
                    >

                      Output Data

                    </h3>

                  </div>

                  <pre
                    className="
                      mt-5
                      overflow-x-auto
                      whitespace-pre-wrap
                      break-all
                      text-sm
                      text-zinc-300
                    "
                  >
                    {JSON.stringify(
                      task.output_data,
                      null,
                      2
                    )}
                  </pre>

                </div>

                {/* ERROR */}

                {task.error_message && (

                  <div
                    className="
                      mt-6
                      rounded-3xl
                      border
                      border-red-500/20
                      bg-red-500/10
                      p-6
                    "
                  >

                    <h3
                      className="
                        text-xl
                        font-black
                        text-red-300
                      "
                    >

                      Error Message

                    </h3>

                    <p
                      className="
                        mt-4
                        text-red-200
                      "
                    >

                      {task.error_message}

                    </p>

                  </div>
                )}

                {/* TIMESTAMPS */}

                <div
                  className="
                    mt-8
                    grid
                    gap-5
                    md:grid-cols-3
                  "
                >

                  <InfoCard
                    title="Started At"
                    value={
                      task.started_at
                        ? new Date(
                            task.started_at
                          ).toLocaleString()
                        : "N/A"
                    }
                  />

                  <InfoCard
                    title="Created At"
                    value={
                      task.created_at
                        ? new Date(
                            task.created_at
                          ).toLocaleString()
                        : "N/A"
                    }
                  />

                  <InfoCard
                    title="Updated At"
                    value={
                      task.updated_at
                        ? new Date(
                            task.updated_at
                          ).toLocaleString()
                        : "N/A"
                    }
                  />

                </div>

              </div>
            )
          )}

        </div>
      )}

    </main>
  );
}

function InfoCard({
  title,
  value,
}: {
  title: string;
  value: string | number;
}) {

  return (

    <div
      className="
        rounded-2xl
        border
        border-cyan-500/10
        bg-cyan-500/5
        p-5
      "
    >

      <p
        className="
          text-sm
          text-zinc-400
        "
      >

        {title}

      </p>

      <h3
        className="
          mt-3
          text-xl
          font-black
          break-all
        "
      >

        {value}

      </h3>

    </div>
  );
}