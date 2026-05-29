"use client";

import { useEffect, useState } from "react";
import { getCurrentPlan } from "@/components/api";
import {
  Shield,
  Rocket,
  Cpu,
  CheckCircle2,
} from "lucide-react";

export default function MyPlanPage() {
  const [planData, setPlanData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPlan();
  }, []);

  async function loadPlan() {
    try {
      const data = await getCurrentPlan();
      setPlanData(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="p-8 text-white">
        Loading plan...
      </div>
    );
  }

  const planName =
    planData?.plan?.toUpperCase() || "FREE";

  return (
    <div className="min-h-screen bg-[#020817] text-white p-8">

      <div className="max-w-6xl mx-auto">

        <div className="rounded-3xl border border-cyan-500/20 bg-[#091525] p-8 mb-8">

          <div className="flex items-center gap-4">

            <div className="h-16 w-16 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center">

              {planName === "ENTERPRISE" ? (
                <Shield className="text-fuchsia-300" size={32} />
              ) : planName === "PRO" ? (
                <Rocket className="text-cyan-300" size={32} />
              ) : (
                <Cpu className="text-slate-300" size={32} />
              )}

            </div>

            <div>

              <p className="text-slate-400 text-sm">
                YOUR CURRENT PLAN
              </p>

              <h1 className="text-5xl font-black">
                {planName}
              </h1>

              <p className="text-green-400 mt-2">
                {planData?.status?.toUpperCase()}
              </p>

            </div>

          </div>

        </div>

        <div className="grid lg:grid-cols-2 gap-8">

          {/* LIMITS */}

          <div className="rounded-3xl border border-cyan-500/20 bg-[#091525] p-8">

            <h2 className="text-2xl font-black mb-6">
              Plan Limits
            </h2>

            <div className="space-y-4">

              {Object.entries(
                planData?.limits || {}
              ).map(([key, value]) => (
                <div
                  key={key}
                  className="flex justify-between border-b border-slate-800 pb-3"
                >
                  <span className="text-slate-400">
                    {key.replaceAll("_", " ")}
                  </span>

                  <span className="font-bold">
                    {String(value)}
                  </span>
                </div>
              ))}

            </div>

          </div>

          {/* FEATURES */}

          <div className="rounded-3xl border border-cyan-500/20 bg-[#091525] p-8">

            <h2 className="text-2xl font-black mb-6">
              Enabled Features
            </h2>

            <div className="space-y-3">

              {Object.entries(
                planData?.features || {}
              )
                .filter(
                  ([, value]) => value === true
                )
                .map(([key]) => (
                  <div
                    key={key}
                    className="flex items-center gap-3"
                  >
                    <CheckCircle2
                      size={18}
                      className="text-cyan-300"
                    />

                    <span>
                      {key.replaceAll("_", " ")}
                    </span>
                  </div>
                ))}

            </div>

          </div>

        </div>
      </div>
    </div>
  );
}