"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";

// Importing the request function or custom route calls isn't even needed! 
// Since your api.ts already has a built-in auto-refresh token interceptor loop,
// we just need to hit a protected endpoint like getCurrentUser to trigger a refresh.
import { getCurrentUser } from "./api"; 

export default function AuthBootstrap() {
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (pathname !== "/") return;

    // Call your existing auth verification function. 
    // If a secure cookie exists, your api.ts interceptor handles everything seamlessly!
    getCurrentUser()
      .then((user) => {
        if (user) {
          // If the handshake is successful, send them straight into the dashboard
          router.replace("/dashboard");
        }
      })
      .catch(() => {
        // Silently swallow errors if no cookie exists, leaving them on the landing page safely
      });
  }, [pathname, router]);

  return null;
}
