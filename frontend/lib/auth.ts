const API_BASE = "http://127.0.0.1:8000"

export async function signupUser(data: {
  name: string
  email: string
  password: string
}) {
  const res = await fetch(`${API_BASE}/auth/signup`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  })

  return res.json()
}

export async function loginUser(
  email: string,
  password: string
) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email,
      password,
    }),
  })

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