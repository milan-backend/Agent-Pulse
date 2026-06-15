"use client";

import { useEffect, useState } from "react";
import { createCheckout, getCurrentPlan } from "@/components/api";
import { initializePaddle, Paddle } from "@paddle/paddle-js"; // Imports the new Paddle SDK engine
import { CreditCard, Rocket, Shield, Cpu, CheckCircle2, Sparkles } from "lucide-react";

const plansData = (isIndia: boolean) => [
  {
    name: "Free",
    price: isIndia ? "₹0" : "$0",
    description: "For solo runtime experimentation",
    features: [
      "Shared Community API Key Tier",
      "Auto-Prompt to add your own key on HTTP 429",
      "Bring Your Own API Key (BYOK) Ready",
      "Agent State Controls (Pause / Resume / Kill)",
      "Audit & Event History Logs Active",
      "1 Active AI Agent Capacity",
      "1 Concurrent Agent Execution Window",
      "10 Total Runtime Hours Limit",
      "Live WebSocket Dashboard Updates",
      "Standard Performance Analytics",
      "No RAG Knowledge Document Uploads"
    ],
    button: "Current Plan",
    disabled: true,
    glow: "from-slate-700/40 to-slate-900/40",
    border: "border-slate-700/40",
  },
  {
    name: "Pro",
    price: isIndia ? "₹2,499" : "$29",
    description: "Advanced runtime monitoring and guardrails built for growing developer teams",
    features: [
      "Bring Your Own API Key (BYOK) Native Integration",
      "Agent State Controls (Pause / Resume / Kill)",
      "Automated Budget Ceiling Guardrails",
      "State Loop & Infinite Execution Detection",
      "Multi-Workspace Partitioning Active",
      "Model Context Protocol (MCP Layer Access)",
      "RAG Documents Enabled (Up to 20 files)",
      "10 Active AI Agent Capacity",
      "5 Concurrent Agent Executions",
      "100 Total Runtime Hours Limit",
      "10 Team Member Seats Allocated",
      "Workspace Bulk Controls (Kill All / Resume All)",
      "Priority Asynchronous Execution Queues"
    ],
    button: "Upgrade to Pro",
    planKey: "pro",
    featured: true,
    glow: "from-cyan-500/20 to-blue-500/10",
    border: "border-cyan-400/30",
  },
  {
    name: "Enterprise",
    price: isIndia ? "₹16,999" : "$199",
    description: "Full scaling capacity and high-throughput logging for high-volume agent frameworks",
    features: [
      "Bring Your Own API Key (BYOK) Native Integration",
      "Agent State Controls (Pause / Resume / Kill)",
      "Automated Budget Ceiling Guardrails",
      "Enterprise Role-Based Access Control (RBAC)",
      "RAG Knowledge Documents (Up to 1,000 files)",
      "100 Active AI Agent Capacity",
      "100 Concurrent Agent Executions",
      "10,000 Total Runtime Hours Limit",
      "100 Team Member Seats Allocated",
      "Infinite Telemetry Audit Log History",
      "Workspace Bulk Controls (Kill All / Resume All)"
    ],
    button: "Upgrade to Enterprise",
    planKey: "enterprise",
    glow: "from-fuchsia-500/20 to-cyan-500/10",
    border: "border-fuchsia-400/30",
  }
];

export default function BillingPage() {
  const [currentPlan, setCurrentPlan] = useState("free");
  const [isIndia, setIsIndia] = useState(true);
  const [detectingRegion, setDetectingRegion] = useState(true);
  const [checkoutLoading, setCheckoutLoading] = useState(false);

  // 1. REGION LOCATION TARGET DETECTION DETECTOR
  useEffect(() => {
    const locateUserRegion = async () => {
      try {
        const response = await fetch("https://ip-api.com/json/");
        const data = await response.json();
        if (data && data.countryCode) {
          setIsIndia(data.countryCode === "IN");
        }
      } catch (err) {
        console.error("Geotargeting layer failed to reach endpoint nodes. Falling back to INR currency context:", err);
        setIsIndia(true);
      } finally {
        setDetectingRegion(false);
      }
    };
    locateUserRegion();
  }, []);

  // 2. INJECT RAZORPAY NATIVE JS WRAPPER CLIENT SCRIPT ONCE
  useEffect(() => {
    const script = document.createElement("script");
    script.src = "https://checkout.razorpay.com/v1/checkout.js";
    script.async = true;
    document.body.appendChild(script);

    return () => {
      if (document.body.contains(script)) {
        document.body.removeChild(script);
      }
    };
  }, []);

  // 3. FETCH ACCOUNT CURRENT PLAN STATUS OVERVIEW
  useEffect(() => {
    const loadPlan = async () => {
      try {
        const data = await getCurrentPlan();
        setCurrentPlan((data?.plan || "free").toLowerCase());
      } catch {
        setCurrentPlan("free");
      }
    };
    loadPlan();
  }, []);

  // 4. SECURED BILLING SYSTEM GATEWAY SWITCHBOARD EXECUTER
  const handleCheckout = async (planName: string) => {
    setCheckoutLoading(true);
    try {
      // Determine target payment provider infrastructure based on region
      const selectedGateway = isIndia ? "razorpay" : "paddle";

      const response = await createCheckout(planName, selectedGateway);

      // ============================================
      // EXECUTION PROFILE: PADDLE ROUTE (GLOBAL USD) [REPLACED GUMROAD]
      // ============================================
      if (selectedGateway === "paddle") {
        const paddleInstance: Paddle | undefined = await initializePaddle({
          environment: response.environment, // loads 'sandbox' securely from backend
          token: response.client_token       // matches your platform token signature string
        });

        if (!paddleInstance) {
          throw new Error("Unable to build frontend client-side Paddle.js framework context wrapper.");
        }

        // Open the native dark mode overlay frame box
        paddleInstance.Checkout.open({
          items: [
            {
              priceId: response.price_id, // maps directly to the Dashboard catalog tier ID string
              quantity: 1
            }
          ],
          customData: response.custom_data, // forwards your user workspace tracking credentials metadata securely
          settings: {
            displayMode: "overlay",
            theme: "dark",
            locale: "en"
          }
        });
        return;
      }

      // ============================================
      // EXECUTION PROFILE: RAZORPAY ROUTE (INDIA INR)
      // ============================================
      const options = {
        key: response.key_id,
        amount: response.amount,
        currency: response.currency,
        name: "Agent Pulse",
        description: `Upgrade to ${planName.toUpperCase()} Plan Tier`,
        order_id: response.order_id,
        handler: function (razorpayResponse: any) {
          if (razorpayResponse.razorpay_payment_id) {
            window.location.href = response.success_url;
          } else {
            window.location.href = response.cancel_url;
          }
        },
        modal: {
          ondismiss: function () {
            console.log("Payment wizard initialization box exited by user context.");
          }
        },
        theme: {
          color: "#22d3ee"
        }
      };

      const rzp = new (window as any).Razorpay(options);
      rzp.open();

    } catch (error) {
      console.error(error);
      alert("Checkout generation session crashed. Please retry the configuration process.");
    } finally {
      setCheckoutLoading(false);
    }
  };

  const dynamicPlans = plansData(isIndia);

  return (
    <div className="min-h-screen bg-[#020817] text-white overflow-hidden relative p-8">
      {/* Background Glow Accents */}
      <div className="absolute top-0 right-0 h-[500px] w-[500px] rounded-full bg-cyan-500/10 blur-3xl" />
      <div className="absolute bottom-0 left-0 h-[500px] w-[500px] rounded-full bg-fuchsia-500/10 blur-3xl" />

      <div className="relative z-10">
        {/* Hero Card Container */}
        <div className="rounded-[40px] border border-cyan-500/20 bg-[linear-gradient(180deg,#071120_0%,#091525_100%)] p-6 md:p-8 overflow-hidden relative mb-6">
          <div className="absolute top-0 right-0 h-96 w-96 rounded-full bg-cyan-500/10 blur-3xl" />
          <div className="relative z-10">
            <div className="flex items-center gap-5">
              <div className="h-16 w-16 rounded-2xl border border-cyan-500/20 bg-cyan-500/10 flex items-center justify-center">
                <CreditCard size={42} className="text-cyan-300" />
              </div>
              <div>
                <h1 className="text-4xl md:text-5xl font-black leading-none">AI Runtime Pricing</h1>
                <p className="mt-4 text-slate-400 text-base md:text-lg max-w-3xl">
                  Scale autonomous AI agents from solo experimentation to enterprise-grade runtime orchestration.
                  {detectingRegion ? " (Analyzing localized geolocation...)" : isIndia ? " 🇮🇳 Domestic INR Tier Active" : " 🌐 Global USD Tier Active"}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Current Active Plan Monitoring Card */}
        <div className="mb-8 rounded-[32px] border border-green-500/20 bg-[linear-gradient(180deg,#071120_0%,#091525_100%)] p-8">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-300 font-black uppercase tracking-wider">Your Current Plan</p>
              <h2 className="text-4xl font-black mt-2">{currentPlan.toUpperCase()}</h2>
            </div>
            <div className="px-5 py-3 rounded-full bg-green-500/10 border border-green-500/20 text-green-300 font-black">
              ACTIVE
            </div>
          </div>
        </div>

        {/* Three Plan Matrix Array Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
          {dynamicPlans.map((plan) => (
            <div
              key={plan.name}
              className={`relative rounded-[36px] border ${plan.border} bg-[linear-gradient(180deg,#0b1220_0%,#091525_100%)] p-10 overflow-hidden backdrop-blur-xl transition-all hover:scale-[1.02] hover:shadow-[0_0_60px_rgba(34,211,238,0.12)] ${
                plan.featured ? "scale-[1.03] shadow-[0_0_60px_rgba(34,211,238,0.18)]" : ""
              }`}
            >
              <div className={`absolute inset-0 bg-gradient-to-br ${plan.glow} opacity-40`} />

              <div className="relative z-10">
                {plan.featured && (
                  <div className="inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-500/10 px-4 py-2 mb-6">
                    <Sparkles size={16} className="text-cyan-300" />
                    <span className="text-sm font-black text-cyan-300">MOST POPULAR</span>
                  </div>
                )}

                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-4xl font-black">{plan.name}</h2>
                  <div className="h-14 w-14 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center">
                    {plan.name === "Enterprise" ? (
                      <Shield className="text-fuchsia-300" />
                    ) : plan.name === "Pro" ? (
                      <Rocket className="text-cyan-300" />
                    ) : (
                      <Cpu className="text-slate-300" />
                    )}
                  </div>
                </div>

                <div className="mb-8">
                  <div className="flex items-end gap-2">
                    <span className="text-6xl font-black">{plan.price}</span>
                    <span className="text-slate-400 mb-2">/month</span>
                  </div>
                  <p className="mt-3 text-slate-400 text-sm">{plan.description}</p>
                </div>

                <div className="space-y-4 mb-10">
                  {plan.features.map((feature) => (
                    <div key={feature} className="flex items-center gap-3">
                      <CheckCircle2 size={18} className="text-cyan-300 shrink-0" />
                      <span className="text-slate-200 text-sm">{feature}</span>
                    </div>
                  ))}
                </div>

                <button
                  disabled={currentPlan === plan.name.toLowerCase() || checkoutLoading}
                  onClick={() => plan.planKey && handleCheckout(plan.planKey)}
                  className={`w-full py-4 rounded-2xl font-black text-lg transition-all ${
                    currentPlan === plan.name.toLowerCase()
                      ? "bg-green-600 text-white cursor-not-allowed"
                      : "bg-cyan-400 text-black hover:scale-[1.02] hover:shadow-[0_0_30px_rgba(34,211,238,0.4)]"
                  } ${checkoutLoading ? "opacity-50 cursor-wait" : ""}`}
                >
                  {currentPlan === plan.name.toLowerCase()
                    ? "Current Plan"
                    : checkoutLoading
                    ? "Processing..."
                    : plan.button}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}