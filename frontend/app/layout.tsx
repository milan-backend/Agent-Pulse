// frontend/app/layout.tsx

import { Analytics } from "@vercel/analytics/react";

import type { Metadata } from "next";

import "./globals.css";

import { Toaster } from "sonner";

export const metadata: Metadata = {

  title:
    "AgentPulse | AI Runtime Observability",

  description:
    "Autonomous AI runtime observability and mission telemetry platform.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {

  return (

    <html lang="en">

      <body
        className="
          bg-[#020817]
          text-white
          antialiased
        "
      >

        {children}

        <Toaster
          position="top-right"
          richColors
          theme="dark"
        />
        <Analytics />
      </body>

    </html>
  );
}