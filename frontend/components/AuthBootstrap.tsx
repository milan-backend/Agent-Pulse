"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { API_URL } from "./api"; // Utilizing your centralized backend URL string

export default function AuthBootstrap() {
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (pathname !== "/") return;

    // Check if the user intentionally logged out during this browser session
    const hasLoggedOut = sessionStorage.getItem("logged_out") === "true";
    if (hasLoggedOut) {
      // If they logged out, do absolutely nothing. Let them see the landing page peacefully!
      return;
    }

    // Otherwise, check for an active persistent cookie session seamlessly
    fetch(`${API_URL}/auth/refresh`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include", // Essential for bringing along your secure HTTP-Only cookie
    })
      .then((res) => {
        if (res.ok) return res.json();
        throw new Error("No active persistent session found.");
      })
      .then((data) => {
        if (data?.access_token) {
          // Store the fresh token exactly where your api.ts file intercepts it
          localStorage.setItem("token", data.access_token);
          
          // Route them straight into their active dashboard workspace safely
          router.replace("/dashboard");
        }
      })
      .catch(() => {
        // Safe fallback: if no cookie exists, stay silently on the landing page
      });
  }, [pathname, router]);

  return null;
}
