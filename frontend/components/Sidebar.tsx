// frontend/components/Sidebar.tsx

"use client";

import Link from "next/link";

import {
  usePathname,
  useRouter,
} from "next/navigation";

import {
  LayoutDashboard,
  BarChart3,
  Rocket,
  ScrollText,
  Users,
  Settings,
  Bot,
  Activity,
  ShieldCheck,
  LogOut,
} from "lucide-react";

const navItems = [
  {
    label: "Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard,
  },

  {
    label: "Analytics",
    href: "/dashboard/analytics",
    icon: BarChart3,
  },

  {
    label: "Missions",
    href: "/dashboard/missions",
    icon: Rocket,
  },

  {
    label: "Agents",
    href: "/dashboard/agents",
    icon: Bot,
  },

  {
    label: "Usage Logs",
    href: "/dashboard/usage-logs",
    icon: ScrollText,
  },

  {
    label: "Workspace",
    href: "/dashboard/workspace",
    icon: Users,
  },

  {
    label: "Settings",
    href: "/dashboard/settings",
    icon: Settings,
  },
];

export default function Sidebar() {

  const pathname =
    usePathname();

  const router =
    useRouter();

  function logout() {

    localStorage.removeItem(
      "token"
    );

    router.push("/login");
  }

  return (

    <aside
      className="
        hidden
        lg:flex
        w-[310px]
        shrink-0
        flex-col
        justify-between
        border-r
        border-cyan-500/10
        bg-[#040b18]
        p-6
        overflow-y-auto
      "
    >
      {/* TOP */}

      <div>

        {/* BRAND */}

        <div
          className="
            flex
            items-center
            gap-4
            mb-10
          "
        >
          <div
            className="
              h-16
              w-16
              rounded-3xl
              border
              border-cyan-500/20
              bg-cyan-500/10
              flex
              items-center
              justify-center
              shrink-0
            "
          >
            <Activity
              size={32}
              className="
                text-cyan-300
              "
            />
          </div>

          <div className="min-w-0">

            <h1
              className="
                text-4xl
                font-black
                leading-none
                break-words
              "
            >
              <span className="text-cyan-400">
                Agent
              </span>

              <span className="text-white">
                Pulse
              </span>
            </h1>

            <p
              className="
                mt-2
                text-sm
                text-slate-400
              "
            >
              AI Runtime Platform
            </p>
          </div>
        </div>

        {/* NAVIGATION */}

        <nav className="space-y-4">

          {navItems.map(
            (item) => {

              const Icon =
                item.icon;

              const active =
                pathname ===
                item.href;

              return (

                <Link
                  key={item.href}
                  href={item.href}
                  className={`
                    group
                    flex
                    items-center
                    gap-4
                    rounded-[24px]
                    border
                    px-5
                    py-5
                    transition-all
                    ${
                      active
                        ? `
                          border-cyan-400/30
                          bg-cyan-500/15
                          shadow-[0_0_25px_rgba(34,211,238,0.15)]
                        `
                        : `
                          border-white/5
                          bg-white/[0.03]
                          hover:bg-white/[0.06]
                        `
                    }
                  `}
                >
                  <div
                    className={`
                      h-12
                      w-12
                      rounded-2xl
                      flex
                      items-center
                      justify-center
                      transition-all
                      ${
                        active
                          ? `
                            bg-cyan-500/20
                            text-cyan-300
                          `
                          : `
                            bg-white/[0.03]
                            text-slate-400
                            group-hover:text-white
                          `
                      }
                    `}
                  >
                    <Icon size={24} />
                  </div>

                  <span
                    className={`
                      text-lg
                      font-bold
                      ${
                        active
                          ? "text-white"
                          : "text-slate-300"
                      }
                    `}
                  >
                    {item.label}
                  </span>
                </Link>
              );
            }
          )}
        </nav>
      </div>

      {/* BOTTOM */}

      <div className="space-y-5">

        {/* HEALTH */}

        <div
          className="
            rounded-[28px]
            border
            border-cyan-500/15
            bg-[linear-gradient(180deg,#071120_0%,#091525_100%)]
            p-6
          "
        >
          <div
            className="
              flex
              items-center
              justify-between
              mb-6
            "
          >
            <div>

              <h3
                className="
                  text-xl
                  font-black
                "
              >
                System Health
              </h3>

              <p
                className="
                  mt-1
                  text-sm
                  text-slate-400
                "
              >
                Runtime telemetry
              </p>
            </div>

            <div
              className="
                flex
                items-center
                gap-2
                rounded-full
                border
                border-green-500/20
                bg-green-500/10
                px-3
                py-2
              "
            >
              <div
                className="
                  h-2
                  w-2
                  rounded-full
                  bg-green-400
                  animate-pulse
                "
              />

              <span
                className="
                  text-xs
                  font-bold
                  text-green-300
                "
              >
                LIVE
              </span>
            </div>
          </div>

          <div className="space-y-4">

            <div
              className="
                rounded-2xl
                bg-black/20
                px-4
                py-3
                flex
                items-center
                justify-between
              "
            >
              <span className="text-slate-400">
                WebSocket
              </span>

              <span className="font-bold text-green-300">
                Connected
              </span>
            </div>

            <div
              className="
                rounded-2xl
                bg-black/20
                px-4
                py-3
                flex
                items-center
                justify-between
              "
            >
              <span className="text-slate-400">
                Runtime
              </span>

              <span className="font-bold text-cyan-300">
                Operational
              </span>
            </div>

            <div
              className="
                rounded-2xl
                bg-black/20
                px-4
                py-3
                flex
                items-center
                justify-between
              "
            >
              <span className="text-slate-400">
                Security
              </span>

              <div
                className="
                  flex
                  items-center
                  gap-2
                "
              >
                <ShieldCheck
                  size={16}
                  className="
                    text-green-300
                  "
                />

                <span className="font-bold text-green-300">
                  Protected
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* LOGOUT */}

        <button
          onClick={logout}
          className="
            w-full
            rounded-[24px]
            border
            border-red-500/20
            bg-red-500/10
            px-5
            py-5
            flex
            items-center
            justify-center
            gap-4
            text-red-300
            font-black
            hover:bg-red-500/20
            transition-all
          "
        >
          <LogOut size={22} />

          Logout
        </button>
      </div>
    </aside>
  );
}