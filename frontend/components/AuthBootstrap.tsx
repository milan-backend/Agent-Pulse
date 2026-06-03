"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import axios from "axios";

export default function AuthBootstrap() {
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    // Only run the token check if the user is explicitly sitting on the landing root page
    if (pathname !== "/") return;

    axios
      .post(
        "https://agentpulse-backend.onrender.com/auth/refresh",
        {},
        {
          withCredentials: true, // Crucial: Ensures cookies travel safely to Render
        }
      )
      .then((response: any) => {
        if (response.data?.access_token) {
          // Store the short-lived token in local runtime memory
          localStorage.setItem("access_token", response.data.access_token);
          
          // Using router.replace prevents the user from clicking the browser "Back" button into an infinite loop
          router.replace("/dashboard");
        }
      })
      .catch(() => {
        // Silently catch errors if no active session cookie exists (user stays on landing page)
      });
  }, [pathname, router]);

  return null;
}
