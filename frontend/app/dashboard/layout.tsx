"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  LayoutDashboard,
  BarChart3,
  Rocket,
  ScrollText,
  Users,
  Settings,
  Bot,
  Activity,
  LogOut,
  CreditCard,
  Shield,
  MessageSquareCode,
} from "lucide-react";
import { useEffect, useState } from "react";
import { logout as secureServerLogout, getWorkspaceMembers, getCurrentUser } from "@/components/api"; 

const navItems = [
  {
    label: "Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard,
    allowedRoles: ["admin", "operator", "viewer"], // 🔓 Public
  },
  {
    label: "Analytics",
    href: "/dashboard/analytics",
    icon: BarChart3,
    allowedRoles: ["admin", "operator", "viewer"], // 🔓 Public
  },
  {
    label: "Missions",
    href: "/dashboard/missions",
    icon: Rocket,
    allowedRoles: ["admin", "operator", "viewer"], // 🔓 Public
  },
  {
    label: "Agents",
    href: "/dashboard/agents",
    icon: Bot,
    allowedRoles: ["admin", "operator", "viewer"], // 🔓 Public
  },
  {
    label: "AP Copilot",
    href: "/dashboard/copilot",
    icon: MessageSquareCode,
    allowedRoles: ["admin", "operator", "viewer"], // 🔓 Public
  },
  {
    label: "Usage Logs",
    href: "/dashboard/usage-logs",
    icon: ScrollText,
    allowedRoles: ["admin", "operator", "viewer"], // 🔓 Public
  },
  {
    label: "Audit Trails",
    href: "/dashboard/audit",
    icon: Shield, // Reusing your premium Lucide Shield icon block layout!
    allowedRoles: ["admin", "operator"], // 🔒 Admin and Operator only. Viewer is excluded!
  },
  {
    label: "Billing",
    href: "/dashboard/billing",
    icon: CreditCard,
    allowedRoles: ["admin"], // 🔒 Admin Only
  },
  {
    label: "My Plan",
    href: "/dashboard/my-plan",
    icon: Shield,
    allowedRoles: ["admin"], // 🔒 Admin Only
  },
  {
    label: "Workspace",
    href: "/dashboard/workspace",
    icon: Users,
    allowedRoles: ["admin"], // 🔒 Admin Only
  },
  {
    label: "Settings",
    href: "/dashboard/settings",
    icon: Settings,
    allowedRoles: ["admin"], // 🔒 Admin Only
  },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  
  // State to hold the current user's role context dynamically
  const [userRole, setUserRole] = useState<string>("viewer");

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }

    // ⚡ Fetch dynamic roster context to accurately find the current user's role
    async function determineUserRole() {
      try {
        const [me, membersList] = await Promise.all([
          getCurrentUser(),
          getWorkspaceMembers()
        ]);
        
        if (me && membersList) {
          const match = membersList.find(
            (m: any) => m.user_email === me.email || m.email === me.email
          );
          if (match?.role) {
            setUserRole(match.role.toLowerCase());
          }
        }
      } catch (err) {
        console.error("DashboardLayout: Error syncing user clearance metrics:", err);
      }
    }

    determineUserRole();
  }, [router]);

  function handleLogoutExecution() {
    console.log("DashboardLayout: Dispatching atomic log out request sequence...");
    secureServerLogout();
  }

  // 🎯 FILTER LINKS: Only return items where allowedRoles includes the current user's role
  const filteredNavItems = navItems.filter((item) =>
    item.allowedRoles.includes(userRole)
  );

  return (
    <div className="min-h-screen bg-[#020817] text-white flex overflow-hidden">
      {/* SIDEBAR */}
      <aside className="w-[310px] shrink-0 border-r border-cyan-500/10 bg-[#040b18] flex flex-col justify-between p-6 overflow-y-auto">
        <div>
          {/* BRAND */}
          <div className="flex items-center gap-4 mb-10">
            <div className="h-16 w-16 rounded-3xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center shrink-0">
              <Activity size={32} className="text-cyan-300" />
            </div>

            <div className="min-w-0">
              <h1 className="text-4xl font-black leading-none break-words">
                <span className="text-cyan-400">Agent</span>
                <span className="text-white">Pulse</span>
              </h1>
              <p className="text-slate-400 text-sm mt-2">AI Runtime Platform</p>
            </div>
          </div>

          {/* NAVIGATION */}
          <nav className="space-y-4">
            {filteredNavItems.map((item) => {
              const Icon = item.icon;
              const active = pathname === item.href;
              const isCopilotItem = item.href === "/dashboard/copilot";

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`group flex items-center gap-4 rounded-[24px] px-5 py-5 transition-all border ${
                    active
                      ? "border-cyan-400/30 bg-cyan-500/15 shadow-[0_0_25px_rgba(34,211,238,0.15)]"
                      : isCopilotItem 
                        ? "border-cyan-500/10 bg-cyan-950/10 hover:bg-cyan-900/15"
                        : "border-white/5 bg-white/[0.03] hover:bg-white/[0.06]"
                  }`}
                >
                  <div
                    className={`h-12 w-12 rounded-2xl flex items-center justify-center transition-all ${
                      active
                        ? "bg-cyan-500/20 text-cyan-300"
                        : isCopilotItem
                          ? "bg-cyan-950/40 text-cyan-400 group-hover:text-cyan-300"
                          : "bg-white/[0.03] text-slate-400 group-hover:text-white"
                    }`}
                  >
                    <Icon size={24} />
                  </div>
                  <span className={`text-lg font-bold ${
                    active 
                      ? "text-white" 
                      : isCopilotItem 
                        ? "text-cyan-400/90 group-hover:text-cyan-300" 
                        : "text-slate-300"
                  }`}>
                    {item.label}
                  </span>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* FOOTER */}
        <div className="space-y-5 pt-8">
          {/* SYSTEM HEALTH */}
          <div className="rounded-[28px] border border-cyan-500/15 bg-[linear-gradient(180deg,#071120_0%,#091525_100%)] p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-xl font-black">System Health</h3>
                <p className="text-slate-400 text-sm mt-1">Runtime telemetry</p>
              </div>
              <div className="flex items-center gap-2 rounded-full border border-green-500/20 bg-green-500/10 px-3 py-2">
                <div className="h-2 w-2 rounded-full bg-green-400 animate-pulse" />
                <span className="text-xs font-bold text-green-300">LIVE</span>
              </div>
            </div>

            <div className="space-y-4">
              <div className="rounded-2xl bg-black/20 px-4 py-3 flex items-center justify-between">
                <span className="text-slate-400">WebSocket</span>
                <span className="text-green-300 font-bold">Connected</span>
              </div>
              <div className="rounded-2xl bg-black/20 px-4 py-3 flex items-center justify-between">
                <span className="text-slate-400">Runtime</span>
                <span className="text-cyan-300 font-bold">Operational</span>
              </div>
              <div className="rounded-2xl bg-black/20 px-4 py-3 flex items-center justify-between">
                <span className="text-slate-400">API</span>
                <span className="text-green-300 font-bold">Healthy</span>
              </div>
            </div>
          </div>

          {/* LOGOUT BUTTON */}
          <button
            onClick={handleLogoutExecution}
            className="w-full rounded-[24px] border border-red-500/20 bg-red-500/10 px-5 py-5 flex items-center justify-center gap-4 font-black text-red-300 hover:bg-red-500/20 transition-all"
          >
            <LogOut size={22} />
            Logout
          </button>
        </div>
      </aside>

      {/* MAIN VIEWPORT */}
      <div className="flex-1 overflow-y-auto">
        <main className="p-8">{children}</main>
      </div>
    </div>
  );
}