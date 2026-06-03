"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { API_URL } from "./api"; // Importing your centralized backend URL variable

export default function AuthBootstrap() {
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (pathname !== "/") return;

    // We use a clean fetch call pointing directly to your API_URL
    // This completely bypasses the api.ts request interceptor, preventing the logout() trigger
    fetch(`${API_URL}/auth/refresh`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include", // Securely passes your HttpOnly token cookies
    })
      .then((res) => {
        if (res.ok) return res.json();
        throw new Error("No active session");
      })
      .then((data) => {
        if (data?.access_token) {
          // Store the fresh token exactly where your api.ts looks for it
          localStorage.setItem("token", data.access_token);
          
          // Smoothly route them inside
          router.replace("/dashboard");
        }
      })
      .catch(() => {
        // If they don't have a cookie, it catches silently here!
        // No logout() gets fired, so they safely stay on your beautiful landing page.
      });
  }, [pathname, router]);

  return null;
}
