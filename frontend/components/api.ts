export const API_URL =
  process.env.NEXT_PUBLIC_API_URL!;

type RequestOptions = {
  method?: string;
  body?: any;
};

function authHeaders() {
  if (
    typeof window === "undefined"
  ) {
    return {
      "Content-Type":
        "application/json",
    };
  }

  const token =
    localStorage.getItem(
      "token"
    );

  const workspaceId =
    localStorage.getItem(
      "workspace_id"
    );

  return {
    "Content-Type":
      "application/json",

    ...(token
      ? {
          Authorization:
            `Bearer ${token}`,
        }
      : {}),

    ...(workspaceId
      ? {
          "workspace-id":
            workspaceId,
        }
      : {}),
  };
}

async function request(
  endpoint: string,
  options: RequestOptions = {}
) {
  const response = await fetch(
    `${API_URL}${endpoint}`,
    {
      method:
        options.method || "GET",

      headers:
        authHeaders(),

      body: options.body
        ? JSON.stringify(
            options.body
          )
        : undefined,
    }
  );

  if (!response.ok) {

    if (
      response.status === 401 &&
      typeof window !== "undefined"
    ) {

      console.error(
        "Unauthorized request"
      );

      localStorage.removeItem(
        "token"
      );

      sessionStorage.removeItem(
        "authenticated"
      );

      // OPTIONAL:
      // uncomment if auto redirect needed

      // window.location.href =
      //   "/login";
    }

    let errorMessage =
      "Request failed";

    try {
      const errorData =
        await response.json();

      errorMessage =
        errorData?.detail ||
        errorData?.message ||
        errorMessage;

    } catch {
      errorMessage =
        await response.text();
    }

    throw new Error(
      errorMessage
    );
  }

  const text =
    await response.text();

  try {
    return text
      ? JSON.parse(text)
      : {};
  } catch {
    return text;
  }
}


/* =========================================================
   AUTH
========================================================= */

export async function signup(
  name: string,
  email: string,
  password: string
) {
  return request(
    "/auth/signup",
    {
      method: "POST",

      body: {
        name,
        email,
        password,
      },
    }
  );
}

export async function login(
  email: string,
  password: string
) {
  const data = await request(
    "/auth/login",
    {
      method: "POST",

      body: {
        email,
        password,
      },
    }
  );

  if (data.access_token) {
    localStorage.setItem(
      "token",
      data.access_token
    );

    sessionStorage.setItem(
      "authenticated",
      "true"
    );
  }

  if (data.workspace_id) {
    localStorage.setItem(
      "workspace_id",
      data.workspace_id
    );
  }

  if (data.user_id) {
    localStorage.setItem(
      "user_id",
      data.user_id
    );
  }

  if (data.workspaces) {
    localStorage.setItem(
      "workspaces",
      JSON.stringify(
        data.workspaces || []
      )
    );
  }

  return data;
}


/* =========================================================
   DEACTIVATE ACCOUNT
========================================================= */

export async function deactivateAccount(
  password: string
) {
  return request(
    "/auth/deactivate-account",
    {
      method: "DELETE",

      body: {
        password,
      },
    }
  );
}




/* =========================================================
   VERIFY EMAIL
========================================================= */

export async function verifyEmail(
  token: string
) {
  return request(
    `/auth/verify-email?token=${token}`
  );
}


/* =========================================================
   FORGOT PASSWORD
========================================================= */

export async function forgotPassword(
  email: string
) {
  return request(
    "/auth/forgot-password",
    {
      method: "POST",

      body: {
        email,
      },
    }
  );
}


/* =========================================================
   RESET PASSWORD
========================================================= */

export async function resetPassword(
  token: string,
  new_password: string
) {
  return request(
    "/auth/reset-password",
    {
      method: "POST",

      body: {
        token,
        new_password,
      },
    }
  );
}

export async function getCurrentUser() {
  return request(
    "/auth/me"
  );
}


/* =========================================================
   BILLING
========================================================= */

export async function createCheckout(
  planName: string
) {

  return request(
    `/billing/checkout/${planName}`,
    {
      method: "POST",
    }
  );
}

export async function getCurrentPlan()
{
  return request(
    "/billing/current-plan"
  );
}


/* =========================================================
   DASHBOARD
========================================================= */

export async function getDashboardSummary() {
  const response =
    await request(
      "/dashboard/summary"
    );

  return (
    response?.data ||
    response
  );
}

export async function getDashboardSteps() {
  const response =
    await request(
      "/dashboard/steps"
    );

  return (
    response?.steps ||
    response?.data ||
    response ||
    []
  );
}

export async function getDashboardUsageLogs() {
  const response =
    await request(
      "/usage/feed"
    );

  return (
    response?.logs ||
    response?.data ||
    response ||
    []
  );
}

export async function getDashboardAgents() {
  const response =
    await request(
      "/dashboard/agents"
    );

  return response;
}


/* =========================================================
   ANALYTICS
========================================================= */

export async function getCostAnalytics() {
  const response =
    await request(
      "/analytics/costs"
    );

  return (
    response?.data ||
    response
  );
}

export async function getBlockedMissions() {
  const response =
    await request(
      "/analytics/blocked"
    );

  return (
    response?.data ||
    response
  );
}

export async function getAgentAnalytics() {
  const response =
    await request(
      "/analytics/agents"
    );

  return (
    response?.data ||
    response
  );
}

export async function getAnalyticsOverview() {
  const response =
    await request(
      "/analytics/overview"
    );

  return (
    response?.data ||
    response
  );
}


/* =========================================================
   MISSIONS
========================================================= */

export async function getMissionOverview() {
  const response =
    await request(
      "/missions/overview"
    );

  return (
    response?.data ||
    response
  );
}

export async function getMissionList() {
  const response =
    await request(
      "/missions/list"
    );

  return Array.isArray(response)
    ? response
    : [];
}

export async function fetchMissionById(
  missionId: string
) {
  const response =
    await request(
      `/missions/${missionId}`
    );

  return (
    response?.data ||
    response
  );
}

export async function retryMission(
  missionId: string
) {
  return request(
    `/missions/${missionId}/retry`,
    {
      method: "POST",
    }
  );
}

export async function killMission(
  missionId: string
) {
  return request(
    `/missions/${missionId}/kill`,
    {
      method: "POST",
    }
  );
}

export async function resumeMission(
  missionId: string
) {
  return request(
    `/missions/${missionId}/resume`,
    {
      method: "POST",
    }
  );
}


/* =========================================================
   AGENT RUNTIME
========================================================= */

export async function createAgent(
  data: {
    name: string;
    system_prompt?: string;
    model?: string;
  }
) {
  return request(
    "/agents/",
    {
      method: "POST",
      body: data,
    }
  );
}

export async function getAgent(
  agentId: string
) {
  const response =
    await request(
      `/dashboard/agent/${agentId}`
    );

  return (
    response?.data ||
    response
  );
}

export async function getAgentTasks(
  agentId: string
) {
  const response =
    await request(
      `/agent/${agentId}`
    );

  return (
    response?.tasks ||
    response?.data ||
    response ||
    []
  );
}

export async function regenerateAgentKey(
  agentId: string
) {
  return request(
    `/agents/regenerate-key/${agentId}`,
    {
      method: "POST",
    }
  );
}

export async function updateAgentSettings(
  agentId: string,
  payload: {
    max_steps?: number;
    max_retries?: number;
    max_cost?: number;
    max_repeated_tasks?: number;
  }
) {
  return request(
    `/agents/${agentId}`,
    {
      method: "PUT",
      body: payload,
    }
  );
}

export async function pauseAgentMission(
  agentId: string
) {
  return request(
    `/mission-control/pause/${agentId}`,
    {
      method: "POST",
    }
  );
}

export async function resumeAgentMission(
  agentId: string
) {
  return request(
    `/mission-control/resume/${agentId}`,
    {
      method: "POST",
    }
  );
}

export async function killAgentMission(
  agentId: string
) {
  return request(
    `/mission-control/kill/${agentId}`,
    {
      method: "POST",
    }
  );
}

export async function stopAllAgents() {
  return request(
    "/agents/kill",
    {
      method: "POST",
    }
  );
}

export async function resumeAllAgents() {
  return request(
    "/agents/resume",
    {
      method: "POST",
    }
  );
}


/* =========================================================
   STEPS
========================================================= */

export async function executeStep(
  data: any
) {
  return request(
    "/steps/execute",
    {
      method: "POST",
      body: data,
    }
  );
}

export async function getStepStatus(
  stepId: string
) {
  const response =
    await request(
      `/steps/${stepId}`
    );

  return (
    response?.data ||
    response
  );
}

export async function retryStep(
  stepId: string
) {
  return request(
    `/steps/retry/${stepId}`,
    {
      method: "POST",
    }
  );
}

export async function getStepLogs(
  stepId: string
) {
  const response =
    await request(
      `/steps/${stepId}/logs`
    );

  return (
    response?.logs ||
    response?.data ||
    response ||
    []
  );
}


/* =========================================================
   WORKSPACE
========================================================= */

export async function createWorkspaceMember(
  data: {
    email: string;
    role: string;
  }
) {
  return request(
    "/workspace/add-member",
    {
      method: "POST",
      body: data,
    }
  );
}

export async function updateWorkspaceMemberRole(
  email: string,
  role: string
) {
  return request(
    `/workspace/members/role`,
    {
      method: "PATCH",

      body: {
        email,
        role,
      },
    }
  );
}

export async function getWorkspaceMembers() {
  const response =
    await request(
      "/workspace/members"
    );

  return (
    response?.members ||
    response?.data ||
    response ||
    []
  );
}

export async function deleteWorkspaceMember(
  userId: string
) {
  return request(
    `/workspace/members/${userId}`,
    {
      method: "DELETE",
    }
  );
}


/* =========================================================
   MCP
========================================================= */

export async function getMcpTools() {
  const response =
    await request(
      "/mcp/tools"
    );

  return (
    response?.tools ||
    response?.data ||
    response ||
    []
  );
}

export async function executeMcp(
  data: any
) {
  return request(
    "/mcp/execute",
    {
      method: "POST",
      body: data,
    }
  );
}


/* =========================================================
   LIVE WEBSOCKET
========================================================= */

export function createDashboardSocket(
  onMessage: (
    data: any
  ) => void,

  onOpen?: () => void,

  onClose?: () => void
) {
  const WS_URL =
    API_URL.replace(
      "http://",
      "ws://"
    ).replace(
      "https://",
      "wss://"
    );

  const workspaceId =
    localStorage.getItem(
      "workspace_id"
    );

  const socket =
    new WebSocket(
      `${WS_URL}/ws/live?workspace_id=${workspaceId}`
    );

  socket.onopen = () => {
    console.log(
      "WebSocket connected"
    );

    if (onOpen) {
      onOpen();
    }
  };

  socket.onmessage = (
    event
  ) => {
    try {
      const parsed =
        JSON.parse(
          event.data
        );

      onMessage(parsed);

    } catch (err) {
      console.error(
        "WebSocket parse error",
        err
      );
    }
  };

  socket.onerror = (
    err
  ) => {
    console.error(
      "WebSocket error",
      err
    );
  };

  socket.onclose = () => {
    console.log(
      "WebSocket disconnected"
    );

    if (onClose) {
      onClose();
    }
  };

  return socket;
}


/* =========================================================
   LOGOUT
========================================================= */

export function logout() {
  if (
    typeof window !==
    "undefined"
  ) {
    localStorage.removeItem(
      "token"
    );

    localStorage.removeItem(
      "workspace_id"
    );

    localStorage.removeItem(
      "user_id"
    );

    localStorage.removeItem(
      "workspaces"
    );

    sessionStorage.removeItem(
      "authenticated"
    );

    window.location.href =
      "/login";
  }
}