"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import axios from "axios";
import "./globals.css"; // Keeps your global tailwind styles intact

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const [checkingAuth, setCheckingAuth] = useState(true);

  useEffect(() => {
    // We only perform the silent handshake if the user is visiting the home landing route "/"
    if (pathname === "/") {
      axios.post(
        "https://agentpulse-backend.onrender.com/auth/refresh",
        {},
        { withCredentials: true } // Crucial: Safely passes HttpOnly cookies to your Render backend
      )
      .then((response: any) => {
        if (response.data && response.data.access_token) {
          // Store token in local memory
          localStorage.setItem("access_token", response.data.access_token);
          // Redirect the user seamlessly straight to their secure dashboard workspace
          router.push("/dashboard");
        } else {
          setCheckingAuth(false);
        }
      })
      .catch(() => {
        // If no active secure cookie session exists, render the home page smoothly
        setCheckingAuth(false);
      });
    } else {
      setCheckingAuth(false);
    }
  }, [pathname, router]);

  // Shows a clean, dark theme-matched runtime synchronization screen while checking cookies
  if (checkingAuth && pathname === "/") {
    return (
      <html lang="en">
        <body className="bg-black flex flex-col items-center justify-center min-h-screen text-cyan-400 font-mono gap-3">
          <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-sm tracking-widest animate-pulse">SYNCHRONIZING SECURE RUNTIME...</p>
        </body>
      </html>
    );
  }

  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}

