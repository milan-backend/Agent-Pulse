// frontend/app/layout.tsx

import type { Metadata } from "next";

import "./globals.css";

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
      </body>

    </html>
  );
}