"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { API_URL } from "./api"; 

export default function AuthBootstrap() {
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (pathname !== "/") return;

    // 💡 BULLETPROOF FIX: Check the URL address bar parameters instantly
    if (typeof window !== "undefined") {
      const urlParams = new URLSearchParams(window.location.search);
      if (urlParams.get("logout") === "true") {
        console.log("AuthBootstrap: URL flag blocks cookie execution. Staying logged out safely.");
        return;
      }
    }

    // 1. If a valid token is present in local storage, they are logged in! 
    const token = localStorage.getItem("token");
    if (token) {
      router.replace("/dashboard");
      return;
    }

    // 2. Fallback check: Read persistent backend cookie layers safely
    fetch(`${API_URL}/auth/refresh`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include", 
    })
      .then((res) => {
        if (res.ok) return res.json();
        throw new Error("No secure cookie session found.");
      })
      .then((data) => {
        if (data?.access_token) {
          localStorage.setItem("token", data.access_token);
          router.replace("/dashboard");
        }
      })
      .catch(() => {
        // Safe Catch: If no cookie exists, stay cleanly on landing page
      });
  }, [pathname, router]);

  return null;
}