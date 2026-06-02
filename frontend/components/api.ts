export const API_URL = process.env.NEXT_PUBLIC_API_URL!;

// =========================================================
// ENTERPRISE PRODUCTION TYPING HANDLERS
// =========================================================

export interface RequestOptions {
  method?: string;
  body?: unknown;
  signal?: AbortSignal;
}

export interface WorkspaceItem {
  workspace_id: string;
  workspace_name: string;
  role: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user_id: string;
  workspace_id: string;
  role: string;
  workspaces: WorkspaceItem[];
  message?: string;
}

export interface ActionResponse {
  success: boolean;
  message: string;
}

export interface TicketResponse {
  ticket: string;
}

export interface MissionOverview {
  total_missions: number;
  running: number;
  completed: number;
  failed: number;
}

export interface Mission {
  mission_id: string;
  task_name: string;
  status: string;
  is_retry?: boolean;
  original_mission_id?: string;
  retry_count: number;
  cache_hit: boolean;
  created_at: string | null;
  updated_at: string | null;
  agent_id?: string;
  runtime_controlled?: boolean;
  error_message?: string | null;
}

export interface UsageLog {
  id?: string;
  event_type?: string;
  type?: string;
  agent_id?: string;
  step_id?: string;
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens?: number;
  cost: number;
  created_at: string | null;
}

export interface AgentPolicy {
  max_cost: number;
  max_steps: number;
  max_retries: number;
  max_repeated_tasks: number;
}

export interface AgentResponse {
  agent: {
    id: string;
    name: string;
    is_active: boolean;
    is_killed: boolean;
    created_at: string | null;
  };
  policy: AgentPolicy;
  mission_count: number;
  total_cost: number;
}

export interface AgentTask {
  step_id: string;
  task_name: string;
  status: string;
  input_data: unknown;
  output_data: unknown;
  error_message: string | null;
  retry_count: number;
  cache_hit: boolean;
  event_type: string | null;
  started_at: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface CheckoutResponse {
  checkout_url: string;
}

export interface PlanResponse {
  plan_name: string;
  status: string;
  expires_at: string | null;
}

// =========================================================
// CONCURRENCY & ROTATION MANAGER STATE
// =========================================================
let refreshPromise: Promise<string | null> | null = null;

let activeSocketInstance: WebSocket | null = null;

// FIX: Initialized variables with undefined instead of null to match structural function signatures exactly
let activeSocketOnMessage: ((data: any) => void) | undefined = undefined;
let activeSocketOnOpen: (() => void) | undefined = undefined;
let activeSocketOnClose: (() => void) | undefined = undefined;

function authHeaders() {
  if (typeof window === "undefined") {
    return { "Content-Type": "application/json" };
  }

  const token = localStorage.getItem("token");
  const workspaceId = localStorage.getItem("workspace_id");

  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(workspaceId ? { "workspace-id": workspaceId } : {}),
  };
}

function recreateDashboardSocket(): void {
  if (activeSocketInstance) {
    activeSocketInstance.onclose = null;
    activeSocketInstance.close();
  }
  
  if (activeSocketOnMessage) {
    createDashboardSocket(activeSocketOnMessage, activeSocketOnOpen, activeSocketOnClose);
  }
}

async function performTokenRefresh(): Promise<string | null> {
  try {
    const refreshResponse = await fetch(`${API_URL}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
    });

    if (refreshResponse.ok) {
      const data = await refreshResponse.json();
      if (data?.access_token) {
        localStorage.setItem("token", data.access_token);
        
        if (activeSocketInstance && activeSocketInstance.readyState === WebSocket.OPEN) {
          console.log("Access token rotated. Re-shaking secure WebSocket channels...");
          recreateDashboardSocket();
        }
        
        return data.access_token;
      }
    }
  } catch (err) {
    console.error("Silent token refresh execution failed:", err);
  }
  return null;
}

async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const response = await fetch(`${API_URL}${endpoint}`, {
    method: options.method || "GET",
    headers: authHeaders(),
    body: options.body ? JSON.stringify(options.body) : undefined,
    credentials: "include",
    signal: options.signal,
  });

  if (
    response.status === 401 && 
    endpoint !== "/auth/login" && 
    endpoint !== "/auth/refresh"
  ) {
    if (typeof window !== "undefined") {
      if (!refreshPromise) {
        refreshPromise = performTokenRefresh().finally(() => {
          refreshPromise = null;
        });
      }

      const newToken = await refreshPromise;
      if (newToken) {
        return await request<T>(endpoint, options);
      }
    }

    if (typeof window !== "undefined") {
      localStorage.removeItem("token");
      localStorage.removeItem("workspace_id");
      localStorage.removeItem("user_id");
      localStorage.removeItem("workspaces");
      sessionStorage.removeItem("authenticated");
      window.location.href = "/login";
      throw new Error("Session unauthorized.");
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
  return text ? (JSON.parse(text) as T) : ({} as T);
}

/* =========================================================
AUTH SECTOR
========================================================= */

export async function signup(name: string, email: string, password: string): Promise<ActionResponse> {
  return request<ActionResponse>("/auth/signup", {
    method: "POST",
    body: { name, email, password },
  });
}

export async function login(email: string, password: string): Promise<LoginResponse> {
  if (typeof window !== "undefined") {
    localStorage.removeItem("token");
    localStorage.removeItem("workspace_id");
  }

  const data = await request<LoginResponse>("/auth/login", {
    method: "POST",
    body: { email, password },
  });

  if (data.access_token) {
    localStorage.setItem("token", data.access_token);
  }
  if (data.workspace_id) {
    localStorage.setItem("workspace_id", data.workspace_id);
  }
  if (data.user_id) {
    localStorage.setItem("user_id", data.user_id);
  }
  if (data.workspaces) {
    localStorage.setItem("workspaces", JSON.stringify(data.workspaces));
  }
  
  sessionStorage.setItem("authenticated", "true");
  return data;
}

export async function deactivateAccount(password: string): Promise<ActionResponse> {
  return request<ActionResponse>("/auth/deactivate-account", {
    method: "DELETE",
    body: { password },
  });
}

export async function verifyEmail(token: string): Promise<ActionResponse> {
  return request<ActionResponse>(`/auth/verify-email?token=${token}`);
}

export async function forgotPassword(email: string): Promise<ActionResponse> {
  return request<ActionResponse>("/auth/forgot-password", {
    method: "POST",
    body: { email },
  });
}

export async function resetPassword(token: string, new_password: string): Promise<ActionResponse> {
  return request<ActionResponse>("/auth/reset-password", {
    method: "POST",
    body: { token, new_password },
  });
}

export async function getCurrentUser(): Promise<any> {
  return request("/auth/me");
}

/* =========================================================
BILLING
========================================================= */

export async function createCheckout(planName: string): Promise<CheckoutResponse> {
  return request<CheckoutResponse>(`/billing/checkout/${planName}`, {
    method: "POST",
  });
}

export async function getCurrentPlan(): Promise<PlanResponse> {
  return request<PlanResponse>("/billing/current-plan");
}

/* =========================================================
DASHBOARD
========================================================= */

export async function getDashboardSummary(): Promise<any> {
  const response = await request<any>("/dashboard/summary");
  return response?.data || response;
}

export async function getDashboardSteps(): Promise<any[]> {
  const response = await request<any>("/dashboard/steps");
  return response?.steps || response?.data || response || [];
}

export async function getDashboardAgents(): Promise<any> {
  return await request("/dashboard/agents");
}

/* =========================================================
ANALYTICS
========================================================= */

export async function getCostAnalytics(): Promise<any> {
  const response = await request<any>("/analytics/costs");
  return response?.data || response;
}

export async function getBlockedMissions(): Promise<any> {
  const response = await request<any>("/analytics/blocked");
  return response?.data || response;
}

export async function getAgentAnalytics(): Promise<any> {
  const response = await request<any>("/analytics/agents");
  return response?.data || response;
}

export async function getAnalyticsOverview(): Promise<any> {
  const response = await request<any>("/analytics/overview");
  return response?.data || response;
}

/* =========================================================
MISSIONS
========================================================= */

export async function getMissionOverview(): Promise<MissionOverview> {
  const response = await request<any>("/missions/overview");
  return response?.data || response;
}

export async function getMissionList(q?: string, status?: string, signal?: AbortSignal): Promise<Mission[]> {
  const queryParams = new URLSearchParams();
  if (q) queryParams.append("q", q);
  if (status) queryParams.append("status", status);

  const queryString = queryParams.toString();
  const endpoint = `/missions/list${queryString ? `?${queryString}` : ""}`;

  const response = await request<any>(endpoint, { signal });
  return Array.isArray(response) ? response : [];
}

export async function fetchMissionById(missionId: string): Promise<Mission> {
  const response = await request<any>(`/missions/${missionId}`);
  return response?.data || response;
}

export async function retryMission(missionId: string): Promise<ActionResponse> {
  return request<ActionResponse>(`/missions/${missionId}/retry`, { method: "POST" });
}

export async function killMission(missionId: string): Promise<ActionResponse> {
  return request<ActionResponse>(`/missions/${missionId}/kill`, { method: "POST" });
}

export async function resumeMission(missionId: string): Promise<ActionResponse> {
  return request<ActionResponse>(`/missions/${missionId}/resume`, { method: "POST" });
}

/* =========================================================
USAGE LOGS
========================================================= */

export async function getDashboardUsageLogs(q?: string, signal?: AbortSignal): Promise<any> {
  const queryParams = new URLSearchParams();
  if (q) queryParams.append("q", q);

  const queryString = queryParams.toString();
  const endpoint = `/usage/feed${queryString ? `?${queryString}` : ""}`;

  return await request<any>(endpoint, { signal });
}

/* =========================================================
AGENT RUNTIME
========================================================= */

export async function createAgent(data: { name: string; system_prompt?: string; model?: string; }): Promise<any> {
  return request("/agents/", {
    method: "POST",
    body: data,
  });
}

export async function getAgent(agentId: string): Promise<AgentResponse> {
  const response = await request<any>(`/dashboard/agent/${agentId}`);
  return response?.data || response;
}

export async function getAgentTasks(agentId: string, q?: string, status?: string, signal?: AbortSignal): Promise<AgentTask[]> {
  const queryParams = new URLSearchParams();
  if (q) queryParams.append("q", q);
  if (status) queryParams.append("status", status);

  const queryString = queryParams.toString();
  const endpoint = `/agent/${agentId}${queryString ? `?${queryString}` : ""}`;

  const response = await request<any>(endpoint, { signal });
  return response?.tasks || response?.data || response || [];
}

export async function regenerateAgentKey(agentId: string): Promise<ActionResponse> {
  return request<ActionResponse>(`/agents/regenerate-key/${agentId}`, { method: "POST" });
}

export async function updateAgentSettings(
  agentId: string,
  payload: { max_steps?: number; max_retries?: number; max_cost?: number; max_repeated_tasks?: number; }
): Promise<ActionResponse> {
  return request<ActionResponse>(`/agents/${agentId}`, {
    method: "PUT",
    body: payload,
  });
}

export async function pauseAgentMission(agentId: string): Promise<ActionResponse> {
  return request<ActionResponse>(`/mission-control/pause/${agentId}`, { method: "POST" });
}

export async function resumeAgentMission(agentId: string): Promise<ActionResponse> {
  return request<ActionResponse>(`/mission-control/resume/${agentId}`, { method: "POST" });
}

export async function killAgentMission(agentId: string): Promise<ActionResponse> {
  return request<ActionResponse>(`/mission-control/kill/${agentId}`, { method: "POST" });
}

export async function stopAllAgents(): Promise<ActionResponse> {
  return request<ActionResponse>("/agents/kill", { method: "POST" });
}

export async function resumeAllAgents(): Promise<ActionResponse> {
  return request<ActionResponse>("/agents/resume", { method: "POST" });
}

/* =========================================================
STEPS
========================================================= */

export async function executeStep(data: unknown): Promise<any> {
  return request("/steps/execute", {
    method: "POST",
    body: data,
  });
}

export async function getStepStatus(stepId: string): Promise<any> {
  const response = await request<any>(`/steps/${stepId}`);
  return response?.data || response;
}

export async function retryStep(stepId: string): Promise<ActionResponse> {
  return request<ActionResponse>(`/steps/retry/${stepId}`, { method: "POST" });
}

export async function getStepLogs(stepId: string): Promise<any[]> {
  const response = await request<any>(`/steps/${stepId}/logs`);
  return response?.logs || response?.data || response || [];
}

/* =========================================================
WORKSPACE
========================================================= */

export async function createWorkspaceMember(data: { email: string; role: string; }): Promise<ActionResponse> {
  return request<ActionResponse>("/workspace/add-member", {
    method: "POST",
    body: data,
  });
}

export async function updateWorkspaceMemberRole(email: string, role: string): Promise<ActionResponse> {
  return request<ActionResponse>("/workspace/members/role", {
    method: "PATCH",
    body: { email, role },
  });
}

export async function getWorkspaceMembers(): Promise<any[]> {
  const response = await request<any>("/workspace/members");
  return response?.members || response?.data || response || [];
}

export async function deleteWorkspaceMember(userId: string): Promise<ActionResponse> {
  return request<ActionResponse>(`/workspace/members/${userId}`, { method: "DELETE" });
}

/* =========================================================
MCP
========================================================= */

export async function getMcpTools(): Promise<any[]> {
  const response = await request<any>("/mcp/tools");
  return response?.tools || response?.data || response || [];
}

export async function executeMcp(data: unknown): Promise<any> {
  return request("/mcp/execute", {
    method: "POST",
    body: data,
  });
}

/* =========================================================
LIVE WEBSOCKET (ONE-TIME HANDSHAKE TICKETS) 🛡️
// ========================================================= */

export function createDashboardSocket(
  onMessage: (data: any) => void,
  onOpen?: () => void,
  onClose?: () => void
): { close: () => void } {
  const WS_URL = API_URL.replace("http://", "ws://").replace("https://", "wss://");
  const workspaceId = localStorage.getItem("workspace_id");

  let isManuallyClosed = false;
  let socketInstance: WebSocket | null = null;

  activeSocketOnMessage = onMessage;
  activeSocketOnOpen = onOpen;
  activeSocketOnClose = onClose;

  async function establishSecureConnection() {
    if (isManuallyClosed) return;

    try {
      const authData = await request<TicketResponse>("/auth/ws-ticket", { method: "POST" });
      
      if (!authData?.ticket) {
        throw new Error("Unable to provision secure network streaming ticket parameters.");
      }

      const socket = new WebSocket(
        `${WS_URL}/ws/live?workspace_id=${workspaceId}&ticket=${authData.ticket}`
      );

      socket.onopen = () => {
        console.log("WebSocket connected securely via short-lived single-use ticket.");
        if (onOpen) onOpen();
      };

      socket.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);
          onMessage(parsed);
        } catch (err) {
          console.error("Streaming packet parsing anomaly detected:", err);
        }
      };

      socket.onerror = (err) => {
        console.error("Secure data stream validation error:", err);
      };

      socket.onclose = () => {
        if (!isManuallyClosed && activeSocketInstance === socket) {
          console.log("Ticket expired or link severed. Re-shaking handshake pipelines...");
          setTimeout(() => establishSecureConnection(), 3000); 
        }
        if (onClose && activeSocketInstance === socket) onClose();
      };

      socketInstance = socket;
      activeSocketInstance = socket;

    } catch (err) {
      console.error("Critical secure socket establishment lifecycle failure:", err);
      setTimeout(() => establishSecureConnection(), 5000);
    }
  }

  establishSecureConnection();

  return {
    close: () => {
      isManuallyClosed = true;
      if (socketInstance) {
        socketInstance.onclose = null;
        socketInstance.close();
      }
      if (activeSocketInstance === socketInstance) {
        activeSocketInstance = null;
      }
    }
  };
}
