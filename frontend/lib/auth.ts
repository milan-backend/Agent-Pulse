const TOKEN_KEY =
  "token"

export const auth = {

  // =========================
  // SAVE TOKEN
  // =========================

  setToken(
    token: string
  ) {

    if (
      typeof window !==
      "undefined"
    ) {

      localStorage.setItem(
        TOKEN_KEY,
        token
      )
    }
  },

  // =========================
  // GET TOKEN
  // =========================

  getToken():
    string | null {

    if (
      typeof window !==
      "undefined"
    ) {

      return localStorage.getItem(
        TOKEN_KEY
      )
    }

    return null
  },

  // =========================
  // REMOVE TOKEN
  // =========================

  removeToken() {

    if (
      typeof window !==
      "undefined"
    ) {

      localStorage.removeItem(
        TOKEN_KEY
      )
    }
  },

  // =========================
  // CHECK AUTH
  // =========================

  isAuthenticated():
    boolean {

    if (
      typeof window !==
      "undefined"
    ) {

      return !!localStorage.getItem(
        TOKEN_KEY
      )
    }

    return false
  },
}