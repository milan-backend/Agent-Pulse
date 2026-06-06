export const API_URL = process.env.NEXT_PUBLIC_API_URL!;

type RequestOptions = {
  method?: string;
  body?: unknown; // Upgraded from any for better type safety
  headers?: Record<string, string>; // Added support for page-level custom headers overrides
};

function authHeaders() {
  if (typeof window === "undefined") {
    return {
      "Content-Type": "application/json",
    };
  }

  const token = localStorage.getItem("token");
  const workspaceId = localStorage.getItem("workspace_id");

  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(workspaceId ? { "workspace-id": workspaceId } : {}),
  };
}

// Global flags to manage unified token refresh states without deadlock
let isRefreshing = false;
let refreshSubscribers: (() => void)[] = [];

function onTokenRefreshed() {
  refreshSubscribers.forEach((callback) => callback());
  refreshSubscribers = [];
}

async function request(endpoint: string, options: RequestOptions = {}): Promise<any> {
  const executeFetch = () => {
    // If explicit customHeaders are supplied, prioritize them over default automated storage lookups
    const finalHeaders = options.headers !== undefined ? options.headers : authHeaders();

    return fetch(`${API_URL}${endpoint}`, {
      method: options.method || "GET",
      headers: finalHeaders,
      body: options.body ? JSON.stringify(options.body) : undefined,
    });
  };

  let response = await executeFetch();

  // INTERCEPTOR: Handle 401 Unauthorized errors and safely execute token rotation
  if (response.status === 401 && endpoint !== "/auth/login" && endpoint !== "/auth/refresh") {
    if (typeof window !== "undefined") {
      console.warn("Access token expired, initializing automatic refresh rotation...");

      if (!isRefreshing) {
        isRefreshing = true;

        try {
          // Trigger the HTTP-Only secure rotation endpoint explicitly passing credentials
          const refreshResponse = await fetch(`${API_URL}/auth/refresh`, {
            method: "POST",
            credentials: "include",
            headers: { "Content-Type": "application/json" }
          });

          if (refreshResponse.ok) {
            const data = await refreshResponse.json();
            if (data.access_token) {
              localStorage.setItem("token", data.access_token);
            }
            
            // 1. Wake up and execute all parallel queued subscribers first
            onTokenRefreshed();
            isRefreshing = false;

            // 2. Request A immediately retries itself right here
            const retryResponse = await executeFetch();
            
            if (!retryResponse.ok) {
              throw new Error(`Retry request failed with status ${retryResponse.status}`);
            }

            const retryText = await retryResponse.text();
            return retryText ? JSON.parse(retryText) : {};
          } else {
            throw new Error("Refresh token expired or invalid");
          }
        } catch (err) {
          isRefreshing = false;
          refreshSubscribers = [];
          console.error("Token refresh sequence failed, routing to login page:", err);
          logout();
          throw err;
        }
      }

      // Parallel Request Queue: Handle overlapping requests cleanly while Request A refreshes
      return new Promise((resolve, reject) => {
        refreshSubscribers.push(async () => {
          try {
            const retryResponse = await executeFetch();
            
            if (!retryResponse.ok) {
              reject(new Error(`Queued retry request failed with status ${retryResponse.status}`));
              return;
            }

            const text = await retryResponse.text();
            resolve(text ? JSON.parse(text) : {});
          } catch (retryErr) {
            reject(retryErr);
          }
        });
      });
    }
  }

  if (!response.ok) {
    let errorMessage = "Request failed";
    try {
      const errorData = await response.json();
      errorMessage = errorData?.detail || errorData?.message || errorMessage;
    } catch {
      errorMessage = await response.text();
    }
    throw new Error(errorMessage);
  }

  const text = await response.text();
  try {
    return text ? JSON.parse(text) : {};
  } catch {
    return text;
  }
}

/* =========================================================
BRING YOUR OWN KEYS (BYOK) INTEGRATION ENDPOINTS
========================================================= */

export const apiKeyApi = {
  /**
   * Safe metadata lookup to discover active key status.
   * Upgraded signature to accept optional provider string parameters cleanly without compilation bugs.
   */
  getKeyStatus: async (workspaceId?: string | null, provider: string = "GEMINI_API_KEY") => {
    const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };

    if (workspaceId) {
      headers["workspace-id"] = workspaceId;
    }

    // Passes provider as a clean flat query parameter matching your updated backend endpoints routing
    return request(`/api-keys/status?provider=${encodeURIComponent(provider)}`, {
      method: "GET",
      headers,
    });
  },

  /**
   * Connect and live-verify an AI console token string.
   */
  connectKey: async (provider: string, apiKey: string, workspaceId?: string | null) => {
    const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };

    if (workspaceId) {
      headers["workspace-id"] = workspaceId;
    }

    return request("/api-keys/connect", {
      method: "POST",
      headers,
      body: { provider, api_key: apiKey },
    });
  },

  /**
   * Completely erase configuration rows from backend storage tables.
   */
  disconnectKey: async (provider: string, workspaceId?: string | null) => {
    const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };

    if (workspaceId) {
      headers["workspace-id"] = workspaceId;
    }

    return request(`/api-keys/disconnect?provider=${encodeURIComponent(provider)}`, {
      method: "DELETE",
      headers,
    });
  }
};

/* =========================================================
AUTH
========================================================= */

export async function signup(name: string, email: string, password: string) {
  return request("/auth/signup", {
    method: "POST",
    body: { name, email, password },
  });
}

export async function login(email: string, password: string) {
  const data = await request("/auth/login", {
    method: "POST",
    body: { email, password },
  });

  if (data.access_token) {
    localStorage.setItem("token", data.access_token);
    sessionStorage.setItem("authenticated", "true");
  }
  if (data.workspace_id) {
    localStorage.setItem("workspace_id", data.workspace_id);
  }
  if (data.user_id) {
    localStorage.setItem("user_id", data.user_id);
  }
  if (data.workspaces) {
    localStorage.setItem("workspaces", JSON.stringify(data.workspaces || []));
  }
  return data;
}

/* =========================================================
DEACTIVATE ACCOUNT
========================================================= */

export async function deactivateAccount(password: string) {
  return request("/auth/deactivate-account", {
    method: "DELETE",
    body: { password },
  });
}

/* =========================================================
VERIFY EMAIL
========================================================= */

export async function verifyEmail(token: string) {
  return request(`/auth/verify-email?token=${token}`);
}

/* =========================================================
FORGOT PASSWORD
========================================================= */

export async function forgotPassword(email: string) {
  return request("/auth/forgot-password", {
    method: "POST",
    body: { email },
  });
}

/* =========================================================
RESET PASSWORD
========================================================= */

export async function resetPassword(token: string, new_password: string) {
  return request("/auth/reset-password", {
    method: "POST",
    body: { token, new_password },
  });
}

export async function getCurrentUser() {
  return request("/auth/me");
}

/* =========================================================
BILLING
========================================================= */

export async function createCheckout(planName: string) {
  return request(`/billing/checkout/${planName}`, {
    method: "POST",
  });
}

export async function getCurrentPlan() {
  return request("/billing/current-plan");
}

/* =========================================================
DASHBOARD
========================================================= */

export async function getDashboardSummary() {
  const response = await request("/dashboard/summary");
  return response?.data || response;
}

export async function getDashboardSteps() {
  const response = await request("/dashboard/steps");
  return response?.steps || response?.data || response || [];
}

export async function getDashboardAgents() {
  const response = await request("/dashboard/agents");
  return response;
}

/* =========================================================
ANALYTICS
========================================================= */

export async function getCostAnalytics() {
  const response = await request("/analytics/costs");
  return response?.data || response;
}

export async function getBlockedMissions() {
  const response = await request("/analytics/blocked");
  return response?.data || response;
}

export async function getAgentAnalytics() {
  const response = await request("/analytics/agents");
  return response?.data || response;
}

export async function getAnalyticsOverview() {
  const response = await request("/analytics/overview");
  return response?.data || response;
}

/* =========================================================
MISSIONS (UPDATED WITH OPTIONAL SEARCH COMPLIANCE HOOKS)
========================================================= */

export async function getMissionOverview() {
  const response = await request("/missions/overview");
  return response?.data || response;
}

export async function getMissionList(q?: string, status?: string) {
  const queryParams = new URLSearchParams();
  if (q) queryParams.append("q", q);
  if (status) queryParams.append("status", status);

  const queryString = queryParams.toString();
  const endpoint = `/missions/list${queryString ? `?${queryString}` : ""}`;
  const response = await request(endpoint);
  return Array.isArray(response) ? response : [];
}

export async function fetchMissionById(missionId: string) {
  const response = await request(`/missions/${missionId}`);
  return response?.data || response;
}

export async function retryMission(missionId: string) {
  return request(`/missions/${missionId}/retry`, {
    method: "POST",
  });
}

export async function killMission(missionId: string) {
  return request(`/missions/${missionId}/kill`, {
    method: "POST",
  });
}

export async function resumeMission(missionId: string) {
  return request(`/missions/${missionId}/resume`, {
    method: "POST",
  });
}

/* =========================================================
USAGE LOGS (UPDATED WITH OPTIONAL SEARCH COMPLIANCE HOOKS)
========================================================= */

export async function getDashboardUsageLogs(q?: string) {
  const queryParams = new URLSearchParams();
  if (q) queryParams.append("q", q);

  const queryString = queryParams.toString();
  const endpoint = `/usage/feed${queryString ? `?${queryString}` : ""}`;
  const response = await request(endpoint);
  return response?.logs || response?.data || response || [];
}

/* =========================================================
AGENT RUNTIME (UPDATED WITH OPTIONAL SEARCH COMPLIANCE HOOKS)
========================================================= */

export async function createAgent(data: { name: string; system_prompt?: string; model?: string; }) {
  return request("/agents/", {
    method: "POST",
    body: data,
  });
}

export async function getAgent(agentId: string) {
  const response = await request(`/dashboard/agent/${agentId}`);
  return response?.data || response;
}

export async function getAgentTasks(agentId: string, q?: string, status?: string) {
  const queryParams = new URLSearchParams();
  if (q) queryParams.append("q", q);
  if (status) queryParams.append("status", status);

  const queryString = queryParams.toString();
  const endpoint = `/agent/${agentId}${queryString ? `?${queryString}` : ""}`;
  const response = await request(endpoint);
  return response?.tasks || response?.data || response || [];
}

export async function regenerateAgentKey(agentId: string) {
  return request(`/agents/regenerate-key/${agentId}`, {
    method: "POST",
  });
}

export async function updateAgentSettings(
  agentId: string,
  payload: { max_steps?: number; max_retries?: number; max_cost?: number; max_repeated_tasks?: number; }
) {
  return request(`/agents/${agentId}`, {
    method: "PUT",
    body: payload,
  });
}

export async function pauseAgentMission(agentId: string) {
  return request(`/mission-control/pause/${agentId}`, {
    method: "POST",
  });
}

export async function resumeAgentMission(agentId: string) {
  return request(`/mission-control/resume/${agentId}`, {
    method: "POST",
  });
}

export async function killAgentMission(agentId: string) {
  return request(`/mission-control/kill/${agentId}`, {
    method: "POST",
  });
}

export async function stopAllAgents() {
  return request("/agents/kill", {
    method: "POST",
  });
}

export async function resumeAllAgents() {
  return request("/agents/resume", {
    method: "POST",
  });
}

/* =========================================================
STEPS
========================================================= */

export async function executeStep(data: unknown) {
  return request("/steps/execute", {
    method: "POST",
    body: data,
  });
}

export async function getStepStatus(stepId: string) {
  const response = await request(`/steps/${stepId}`);
  return response?.data || response;
}

export async function retryStep(stepId: string) {
  return request(`/steps/retry/${stepId}`, {
    method: "POST",
  });
}

export async function getStepLogs(stepId: string) {
  const response = await request(`/steps/${stepId}/logs`);
  return response?.logs || response?.data || response || [];
}

/* =========================================================
WORKSPACE
========================================================= */

export async function createWorkspaceMember(data: { email: string; role: string; }) {
  return request("/workspace/add-member", {
    method: "POST",
    body: data,
  });
}

export async function updateWorkspaceMemberRole(email: string, role: string) {
  return request("/workspace/members/role", {
    method: "PATCH",
    body: { email, role },
  });
}

export async function getWorkspaceMembers() {
  const response = await request("/workspace/members");
  return response?.members || response?.data || response || [];
}

export async function deleteWorkspaceMember(userId: string) {
  return request(`/workspace/members/${userId}`, {
    method: "DELETE",
  });
}

/* =========================================================
MCP
========================================================= */

export async function getMcpTools() {
  const response = await request("/mcp/tools");
  return response?.tools || response?.data || response || [];
}

export async function executeMcp(data: unknown) {
  return request("/mcp/execute", {
    method: "POST",
    body: data,
  });
}

/* =========================================================
LIVE WEBSOCKET
========================================================= */

export function createDashboardSocket(
  onMessage: (data: any) => void,
  onOpen?: () => void,
  onClose?: () => void
) {
  const WS_URL = API_URL.replace("http://", "ws://").replace("https://", "wss://");
  const workspaceId = localStorage.getItem("workspace_id");

  const socketContainer = {
    ws: null as WebSocket | null,
    close: function() {
      if (this.ws) this.ws.close();
    }
  };

  (async () => {
    try {
      const ticketResponse = await fetch(`${API_URL}/auth/ws-ticket`, {
        method: "POST",
        headers: authHeaders(),
      });

      let ticketQuery = "";
      if (ticketResponse.ok) {
        const ticketData = await ticketResponse.json();
        if (ticketData.ticket) {
          ticketQuery = `&ticket=${ticketData.ticket}`;
        }
      }

      const socket = new WebSocket(`${WS_URL}/ws/live?workspace_id=${workspaceId}${ticketQuery}`);
      socketContainer.ws = socket;

      socket.onopen = () => {
        console.log("WebSocket connected securely to live runtime");
        if (onOpen) onOpen();
      };

      socket.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);
          onMessage(parsed);
        } catch (err) {
          console.error("WebSocket parse error", err);
        }
      };

      socket.onerror = (err) => {
        console.error("WebSocket error", err);
      };

      socket.onclose = () => {
        console.log("WebSocket disconnected");
        if (onClose) onClose();
      };

    } catch (error) {
      console.error("Failed to initialize secure live WebSocket connection:", error);
    }
  })();

  return socketContainer;
}

/* =========================================================
LOGOUT
========================================================= */

export function logout() {
  if (typeof window !== "undefined") {
    // Included credentials option to clear HTTP-Only tracking cookies on your live FastAPI server
    fetch(`${API_URL}/auth/logout`, { 
      method: "POST",
      credentials: "include"
    }).catch((err) =>
      console.error("Session cookie clearance request skipped or unauthorized:", err)
    );

    localStorage.removeItem("token");
    localStorage.removeItem("workspace_id");
    localStorage.removeItem("user_id");
    localStorage.removeItem("workspaces");
    sessionStorage.removeItem("authenticated");
    window.location.href = "/login";
  }
}