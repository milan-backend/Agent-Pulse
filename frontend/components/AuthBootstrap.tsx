"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { API_URL } from "./api"; // Utilizing your centralized backend URL string

export default function AuthBootstrap() {
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (pathname !== "/") return;

    // 1. If a valid token is present in local storage, they are logged in! 
    // Send them directly to the dashboard immediately.
    const token = localStorage.getItem("token");
    if (token) {
      router.replace("/dashboard");
      return;
    }

    // 💡 NEW SECURITY GUARDRAIL: 
    // Check if a logout action was just triggered during this browser session window.
    // If we just logged out, completely skip trying to refresh via cookies!
    const wasLoggedOut = sessionStorage.getItem("logged_out_marker") === "true";
    if (wasLoggedOut) {
      console.log("AuthBootstrap: Explicit logout detected. Auto-cookie refresh aborted.");
      return;
    }

    // 2. If no token is in storage, check the backend to see if a valid persistent session cookie exists.
    fetch(`${API_URL}/auth/refresh`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include", // Safely forwards your HttpOnly token cookie to Render
    })
      .then((res) => {
        if (res.ok) return res.json();
        throw new Error("No secure cookie session found.");
      })
      .then((data) => {
        if (data?.access_token) {
          // Store it where your api.ts file expects it
          localStorage.setItem("token", data.access_token);
          router.replace("/dashboard");
        }
      })
      .catch(() => {
        // Safe Catch: If no cookie exists, do absolutely nothing!
        // The user cleanly stays on your landing page without any loops or redirects.
      });
  }, [pathname, router]);

  return null;
}