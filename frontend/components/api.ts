const API_BASE = process.env.NEXT_PUBLIC_API_KEY

export async function fetchDashboardSummary(
  token: string
) {
  const res = await fetch(
    `${API_BASE}/dashboard/summary`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  )

  return res.json()
}

export async function fetchDashboardUsage(
  token: string
) {
  const res = await fetch(
    `${API_BASE}/dashboard/usage`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  )

  return res.json()
}

export async function fetchDashboardSteps(
  token: string
) {
  const res = await fetch(
    `${API_BASE}/dashboard/steps`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  )

  return res.json()
}

export async function fetchUsageLogs(
  token: string
) {
  const res = await fetch(
    `${API_BASE}/dashboard/usage/logs`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  )

  return res.json()
}


export function saveToken(token: string) {
  localStorage.setItem("token", token)
}

export function getToken() {
  return localStorage.getItem("token")
}

export function logout() {
  localStorage.removeItem("token")
}


export async function regenerateApiKey(
  token: string
) {

  const res = await fetch(
    `${API_BASE}/agents/regenerate-key`,
    {
      method: "POST",

      headers: {
        Authorization:
          `Bearer ${token}`,
      },
    }
  )

  return res.json()
}

export async function fetchStepById(
  stepId: string,
  token: string
) {
  const response = await fetch(
    `http://127.0.0.1:8000/steps/${stepId}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  )

  if (!response.ok) {
    throw new Error("Failed to fetch step")
  }

  return response.json()
}